from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryBody(BaseModel):
    text: str

@app.post("/query")
def perform_query(body: QueryBody):
    return { "text": "your query was " + body.text }
