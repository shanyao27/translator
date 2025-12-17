import re

def preprocess(text: str) -> str:
    # убираем // комментарии
    text = re.sub(r"//.*", "", text)
    # убираем { ... } комментарии
    text = re.sub(r"\{.*?\}", "", text, flags=re.DOTALL)
    # убираем (* ... *) комментарии
    text = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)

    # нормализуем переводы строк
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text
