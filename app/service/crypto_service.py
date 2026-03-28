import json
from decimal import Decimal
from datetime import datetime, timezone
from typing import AsyncGenerator
import websockets
import structlog

logger = structlog.get_logger(__name__)

# Add or remove symbols here
TRACKED_SYMBOLS: dict[str, str] = {
    "BTCUSDT": "Bitcoin",
    "ETHUSDT": "Ethereum",
    "BNBUSDT": "BNB",
}

_streams = "/".join(f"{s.lower()}@ticker" for s in TRACKED_SYMBOLS)
BINANCE_WS_URL = f"wss://stream.binance.com:9443/stream?streams={_streams}"


async def binance_ticker_stream() -> AsyncGenerator[dict, None]:
    """
    Connects to Binance combined WebSocket and yields parsed ticker updates.
    Reconnects automatically on disconnect.
    """
    while True:
        try:
            logger.info("binance_ws_connecting", url=BINANCE_WS_URL)
            async with websockets.connect(BINANCE_WS_URL) as ws:
                logger.info("binance_ws_connected")
                async for raw in ws:
                    envelope = json.loads(raw)
                    data = envelope["data"]
                    symbol = data["s"]
                    yield {
                        "name": TRACKED_SYMBOLS.get(symbol, symbol),
                        "symbol": symbol,
                        "last_price": Decimal(data["c"]),
                        "24_hour_change_percent": Decimal(data["P"]),
                        "timestamp": datetime.fromtimestamp(data["E"] / 1000, tz=timezone.utc),
                    }
        except websockets.ConnectionClosed as e:
            logger.exception("binance_ws_disconnected", reason=str(e))
        except Exception as e:
            logger.exception("binance_ws_error", error=str(e))
