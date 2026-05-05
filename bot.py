import os
from openai import OpenAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# 🔍 Debug
print("OPENAI:", bool(os.getenv("OPENAI_API_KEY")))
print("SLACK BOT:", bool(os.getenv("SLACK_BOT_TOKEN")))
print("SLACK APP:", bool(os.getenv("SLACK_APP_TOKEN")))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found")

if not SLACK_BOT_TOKEN:
    raise ValueError("❌ SLACK_BOT_TOKEN not found")

if not SLACK_APP_TOKEN:
    raise ValueError("❌ SLACK_APP_TOKEN not found")

client = OpenAI(api_key=OPENAI_API_KEY)

# 🚀 Slack app
app = App(token=SLACK_BOT_TOKEN)

# 🧠 PROMPTS

TRANSLATOR_PROMPT = """
You are a professional translator specializing in German advertising copy.

Your task is to translate the text below from English into natural, fluent Standard German (Hochdeutsch).

CONTEXT:
- Brand: a Swiss activity discovery app
- Audience: Swiss locals and tourists
- Placement: short social media ads (Instagram, Facebook, etc.)

TONE:
Friendly, energetic, and broadly appealing. Natural and engaging — not too casual, not too formal.

RULES:
1. Translate meaning and intent — not word-for-word.
2. Keep the original structure unless it sounds unnatural in German.
3. Use "du" when addressing the reader.
4. Do NOT translate brand names, app names, slogans, or hashtags.
5. Use clean Standard German (no Swiss slang or dialect).
6. Keep emojis if they fit naturally.
7. Preserve CTA intent if present.

IMPORTANT:
- Do NOT improve or rewrite heavily — focus on accurate, natural translation.

OUTPUT:
Return ONLY the German translation.
"""

REVIEW_PROMPT = """
You are a senior German copywriter and editor specializing in high-performing social media ads for Swiss audiences.

You will receive:
1. The original English text
2. A German translation

Your task is to refine the German version into a polished, high-quality ad.

GOALS:
- Make the text sound fully native and natural
- Improve clarity, rhythm, and flow
- Strengthen the marketing appeal
- Ensure consistency with the original meaning

CHECK:
- Natural phrasing (no literal translation artifacts)
- Correct use of "du"
- Brand names, hashtags, slogans unchanged
- Clear and compelling CTA (if present)
- Tone: friendly, energetic, appealing to both locals and tourists
- Grammar, spelling, punctuation

IMPORTANT:
- Do NOT change the meaning
- Do NOT add new information
- Do NOT make the text longer unless necessary for natural flow

OUTPUT:
Return ONLY the final improved German text.
"""

# 💬 Handler
@app.event("message")
def handle_message_events(body, say):
    event = body.get("event", {})

    if event.get("bot_id"):
        return

    user_text = event.get("text")
    if not user_text:
        return

    # 🥇 STEP 1 — TRANSLATION
    translation = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": TRANSLATOR_PROMPT
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    ).choices[0].message.content.strip()

    # 🥈 STEP 2 — REVIEW
    review_input = f"""
ORIGINAL ENGLISH TEXT:
{user_text}

GERMAN TRANSLATION:
{translation}
"""

    final_text = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": REVIEW_PROMPT
            },
            {
                "role": "user",
                "content": review_input
            }
        ]
    ).choices[0].message.content.strip()

    # 📤 Відповідь
    say(f"🇩🇪 {final_text}")

# ▶️ Запуск
if __name__ == "__main__":
    print("⚡ Slack bot is running...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()