#!/usr/bin/env python3
"""
Generate OpenAPI specification and export to JSON.
"""

import json
import sys
sys.path.insert(0, '/Volumes/Project Disk/Project Built/Z/Agent Projects/LAS/gemini_build/las_core')

from api import app

# Generate OpenAPI schema
openapi_spec = app.openapi()

# Export to JSON
output_file = "openapi.json"
with open(output_file, "w") as f:
    json.dump(openapi_spec, f, indent=2)

print(f"✓ OpenAPI specification exported to {output_file}")
print(f"  Title: {openapi_spec['info']['title']}")
print(f"  Version: {openapi_spec['info']['version']}")
print(f"  Endpoints: {len(openapi_spec['paths'])}")
print(f"\n🌐 View interactive docs at: http://localhost:8080/docs")
