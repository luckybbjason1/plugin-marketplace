#!/usr/bin/env python3
"""
Plugin Marketplace - 自动赚钱项目
出售 WordPress/Shopify/浏览器插件
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from pathlib import Path

app = FastAPI(title="Plugin Marketplace", version="1.0.0")

DB_PATH = Path.home() / "桌面" / "plugin-marketplace" / "plugins.db"
DB_PATH.parent.mkdir(exist_ok=True)

class Plugin(BaseModel):
    name: str
    type: str  # wordpress, shopify, chrome
    price: float
    description: str

class Purchase(BaseModel):
    plugin_id: int
    email: str

@app.get("/")
async def root():
    return {
        "message": "Plugin Marketplace - 自动赚钱",
        "supported_types": ["WordPress", "Shopify", "Chrome Extension", "VS Code"]
    }

@app.post("/upload")
async def upload_plugin(plugin: Plugin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO plugins (name, type, price, description) VALUES (?, ?, ?, ?)",
        (plugin.name, plugin.type, plugin.price, plugin.description)
    )
    conn.commit()
    conn.close()
    return {"message": "Plugin uploaded", "plugin_id": 1}

@app.post("/purchase")
async def purchase_plugin(purchase: Purchase):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM plugins WHERE id = ?", (purchase.plugin_id,))
    plugin = cursor.fetchone()
    if not plugin:
        conn.close()
        return {"error": "Plugin not found"}
    
    cursor.execute(
        "INSERT INTO purchases (plugin_id, email, amount) VALUES (?, ?, ?)",
        (purchase.plugin_id, purchase.email, plugin[0])
    )
    conn.commit()
    conn.close()
    return {"message": "Purchase successful", "price": plugin[0]}

@app.get("/stats")
async def stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM plugins")
    total_plugins = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM purchases")
    total_revenue = cursor.fetchone()[0] or 0
    conn.close()
    return {
        "total_plugins": total_plugins,
        "total_revenue": total_revenue,
        "monthly_revenue": total_revenue * 12
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
