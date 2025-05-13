def validate_positive_number(input_str: str, field_name: str):
    """Валидация положительных чисел"""
    try:
        value = float(input_str.replace(",", "."))
        if value <= 0:
            raise ValueError(f"{field_name} должна быть больше 0")
        return value
    except ValueError:
        raise ValueError(f"Некорректный ввод для {field_name}. Введите число")

def validate_angle(input_str: str):
    """Специальная валидация для угла"""
    try:
        angle = float(input_str.replace(",", "."))
        if angle <= 0 or angle >= 90:
            raise ValueError("Угол должен быть между 0 и 90 градусами")
        return angle
    except ValueError:
        raise ValueError("Некорректный угол. Введите число от 0 до 90")