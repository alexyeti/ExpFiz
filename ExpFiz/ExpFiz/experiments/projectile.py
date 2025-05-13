import numpy as np
from models.params import ProjectileParams
from config import Config


class ProjectileMotion:
    """Упрощенный класс для расчетов баллистической траектории"""

    def __init__(self):
        self.dt = 0.01  # Шаг интегрирования
        self.min_height = 1e-3  # Минимальная высота для остановки расчета
        self.rho_air = Config.PHYSICS_CONSTANTS['RHO_0']  # Плотность воздуха
        self.cd = Config.PHYSICS_CONSTANTS['CD']  # Коэффициент сопротивления

    def calculate_trajectory(self , params: ProjectileParams):
        """Основной метод расчета траектории"""
        angle_rad = np.radians(params.angle)
        vx = params.initial_velocity * np.cos(angle_rad)
        vy = params.initial_velocity * np.sin(angle_rad)
        x , y = 0.0 , params.initial_height

        trajectory = [(x , y)]
        velocities = [params.initial_velocity]

        # Рассчитываем площадь сечения из массы и плотности шара
        radius = (3 * params.mass / (4 * np.pi * params.density)) ** (1 / 3)
        area = np.pi * radius ** 2

        while y >= self.min_height:
            v = np.sqrt(vx ** 2 + vy ** 2)
            velocities.append(v)

            # Сила сопротивления
            Fd = 0.5 * self.rho_air * self.cd * area * v ** 2
            theta = np.arctan2(vy , vx)

            # Ускорения
            ax = (-Fd * np.cos(theta)) / params.mass
            ay = -params.gravity + (-Fd * np.sin(theta)) / params.mass

            # Простое интегрирование (Эйлер)
            vx += ax * self.dt
            vy += ay * self.dt
            x += vx * self.dt
            y += vy * self.dt

            trajectory.append((x , y))

            if x > 1e6:  # Защита от бесконечного цикла
                break

        return np.array(trajectory) , np.array(velocities)