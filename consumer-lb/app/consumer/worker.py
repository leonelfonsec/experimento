import os, json, time
import boto3
import httpx
from botocore.exceptions import BotoCoreError, ClientError

# === ENV ===
REGION = os.getenv("AWS_REGION", "us-east-1")
QUEUE_URL = os.getenv("SQS_QUEUE_URL")  # p.ej. http://localstack:4566/000000000000/orders.fifo
SQS_ENDPOINT = os.getenv("SQS_ENDPOINT")  # p.ej. http://localstack:4566 (vacío en AWS real)
BATCH = int(os.getenv("SQS_BATCH", "10"))           # <= 10
WAIT = int(os.getenv("SQS_WAIT", "20"))             # long polling
VISIBILITY = int(os.getenv("SQS_VISIBILITY", "60")) # > tiempo de proceso
LB_TARGET_URL = os.getenv("LB_TARGET_URL", "http://localhost:8080/orders")  # URL completa (con path)
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "30"))

if not QUEUE_URL:
    raise SystemExit("Falta SQS_QUEUE_URL")

sqs = boto3.client("sqs", region_name=REGION, endpoint_url=SQS_ENDPOINT)
client = httpx.Client(timeout=HTTP_TIMEOUT)

def deliver_to_orders(payload: dict) -> None:
    # Sin afinidad: NO enviamos headers especiales; HAProxy hará round-robin.
    r = client.post(LB_TARGET_URL, json=payload)
    r.raise_for_status()

def handle_message(m: dict) -> bool:
    body = json.loads(m["Body"])
    # Retries básicos de red/HTTP
    for attempt in range(2):
        try:
            deliver_to_orders(body)
            return True  # OK → borrar mensaje
        except httpx.HTTPError as e:
            # 5xx/timeout → reintentar una vez
            if attempt == 0:
                time.sleep(1.0)
                continue
            print("HTTP error:", e)
            return False
        except Exception as e:
            print("Unexpected error:", e)
            return False

def main():
    while True:
        try:
            resp = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=BATCH,
                WaitTimeSeconds=WAIT,
                VisibilityTimeout=VISIBILITY,
                MessageAttributeNames=["All"],
                AttributeNames=["All"],
            )
        except (BotoCoreError, ClientError) as e:
            print("SQS receive error:", e)
            time.sleep(2.0)
            continue

        msgs = resp.get("Messages", [])
        if not msgs:
            continue

        to_delete = []
        for m in msgs:
            ok = False
            try:
                ok = handle_message(m)
            except Exception as e:
                print("handle_message error:", e)
            if ok:
                to_delete.append({"Id": m["MessageId"], "ReceiptHandle": m["ReceiptHandle"]})

        if to_delete:
            try:
                sqs.delete_message_batch(QueueUrl=QUEUE_URL, Entries=to_delete)
            except (BotoCoreError, ClientError) as e:
                print("SQS delete error:", e)

if __name__ == "__main__":
    main()
