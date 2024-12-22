import string
import datetime as dt

def server_print(category: str, text: str) -> None:
    current_time = dt.datetime.now()
    print(f"\033[38;2;242;202;41m[{current_time.strftime('%d-%m-%Y %H:%M:%S')}] [{category}] " + text + "\033[0m")

    # log system
    with open(f"Logs/{current_time.strftime('%d-%m-%Y')}.log", 'a') as log:
        log.write(f"[{current_time.strftime('%d-%m-%Y %H:%M:%S')}] [{category}] " + text + "\n")