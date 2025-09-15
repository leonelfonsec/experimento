import uuid
import boto3
import json

class SQSService:
    def __init__(self, region_name: str, queue_url: str, default_group_id: str = "grupo1", content_based_dedup: bool = True, endpoint_url: str = None):
        self.queue_url = queue_url
        self.default_group_id = default_group_id
        self.content_based_dedup = content_based_dedup
        # aqui agregamos endpoint_url
        self.client = boto3.client("sqs", region_name=region_name, endpoint_url=endpoint_url)

    def send_message(self, body: str, group_id: str | None = None, dedup_id: str | None = None):
        if not self.queue_url:
            raise ValueError("SQS_QUEUE_URL no está configurado")
        body_str = json.dumps(body, ensure_ascii=False)

        params = {
            "QueueUrl": self.queue_url,
            "MessageBody": body_str,
            "MessageGroupId": group_id or self.default_group_id,
        }

        if not self.content_based_dedup:
            params["MessageDeduplicationId"] = dedup_id or str(uuid.uuid4())

        return self.client.send_message(**params)