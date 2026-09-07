from datetime import datetime

def log(text):

    with open("logs/log.txt", "a", encoding="utf8") as f:

        f.write(f"[{datetime.now()}] {text}\n")