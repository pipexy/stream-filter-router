from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Gauge
from fastapi.responses import Response
import psutil
import os

app = FastAPI()

# Metryki
STREAM_PROCESSED = Counter('sfr_stream_processed_total', 'Total number of processed streams')
STREAM_ERRORS = Counter('sfr_stream_errors_total', 'Total number of stream processing errors')
ACTIVE_STREAMS = Gauge('sfr_active_streams', 'Number of currently active streams')
CPU_USAGE = Gauge('sfr_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('sfr_memory_usage_bytes', 'Memory usage in bytes')


@app.get("/metrics")
async def metrics():
    # Aktualizuj metryki
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.Process(os.getpid()).memory_info().rss)

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
