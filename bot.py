from openai import OpenAI
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# 🔐 ENV
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

print("DEBUG ENV:")
print("OPENAI:", bool(OPENAI_API_KEY))
print("SLACK BOT:", bool(SLACK_BOT_TOKEN))
print("SLACK APP:", bool(SLACK_APP_TOKEN))

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found")

if not SLACK_BOT_TOKEN:
    raise ValueError("❌ SLACK_BOT_TOKEN not found")

if not SLACK_APP_TOKEN:
    raise ValueError("❌ SLACK_APP_TOKEN not found")

client = OpenAI(api_key=OPENAI_API_KEY)

# 🚀 Slack app
app = App(token=SLACK_BOT_TOKEN)

# 💬 Handler
@app.event("message")
def handle_message_events(body, say):
    event = body.get("event", {})

    if event.get("bot_id"):
        return

    user_text = event.get("text")
    if not user_text:
        return

    # STEP 1 — TRANSLATE
    translate_prompt = f"""
You are a native German copywriter.
Translate this English text into natural, engaging German.

Text: {user_text}
"""

    translation = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": translate_prompt}]
    ).choices[0].message.content.strip()

    # STEP 2 — REVIEW
    review_prompt = f"""
Improve this German text. Keep it natural and concise.

Text: {translation}
"""

    final_text = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": review_prompt}]
    ).choices[0].message.content.strip()

    say(f"🇩🇪 {final_text}")


# ▶️ Запуск
if __name__ == "__main__":
    print("⚡ Slack bot is running...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()