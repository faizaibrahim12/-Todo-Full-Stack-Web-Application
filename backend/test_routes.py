"""Debug route registration"""
import sys
sys.path.insert(0, '.')

from main import app

print("Registered routes:")
for route in app.routes:
    print(f"  {route.methods} {route.path}")

print("\nAuth router routes:")
for route in app.routes:
    if hasattr(route, 'router'):
        print(f"  {route.methods} {route.path}")
