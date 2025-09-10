from flask import Blueprint, request, jsonify, current_app

bp = Blueprint("messages", __name__)

@bp.post("/messages")
def post_message():
    data = request.get_json(silent=True) or {}
    body = data.get("body")
    if not body:
        return jsonify(error="Falta 'body' en el JSON"), 400

    group_id = data.get("group_id")          # opcional, por defecto el de config
    dedup_id = data.get("dedup_id")          # opcional si usas CONTENT_BASED_DEDUP

    sqs: "SQSService" = current_app.extensions["sqs"]
    resp = sqs.send_message(body=body, group_id=group_id, dedup_id=dedup_id)

    return jsonify(messageId=resp["MessageId"]), 201
