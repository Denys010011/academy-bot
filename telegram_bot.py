import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import json
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Загружаем структуру бота
with open("bot_structure_full.json", "r", encoding="utf-8") as f:
    structure = json.load(f)

def create_keyboard(node_key):
    markup = InlineKeyboardMarkup()
    node = structure.get(node_key)
    if not node or "buttons" not in node:
        return markup
    for button in node["buttons"]:
        markup.add(InlineKeyboardButton(button["text"], callback_data=button["next"]))
    return markup

@bot.message_handler(commands=["start"])
def handle_start(message):
    node = structure["start"]
    markup = create_keyboard("start")
    bot.send_message(message.chat.id, node["text"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    node_key = call.data
    node = structure.get(node_key)
    if not node:
        bot.answer_callback_query(call.id, "Раздел не найден.")
        return
    markup = create_keyboard(node_key)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=node["text"],
        reply_markup=markup
    )

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return 'Бот работает!', 200

if __name__ == "__main__":
    # Установка webhook при старте
    url = os.getenv("WEBHOOK_URL")  # Например: https://your-app-name.onrender.com
    bot.remove_webhook()
    bot.set_webhook(url=f"{url}/{TOKEN}")

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
