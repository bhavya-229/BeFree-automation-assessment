import os
import sys

os.chdir("d:/beFree/backend")
sys.path.insert(0, "d:/beFree/backend")

import uvicorn

if __name__ == "__main__":
    print("Starting uvicorn on 127.0.0.1:8000...", flush=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="info")
