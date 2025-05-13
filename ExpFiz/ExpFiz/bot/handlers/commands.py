from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_message = (
        "👋 Привет! Я бот для физических экспериментов.\n"
        "Доступные команды:\n"
        "/start - Начать\n"
        "/projectile_motion - Эксперимент с баллистикой"
    )
    await update.message.reply_text(welcome_message)

def get_handlers():
    """Возвращает список обработчиков команд"""
    return [
        CommandHandler('start', start)
    ]