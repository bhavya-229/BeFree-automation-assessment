from pathlib import Path
import os
import sys

backend_dir = Path(__file__).resolve().parent
os.chdir(backend_dir)
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn

if __name__ == "__main__":
    print("Starting uvicorn on 127.0.0.1:8000...", flush=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
