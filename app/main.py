import hashlib

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_VERSION = "0.1.0"
MAX_TEXT_BYTES = 4096

app = FastAPI(
    title="Secure Delivery API",
    version=APP_VERSION,
)


class ChecksumRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_BYTES)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": APP_VERSION}


@app.post("/checksum")
def checksum(request: ChecksumRequest):
    encoded = request.text.encode("utf-8")

    if len(encoded) > MAX_TEXT_BYTES:
        raise HTTPException(
            status_code=422,
            detail="Text exceeds the 4096-byte limit",
        )

    return {
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "bytes": len(encoded),
    }
