import re

def preprocess(text: str) -> str:

    text = re.sub(r"//.*", "", text)

    text = re.sub(r"\{.*?\}", "", text, flags=re.DOTALL)

    text = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)


    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text