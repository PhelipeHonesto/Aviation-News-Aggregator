#!/usr/bin/env python3

import os
os.environ["DATABASE_URL"] = "postgresql://postgres:Kikobaby%4022%21@db.lnlbcpsrpaltkntjghvk.supabase.co:5432/postgres"

from main import app

print("Available routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"  {route.methods} {route.path}")

print("\nBookmark routes:")
for route in app.routes:
    if hasattr(route, 'path') and 'bookmark' in route.path:
        print(f"  {route.methods} {route.path}")
