import uuid
import boto3

class SQSService:
    def __init__(self, region_name: str, queue_url: str, default_group_id: str, content_based_dedup: bool):
        self.queue_url = queue_url
        self.default_group_id = default_group_id
        self.content_based_dedup = content_based_dedup
        self.client = boto3.client("sqs", region_name=region_name)

    def send_message(self, body: str, group_id: str | None = None, dedup_id: str | None = None):
        if not self.queue_url:
            raise ValueError("SQS_QUEUE_URL no está configurado")

        params = {
            "QueueUrl": self.queue_url,
            "MessageBody": body,
            "MessageGroupId": group_id or self.default_group_id,  # obligatorio en FIFO
        }

        # Si NO hay deduplicación por contenido, enviamos un ID único
        if not self.content_based_dedup:
            params["MessageDeduplicationId"] = dedup_id or str(uuid.uuid4())

        return self.client.send_message(**params)