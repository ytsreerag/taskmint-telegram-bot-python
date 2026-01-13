import os
import time
import requests
import pymysql

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    return requests.get(url, params=params).json()

def get_stats():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM users")
        users = cur.fetchone()["total"]

        cur.execute("SELECT SUM(balance) AS total FROM users")
        balance = cur.fetchone()["total"] or 0

    conn.close()
    return users, balance

def main():
    offset = None
    send_message(OWNER_ID, "✅ TaskMint bot started")

    while True:
        updates = get_updates(offset)
        for u in updates.get("result", []):
            offset = u["update_id"] + 1
            msg = u.get("message")
            if not msg:
                continue

            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")

            if chat_id != OWNER_ID:
                send_message(chat_id, "❌ Unauthorized")
                continue

            if text == "/start":
                send_message(chat_id, "✅ Bot connected\nUse /stats")

            if text == "/stats":
                try:
                    users, balance = get_stats()
                    send_message(chat_id,
                        f"📊 TaskMint Stats\n\n👥 Users: {users}\n💰 Balance: ₹{balance}"
                    )
                except Exception as e:
                    send_message(chat_id, f"❌ DB Error:\n{e}")

        time.sleep(1)

if __name__ == "__main__":
    main()
