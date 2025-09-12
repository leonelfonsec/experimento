﻿from fastapi import FastAPI, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session, Base, engine 
from app.models import IdempotencyRequest, IdemStatus, Order, OutboxEvent
from app.schemas import CreateOrderRequest, AcceptedResponse
from app.tasks import celery
from uuid import uuid4

app = FastAPI(title="Orders Service")

def _sha256(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def get_idempotency_key(
    idem: str | None = Header(
        default=None,
        alias="Idempotency-Key",      
        convert_underscores=False,
        description="UUID v4 para idempotencia (si lo dejas vacío, el server genera uno)",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
) -> str:
    return idem or str(uuid4())

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/orders", response_model=AcceptedResponse, status_code=202)
async def create_order(
    body: CreateOrderRequest,
    Idempotency_Key: str = Depends(get_idempotency_key),
    session: AsyncSession = Depends(get_session),   
):
    key_hash = _sha256(Idempotency_Key)
    body_hash = _sha256(body.model_dump_json())

    async with session.begin():                     
        idem = await session.get(IdempotencyRequest, key_hash)
        if idem:
            if idem.body_hash != body_hash:
                raise HTTPException(status_code=409, detail="Idempotency-Key ya usada con payload distinto")
            if idem.status == IdemStatus.DONE and idem.response_body:
                return AcceptedResponse(request_id=key_hash, message="Ya procesado (idempotente)")
        else:
            idem = IdempotencyRequest(key_hash=key_hash, body_hash=body_hash, status=IdemStatus.PENDING)
            session.add(idem)

        order = Order(customer_id=body.customer_id, items=[i.model_dump() for i in body.items])
        session.add(order)
        await session.flush()

        evt = OutboxEvent(
            aggregate_id=order.id,
            type="OrderCreated",
            payload={"order_id": str(order.id), "key_hash": key_hash},
        )
        session.add(evt)

    # fuera de la transacción
    celery.send_task("process_outbox_event", args=[str(evt.event_id)])
    return AcceptedResponse(request_id=key_hash)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
