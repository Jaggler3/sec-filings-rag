from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class QueryBody(BaseModel):
    text: str

@app.post("/query")
def perform_query(body: QueryBody):
    response = requests.post("http://localhost:7070/query", json={ "text": "sending to go" })
    print("status code", response.status_code)
    return response.json()