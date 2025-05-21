
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# Замените этот токен на свой
import os
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Загружаем структуру бота из JSON-файла
with open("bot_structure_full.json", "r", encoding="utf-8") as f:
    structure = json.load(f)

# Создание клавиатуры по текущему узлу
def create_keyboard(node_key):
    markup = InlineKeyboardMarkup()
    node = structure.get(node_key)
    if not node or "buttons" not in node:
        return markup
    for button in node["buttons"]:
        markup.add(InlineKeyboardButton(button["text"], callback_data=button["next"]))
    return markup

# Обработка команды /start
@bot.message_handler(commands=["start"])
def handle_start(message):
    node = structure["start"]
    markup = create_keyboard("start")
    bot.send_message(message.chat.id, node["text"], reply_markup=markup)

# Обработка всех нажатий на inline-кнопки
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

# Запуск бота
print("Бот запущен.")
bot.infinity_polling()
