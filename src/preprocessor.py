# предобработка текста Pascal
import re

def preprocess(text: str) -> str:
    # убрать // комментарии
    text = re.sub(r"//.*", "", text)
    # убрать { ... } комментарии
    text = re.sub(r"\{.*?\}", "", text, flags=re.DOTALL)
    # убрать (* ... *) комментарии
    text = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)

    # нормализуем переводы строк
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text
