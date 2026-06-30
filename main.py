import time
import uuid
from collections import deque
from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

EMAIL = "23f2000298@ds.study.iitm.ac.in"
START_TIME = time.time()

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests received")

# Keep the last 500 log entries in memory
LOGS = deque(maxlen=500)


@app.middleware("http")
async def logging_and_counting_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    LOGS.append({
        "level": "info",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id,
        "method": request.method,
        "status_code": response.status_code,
    })

    return response


@app.get("/work")
async def work(n: int = 1):
    total = 0
    for i in range(n):
        total += i
    return {"email": EMAIL, "done": n}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "uptime_s": time.time() - START_TIME}


@app.get("/logs/tail")
async def logs_tail(limit: int = 10):
    entries = list(LOGS)[-limit:]
    return entries


@app.get("/")
async def root():
    return {"status": "ok", "endpoints": ["/work", "/metrics", "/healthz", "/logs/tail"]}
