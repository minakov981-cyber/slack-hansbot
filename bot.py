from openai import OpenAI
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# 🔑 ENV (Railway бере автоматично)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

# 🤖 Slack app
app = App(token=SLACK_BOT_TOKEN)


# 🧠 OpenAI client (створюємо коли потрібно)
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)


# 💬 Handler
@app.event("message")
def handle_message_events(body, say):
    event = body.get("event", {})

    # ❗ Ігноруємо ботів
    if event.get("bot_id"):
        return

    user_text = event.get("text")

    if not user_text:
        return

    print(f"📩 New message: {user_text}")

    client = get_openai_client()

    try:
        # STEP 1 — TRANSLATE
        translate_prompt = f"""
You are a native German copywriter.

Translate this English text into natural, engaging German for an advertising context.

Rules:
- Sound like a native speaker
- Keep it clear and appealing
- Avoid literal translation if it sounds unnatural
- Keep it concise

Text: {user_text}
"""

        translation = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": translate_prompt}]
        ).choices[0].message.content.strip()

        # STEP 2 — REVIEW
        review_prompt = f"""
You are a native German copywriter and editor.

Review and improve this German text.

Rules:
- Keep natural, native tone
- Improve marketing appeal
- Fix grammar if needed
- DO NOT make it longer
- DO NOT add new ideas

Text: {translation}
"""

        final_text = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": review_prompt}]
        ).choices[0].message.content.strip()

        # 📤 Відповідь
        say(f"🇩🇪 {final_text}")

    except Exception as e:
        print("❌ Error:", e)
        say("⚠️ Something went wrong, try again.")


# ▶️ Запуск
if __name__ == "__main__":
    print("🚀 Slack bot starting...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()