from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schema import front_json, response
from calc import calculate

app = FastAPI(title="blackjack API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/recommend", response_model=response)
def recommend(hand: front_json):
    result = calculate(hand.delt, hand.dealer)
    return result
