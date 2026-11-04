"""Bank Statement Processing & Classification System Backend."""

import os
# Prevent OpenBLAS thread allocation issues on Windows Python 3.13
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
