from dataclasses import dataclass

@dataclass
class ProjectileParams:
    """Модель параметров для баллистического эксперимента"""
    mass: float
    angle: float
    gravity: float
    initial_height: float
    initial_velocity: float