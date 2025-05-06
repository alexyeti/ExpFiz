from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
from experiments.projectile import ProjectileMotion
from models.params import ProjectileParams
from utils.plotting import PlotGenerator
from utils.validators import validate_positive_number, validate_angle
import numpy as np
import logging
from io import BytesIO

# Состояния ConversationHandler
(
    INPUT_MASS, INPUT_ANGLE, INPUT_GRAVITY,
    INPUT_H0, INPUT_V0, CONFIRM_PARAMS
) = range(6)

class ProjectileMotionHandler:
    def __init__(self):
        self.calculator = ProjectileMotion()
        self.logger = logging.getLogger(__name__)

    async def start_experiment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало эксперимента с интерактивным меню"""
        keyboard = [
            [InlineKeyboardButton("Использовать стандартные параметры", callback_data='default')],
            [InlineKeyboardButton("Ввести свои параметры", callback_data='custom')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🔭 <b>Эксперимент: Движение снаряда</b>\n\n"
            "Выберите режим ввода параметров:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return INPUT_MASS

    async def handle_mode_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора режима"""
        query = update.callback_query
        await query.answer()

        if query.data == 'default':
            context.user_data.update({
                'mass': 1.0,
                'angle': 45,
                'gravity': 9.8,
                'h0': 0,
                'v0': 20
            })
            await query.edit_message_text("✅ Используются стандартные параметры")
            return await self.show_confirmation(update, context)
        else:
            await query.edit_message_text("Введите массу снаряда (кг):")
            return INPUT_MASS

    async def input_mass(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка массы с примером"""
        try:
            mass = validate_positive_number(update.message.text, "Масса")
            context.user_data['mass'] = mass
            await update.message.reply_text(
                "📐 Введите угол запуска (0-90°):\n"
                "<i>Пример: 45 (для угла в 45 градусов)</i>",
                parse_mode='HTML'
            )
            return INPUT_ANGLE
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}\nПопробуйте снова:")
            return INPUT_MASS

    async def input_angle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка угла с валидацией"""
        try:
            angle = validate_angle(update.message.text)
            context.user_data['angle'] = angle
            await update.message.reply_text(
                "🌍 Введите ускорение свободного падения (м/с²):\n"
                "<i>Стандартное значение для Земли: 9.8</i>",
                parse_mode='HTML'
            )
            return INPUT_GRAVITY
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}\nПопробуйте снова:")
            return INPUT_ANGLE

    async def input_gravity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ускорения с подсказкой"""
        try:
            gravity = validate_positive_number(update.message.text, "Ускорение свободного падения")
            context.user_data['gravity'] = gravity
            await update.message.reply_text(
                "🏗 Введите начальную высоту (м):\n"
                "<i>Пример: 10 (для запуска с 10 метров)</i>",
                parse_mode='HTML'
            )
            return INPUT_H0
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}\nПопробуйте снова:")
            return INPUT_GRAVITY

    async def input_h0(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка высоты"""
        try:
            h0 = validate_positive_number(update.message.text, "Начальная высота")
            context.user_data['h0'] = h0
            await update.message.reply_text(
                "💨 Введите начальную скорость (м/с):\n"
                "<i>Пример: 15 (для 15 м/с)</i>",
                parse_mode='HTML'
            )
            return INPUT_V0
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}\nПопробуйте снова:")
            return INPUT_H0

    async def input_v0(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка скорости и переход к подтверждению"""
        try:
            v0 = validate_positive_number(update.message.text, "Начальная скорость")
            context.user_data['v0'] = v0
            return await self.show_confirmation(update, context)
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}\nПопробуйте снова:")
            return INPUT_V0

    async def show_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ подтверждения параметров"""
        params_text = (
            "📋 <b>Параметры эксперимента:</b>\n"
            f"• Масса: {context.user_data['mass']} кг\n"
            f"• Угол: {context.user_data['angle']}°\n"
            f"• Ускорение: {context.user_data['gravity']} м/с²\n"
            f"• Высота: {context.user_data['h0']} м\n"
            f"• Скорость: {context.user_data['v0']} м/с"
        )

        keyboard = [
            [InlineKeyboardButton("✅ Начать расчет", callback_data='confirm')],
            [InlineKeyboardButton("🔄 Изменить параметры", callback_data='change')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if hasattr(update, 'callback_query'):
            await update.callback_query.edit_message_text(
                params_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                params_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        return CONFIRM_PARAMS

    async def confirm_parameters(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка подтверждения параметров"""
        query = update.callback_query
        await query.answer()

        if query.data == 'confirm':
            try:
                params = ProjectileParams(
                    mass=context.user_data['mass'],
                    angle=context.user_data['angle'],
                    gravity=context.user_data['gravity'],
                    initial_height=context.user_data['h0'],
                    initial_velocity=context.user_data['v0']
                )

                trajectory, velocities = self.calculator.calculate_trajectory(params)
                flight_time = len(trajectory) * 0.01
                max_height = np.max(trajectory[:, 1])
                distance = trajectory[-1, 0]
                max_speed = np.max(velocities)

                plot_buffer = BytesIO()
                PlotGenerator.generate_trajectory_plot(
                    trajectory=trajectory,
                    params=params,
                    output=plot_buffer
                )
                plot_buffer.seek(0)

                result_text = (
                    "🎯 <b>Результаты эксперимента:</b>\n\n"
                    f"⏱ <b>Время полета:</b> {flight_time:.2f} сек\n"
                    f"📏 <b>Макс. высота:</b> {max_height:.2f} м\n"
                    f"🏁 <b>Дальность:</b> {distance:.2f} м\n"
                    f"🚀 <b>Макс. скорость:</b> {max_speed:.2f} м/с"
                )

                await query.message.reply_photo(
                    photo=plot_buffer,
                    caption=result_text,
                    parse_mode='HTML'
                )
                plot_buffer.close()

                return ConversationHandler.END

            except Exception as e:
                self.logger.error(f"Calculation error: {str(e)}", exc_info=True)
                await query.message.reply_text(
                    "⚠️ Произошла ошибка при расчетах. Попробуйте другие параметры."
                )
                return ConversationHandler.END
        else:
            await query.edit_message_text("Введите массу снаряда (кг):")
            return INPUT_MASS

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена эксперимента"""
        await update.message.reply_text(
            "❌ Эксперимент отменен. "
            "Вы можете начать заново командой /projectile_motion"
        )
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
                CONFIRM_PARAMS: [CallbackQueryHandler(self.confirm_parameters)]
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                CallbackQueryHandler(self.handle_mode_selection, pattern='^(default|custom)$')
            ],
            allow_reentry=True
        )