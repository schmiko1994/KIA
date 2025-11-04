"""Upload worker for processing scheduled uploads"""

import asyncio
from datetime import datetime
from app.config import settings
from app.utils.logger import app_logger


async def start_upload_worker():
    """Start the upload worker"""
    if not settings.enable_upload_worker:
        app_logger.info("Upload worker is disabled")
        return
    
    app_logger.info("Starting upload worker")
    
    while True:
        try:
            await process_upload_queue()
            await asyncio.sleep(settings.upload_worker_interval)
        except Exception as e:
            app_logger.error(f"Upload worker error: {e}")
            await asyncio.sleep(60)


async def process_upload_queue():
    """Process pending uploads"""
    try:
        # In production, this would query database for pending schedules
        # and execute uploads using the upload service
        app_logger.debug("Processing upload queue")
    except Exception as e:
        app_logger.error(f"Error processing upload queue: {e}")
