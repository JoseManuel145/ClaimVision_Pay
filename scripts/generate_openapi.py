#!/usr/bin/env python3
"""Genera openapi.json desde la app FastAPI."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.main import app

output = Path("openapi_pay.json")
output.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False))
print(f"OpenAPI generado en {output}  ({output.stat().st_size:,} bytes)")