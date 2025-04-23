import logging
from telegram.ext import Application
from config import Config
from bot.handlers.commands import get_handlers
from bot.handlers.experiments_2.projectile_motion import ProjectileMotionHandler

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' ,
    level=logging.INFO
)


async def post_init(app: Application):
    """Действия после инициализации бота"""
    logging.info("Бот успешно запущен")


def setup_handlers(app: Application):
    """Регистрация всех обработчиков"""
    # Основные команды
    for handler in get_handlers():
        app.add_handler(handler)

    # Обработчик эксперимента
    projectile_handler = ProjectileMotionHandler()
    app.add_handler(projectile_handler.get_handler())


def main():
    """Точка входа"""
    app = Application.builder() \
        .token(Config.TOKEN) \
        .post_init(post_init) \
        .build()

    setup_handlers(app)

    app.run_polling()


if __name__ == "__main__":
    main()