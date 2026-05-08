from fastapi import FastAPI, Depends, HTTPException
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

@app.post("/recommend", response_model=HandResponse)
def recommend(hand: HandRequest):
    result = calculate(hand.dealt, hand.dealer)
    return result
