from fastapi import FastAPI, Request
import json
from binance_client import place_order, get_price, set_leverage, get_balance, get_position

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    symbol = data["symbol"]
    side = data["side"].upper()
    leverage = int(data["leverage"])
    margin_pct = float(data["margin_pct"])

    # 현재가 조회
    price_data = get_price(symbol)
    if side == "LONG":
        price = float(price_data["bidPrice"]) - 0.01
        order_side = "BUY"
    elif side == "SHORT":
        price = float(price_data["askPrice"]) + 0.01
        order_side = "SELL"
    else:
        # 반대 포지션 청산
        pos = get_position(symbol)
        if float(pos["positionAmt"]) != 0:
            close_side = "SELL" if float(pos["positionAmt"]) > 0 else "BUY"
            qty = abs(float(pos["positionAmt"]))
            return place_order(symbol, close_side, qty, float(price_data["askPrice"]))
        return {"status": "no position to close"}

    # 레버리지 설정
    set_leverage(symbol, leverage)

    # 잔고 조회 → 수량 계산
    balances = get_balance()
    usdt_balance = float([b for b in balances if b["asset"] == "USDT"][0]["balance"])
    trade_value = usdt_balance * margin_pct
    qty = round(trade_value / price, 3)

    # 기존 포지션 중복 확인
    pos = get_position(symbol)
    if (side == "LONG" and float(pos["positionAmt"]) > 0) or \
       (side == "SHORT" and float(pos["positionAmt"]) < 0):
        return {"status": "already in position"}

    # 주문
    return place_order(symbol, order_side, qty, price)
