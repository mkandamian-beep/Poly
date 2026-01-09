import requests
import time
import os

WEBHOOK = os.getenv("DISCORD_WEBHOOK")
if not WEBHOOK:
    raise RuntimeError("Missing DISCORD_WEBHOOK environment variable")

seen = set()

print("Polymarket alerts running")

while True:
    try:
        markets = requests.get(
            "https://gamma-api.polymarket.com/markets?sort=createdAt&limit=10",
            timeout=10
        ).json()

        # First run: populate 'seen' to avoid spamming old markets
        if not seen:
            for m in markets:
                seen.add(m["id"])
            print("Initialized seen set; waiting for new markets...")
        else:
            for m in markets:
                if m["id"] not in seen:
                    seen.add(m["id"])
                    msg = (
                        f"🚨 New Polymarket market:\n"
                        f"{m.get('question','(no question)')}\n"
                        f"https://polymarket.com/market/{m.get('slug','')}"
                    )
                    requests.post(WEBHOOK, json={"content": msg}, timeout=10)
                    print("Sent alert:", m.get("question"))

        time.sleep(120)  # check every 2 minutes

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
