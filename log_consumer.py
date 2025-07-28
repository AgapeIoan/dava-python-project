import os
import asyncio
import redis.asyncio as redis
from redis.exceptions import RedisError

REDIS_STREAM_KEY = "log_stream"
LOG_FILE = "log.txt"

# ✅ Folosim variabilă de mediu pentru flexibilitate (localhost vs redis)
redis_host = os.getenv("REDIS_HOST", "localhost")

async def consume_logs():
    print("✅ log_consumer.py A PORNIT!")

    try:
        client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
        last_id = "0"
        print(f"👂 Conectat la Redis ({redis_host}:6379). Ascultăm logurile...\n")

        while True:
            try:
                entries = await client.xread({REDIS_STREAM_KEY: last_id}, count=10, block=5000)
                for stream, messages in entries:
                    for msg_id, data in messages:
                        log_line = (
                            f"[{data.get('timestamp')}] "
                            f"[{data.get('level')}] "
                            f"{data.get('message')} "
                            f"{data.get('extra')}"
                        )

                        # ✅ Afișează în terminal
                        print("🧾 Log primit:")
                        print(log_line)
                        print("-" * 60)

                        # ✅ Scrie în fișier
                        with open(LOG_FILE, "a", encoding="utf-8") as f:
                            f.write(log_line + "\n")

                        last_id = msg_id

            except RedisError as e:
                print(f"❌ Eroare la citirea din Redis: {e}")
                await asyncio.sleep(2)

    except Exception as e:
        print(f"🚨 Eroare generală în log_consumer.py: {e}")

if __name__ == "__main__":
    asyncio.run(consume_logs())
