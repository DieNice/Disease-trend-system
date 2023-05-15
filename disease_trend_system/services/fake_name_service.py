

def generate_fake_symptom_complex_name(name: str) -> str:
    """Преобразование хеша в более короткое именование

    Args:
        name (str): хеш

    Returns:
        str: Симптомокомлекс + 3 первых символа
    """
    return "СК"+name[:3]
