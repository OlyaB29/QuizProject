import telebot
from .config import sender_TOKEN

bot = telebot.TeleBot(token=sender_TOKEN)


def send_quiz_results(chat_id, message):
    bot.send_message(chat_id, message, parse_mode="html")