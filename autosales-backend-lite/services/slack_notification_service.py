import requests
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_notification(vehicle: dict):
    if not SLACK_WEBHOOK_URL:
        return

    text = f"""
🚗 New Vehicle Added
VIN: {vehicle.get("vin")}
{vehicle.get("year", "")} {vehicle.get("make", "")} {vehicle.get("model", "")}
💰 Price: ${vehicle.get("price_purchase", 0)}
📍 {vehicle.get("city", "")}, {vehicle.get("state", "")}
Status: {vehicle.get("status", "new")}
"""

    requests.post(SLACK_WEBHOOK_URL, json={"text": text.strip()}, timeout=5)