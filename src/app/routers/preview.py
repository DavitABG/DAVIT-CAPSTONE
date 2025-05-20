# src/app/routers/preview.py

import os
import sqlite3
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/preview")
def preview():
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise HTTPException(status_code=500, detail="DB_URL environment variable not set")
    try:
        conn = sqlite3.connect(db_url)
        cursor = conn.cursor()
        # Get first user table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        if not tables:
            return {"error": "No tables found in database"}
        table_name = tables[0][0]
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        conn.close()
        return {
            "columns": col_names,
            "rows": rows,
            "table": table_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
