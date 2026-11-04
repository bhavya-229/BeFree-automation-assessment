import asyncio
import os
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.chdir("d:/beFree/backend")
sys.path.insert(0, "d:/beFree/backend")

from app.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting uvicorn on 127.0.0.1:8000...", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
