from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from experiments.projectile import ProjectileMotion
from models.params import ProjectileParams
from utils.plotting import plot_trajectory
from utils.validators import validate_positive_number, validate_angle
import numpy as np

# Состояния ConversationHandler
(
    INPUT_MASS, INPUT_ANGLE, INPUT_GRAVITY,
    INPUT_H0, INPUT_V0, INPUT_DENSITY
) = range(6)

class ProjectileMotionHandler:
    def __init__(self):
        self.calculator = ProjectileMotion()

    async def start_experiment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало эксперимента"""
        await update.message.reply_text("Введите параметры:\n1. Масса (кг):")
        return INPUT_MASS

    async def input_mass(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка массы"""
        try:
            mass = validate_positive_number(update.message.text, "Масса")
            context.user_data['mass'] = mass
            await update.message.reply_text("2. Угол запуска (0-90°):")
            return INPUT_ANGLE
        except ValueError as e:
            await update.message.reply_text(str(e))
            return INPUT_MASS

    async def input_angle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка угла запуска"""
        try:
            angle = validate_angle(update.message.text)
            context.user_data['angle'] = angle
            await update.message.reply_text("3. Ускорение свободного падения (м/с²):")
            return INPUT_GRAVITY
        except ValueError as e:
            await update.message.reply_text(str(e))
            return INPUT_ANGLE

    async def input_gravity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ускорения свободного падения"""
        try:
            gravity = validate_positive_number(update.message.text, "Ускорение свободного падения")
            context.user_data['gravity'] = gravity
            await update.message.reply_text("4. Начальная высота (м):")
            return INPUT_H0
        except ValueError as e:
            await update.message.reply_text(str(e))
            return INPUT_GRAVITY

    async def input_h0(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка начальной высоты"""
        try:
            h0 = validate_positive_number(update.message.text, "Начальная высота")
            context.user_data['h0'] = h0
            await update.message.reply_text("5. Начальная скорость (м/с):")
            return INPUT_V0
        except ValueError as e:
            await update.message.reply_text(str(e))
            return INPUT_H0

    async def input_v0(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка начальной скорости"""
        try:
            v0 = validate_positive_number(update.message.text, "Начальная скорость")
            context.user_data['v0'] = v0
            await update.message.reply_text("6. Плотность шара (кг/м³):")
            return INPUT_DENSITY
        except ValueError as e:
            await update.message.reply_text(str(e))
            return INPUT_V0

    async def input_density(self , update: Update , context: ContextTypes.DEFAULT_TYPE):
        """Финальный обработчик - расчет и вывод результатов"""
        try:
            density = validate_positive_number(update.message.text , "Плотность")
            params = ProjectileParams(
                mass=context.user_data['mass'] ,
                angle=context.user_data['angle'] ,
                gravity=context.user_data['gravity'] ,
                initial_height=context.user_data['h0'] ,
                initial_velocity=context.user_data['v0'] ,
                density=density
            )

            trajectory , velocities = self.calculator.calculate_trajectory(params)

            # Генерация графика
            import matplotlib
            matplotlib.use('Agg')
            from utils.plotting import plot_trajectory
            plot_trajectory(trajectory)

            # Формирование текста с результатами
            result = (
                "📊 Результаты:\n"
                f"⏱ Время: {len(trajectory) * 0.01:.2f} сек\n"
                f"📏 Макс. высота: {np.max(trajectory[: , 1]):.2f} м\n"
                f"🏁 Дальность: {trajectory[-1 , 0]:.2f} м\n"
                f"🚀 Макс. скорость: {np.max(velocities):.2f} м/с"
            )

            # Отправка результатов и графика
            await update.message.reply_text(result)
            with open("trajectory.png" , "rb") as photo:
                await update.message.reply_photo(photo)

            return ConversationHandler.END

        except ValueError as e:
            await update.message.reply_text(str(e))
            return INPUT_DENSITY
        except Exception as e:
            await update.message.reply_text(f"Ошибка при расчетах: {str(e)}")
            return INPUT_DENSITY

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена эксперимента"""
        await update.message.reply_text("Эксперимент отменен.")
        return ConversationHandler.END

    def get_handler(self):
        """Возвращает настроенный ConversationHandler"""
        return ConversationHandler(
            entry_points=[CommandHandler("projectile_motion", self.start_experiment)],
            states={
                INPUT_MASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_mass)],
                INPUT_ANGLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_angle)],
                INPUT_GRAVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_gravity)],
                INPUT_H0: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_h0)],
                INPUT_V0: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_v0)],
                INPUT_DENSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_density)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)]
        )