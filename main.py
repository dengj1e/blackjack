import random
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schema import front_json
from calc import 

app = FastAPI(title="blackjack API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/calculations", response_model=response, status_code=200)

    return
