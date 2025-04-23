from b import tk
class Config:
    TOKEN = tk
    MAX_INPUT_ATTEMPTS = 3
    DEFAULT_GRAVITY = 9.806
    PHYSICS_CONSTANTS = {
        'RHO_0': 1.225,    # Плотность воздуха на уровне моря
        'H_SCALE': 8434,   # Масштабная высота (м)
        'CD': 0.47         # Коэффициент сопротивления
    }