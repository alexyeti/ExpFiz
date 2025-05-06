import numpy as np
from models.params import ProjectileParams
from config import Config

class ProjectileMotion:
    """Класс для расчетов баллистической траектории"""

    def __init__(self):
        self.dt = 0.01  # Шаг интегрирования
        self.min_height = 1e-3  # Минимальная высота для остановки расчета

    def calculate_trajectory(self, params: ProjectileParams):
        """Основной метод расчета траектории"""
        angle_rad = np.radians(params.angle)
        vx = params.initial_velocity * np.cos(angle_rad)
        vy = params.initial_velocity * np.sin(angle_rad)
        x, y = 0.0, params.initial_height

        trajectory = [(x, y)]
        velocities = [params.initial_velocity]

        while y >= self.min_height:
            v = np.sqrt(vx**2 + vy**2)
            velocities.append(v)

            # Ускорения (только гравитация)
            ax = 0
            ay = -params.gravity

            # Интегрирование Эйлера
            vx += ax * self.dt
            vy += ay * self.dt
            x += vx * self.dt
            y += vy * self.dt

            trajectory.append((x, y))

            if x > 1e6:  # Защита от бесконечного цикла
                break

        return np.array(trajectory), np.array(velocities)