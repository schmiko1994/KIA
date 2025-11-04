"""Metrics worker for collecting KPIs"""

import asyncio
from app.config import settings
from app.utils.logger import app_logger


async def start_metrics_worker():
    """Start the metrics worker"""
    if not settings.enable_metrics_worker:
        app_logger.info("Metrics worker is disabled")
        return
    
    app_logger.info("Starting metrics worker")
    
    while True:
        try:
            await collect_metrics()
            await asyncio.sleep(settings.metrics_worker_interval)
        except Exception as e:
            app_logger.error(f"Metrics worker error: {e}")
            await asyncio.sleep(60)


async def collect_metrics():
    """Collect metrics for all accounts and videos"""
    try:
        # In production, this would query database for active accounts
        # and collect metrics using the metrics collector service
        app_logger.debug("Collecting metrics")
    except Exception as e:
        app_logger.error(f"Error collecting metrics: {e}")
