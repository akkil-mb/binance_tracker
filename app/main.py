import asyncio
import json
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.database import SessionLocal
from app.models.models import CryptoCurrency, CryptoTracker
from app.service.crypto_service import binance_ticker_stream

logger = structlog.get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: list[dict]):
        message = json.dumps(data, default=str)
        for ws in list(self.active):
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect(ws)


manager = ConnectionManager()


async def price_updater():
    """Background task: consume Binance WS stream, update DB, broadcast to clients."""
    async for tick in binance_ticker_stream():
        try:
            db = SessionLocal()
            try:
                currency = db.query(CryptoCurrency).filter_by(symbol=tick["symbol"]).first()
                if not currency:
                    db.add(CryptoCurrency(symbol=tick["symbol"], name=tick["name"]))
                    db.flush()

                tracker = db.query(CryptoTracker).filter_by(symbol=tick["symbol"]).first()
                if tracker:
                    tracker.last_price = tick["last_price"]
                    tracker.one_day_change = tick["24_hour_change_percent"]
                    tracker.timestamp = tick["timestamp"]
                else:
                    db.add(CryptoTracker(
                        symbol=tick["symbol"],
                        last_price=tick["last_price"],
                        one_day_change=tick["24_hour_change_percent"],
                        timestamp=tick["timestamp"],
                    ))
                db.commit()
            finally:
                db.close()

            await manager.broadcast([{
                "symbol": tick["symbol"],
                "name": tick["name"],
                "last_price": tick["last_price"],
                "24_hour_change_percent": tick["24_hour_change_percent"],
                "timestamp": tick["timestamp"].isoformat(),
            }])
            logger.info("tick_broadcast", symbol=tick["symbol"], price=tick["last_price"])
        except Exception as e:
            logger.error("price_updater_error", error=str(e))


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(price_updater())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/price")
def get_prices():
    db = SessionLocal()
    try:
        records = db.query(CryptoTracker).all()
        return [
            {
                "symbol": r.symbol,
                "last_price": str(r.last_price),
                "24_hour_change_percent": str(r.one_day_change),
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in records
        ]
    finally:
        db.close()


@app.websocket("/ws/crypto")
async def websocket_crypto(ws: WebSocket):
    await manager.connect(ws)
    logger.info("ws_client_connected", total=len(manager.active))

    db = SessionLocal()
    try:
        records = db.query(CryptoTracker).all()
        snapshot = [
            {
                "symbol": r.symbol,
                "last_price": r.last_price,
                "24_hour_change_percent": r.one_day_change,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in records
        ]
    finally:
        db.close()

    await ws.send_text(json.dumps(snapshot, default=str))

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
        logger.info("ws_client_disconnected", total=len(manager.active))
