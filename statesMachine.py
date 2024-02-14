import configparser
import logging
import os

loggerState = logging.getLogger(__name__)
loggerState.setLevel(logging.INFO)
handlerState = logging.FileHandler(f"logs/{__name__}.log", mode="w")
formatterState = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handlerState.setFormatter(formatterState)
loggerState.addHandler(handlerState)


config = configparser.ConfigParser()
config.read("config.ini")


# Машина состояний для бота Вконтакте с использованием sqlite3, где будет сохраняться id пользователя и его
class StatesMachine:
    state = None
    # states_dict = {
    #     "start": [
    #         "start",
    #         "exit",
    #     ],  # TODO: написать словарь с клавиатурами и генератор клавиатур
    #     "ask_name": ["check_name", "ask_age"],
    # }

    def __init__(self):
        loggerState.info("Машина состояний инициализируется")
        self.initCheck()
        self.state = self.getState()  # текущее состояние машины состояний

    def initCheck(self):
        if os.path.isfile("states/currentState.txt"):
            try:
                with open("states/currentState.txt", "r") as file:
                    self.state = file.read().strip()
                loggerState.info("Файл состояния загружен")
            except Exception as ex:
                loggerState.error(f"Ошибка при чтении файла состояния. Ошибка: {ex}")
        else:
            with open("states/currentState.txt", "w") as file:
                file.write("start")  # TODO: сделать актуальные состояния

    def getState(self) -> str:
        try:
            with open("states/currentState.txt", "r") as file:
                state = file.read().strip()
                loggerState.info("Состояние прочитано")
                return state
        except Exception as ex:
            loggerState.error(f"Ошибка при чтении состояния. Ошибка: {ex}")

    def setState(self, state) -> None:
        try:
            with open("states/currentState.txt", "w") as file:
                file.write(state)
                loggerState.info("Состояние установлено")
        except Exception as ex:
            loggerState.error(f"Ошибка при изменении состояния. Ошибка: {ex}")
