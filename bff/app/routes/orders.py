from flask import Blueprint, request, jsonify, current_app
import uuid

bp = Blueprint("orders", __name__)

@bp.post("/api/v1/orders")
def post_message():
    data = request.get_json(silent=True) or {}
    body = data.get("body")
    if not body:
        return jsonify(error="Falta 'body' en el JSON"), 400
    
    event_id = str(uuid.uuid4())
    sqs_message = {
        "event_id": event_id,
        "order": body  # El body que envió el usuario
    }

    group_id = data.get("group_id")          # opcional, por defecto el de config
    dedup_id = data.get("dedup_id", event_id)  # usa event_id como dedup_id por defecto

    sqs: "SQSService" = current_app.extensions["sqs"]
    resp = sqs.send_message(body=sqs_message, group_id=group_id, dedup_id=dedup_id)

    return jsonify(messageId=resp["MessageId"], event_id=event_id), 201