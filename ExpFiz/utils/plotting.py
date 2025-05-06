import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np


class PlotGenerator:
    @staticmethod
    async def kinematics(v0: float , a: float , t_max: float):
        """Генерация графика для равноускоренного движения"""
        plt.style.use('seaborn-v0_8-darkgrid')  # Стиль с сеткой

        # Создаём данные
        t = np.linspace(0 , t_max , 100)
        s = v0 * t + (a * t ** 2) / 2

        # Настройка графика
        fig , ax = plt.subplots(figsize=(10 , 6))
        ax.plot(t , s , linewidth=3 , color='#3498db' , label=f'v₀={v0} м/с, a={a} м/с²')

        # Оформление
        ax.set_title('Зависимость пути от времени' , pad=20 , fontsize=14)
        ax.set_xlabel('Время (с)' , fontsize=12)
        ax.set_ylabel('Расстояние (м)' , fontsize=12)
        ax.legend()
        ax.grid(True , alpha=0.4)

        # Сохраняем в буфер
        buf = BytesIO()
        plt.savefig(buf , format='png' , dpi=120 , bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return buf