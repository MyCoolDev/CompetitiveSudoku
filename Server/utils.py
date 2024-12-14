import string
import datetime as dt

def server_print(category: str, text: str) -> None:
    print(f"\033[38;2;242;202;41m[{dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] [{category}]" + text + "\033[0m")