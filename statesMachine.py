import configparser  # Импорт модуля для работы с конфигурационными файлами
import logging  # Импортдуля для логирования
import os  # Импортдуля для работы с операционной системой

# Инициализация логгера
loggerState = logging.getLogger(__name__)
loggerState.setLevel(logging.INFO)
handlerState = logging.FileHandler(f"logs/{__name__}.log", mode="w")
formatterState = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handlerState.setFormatter(formatterState)
loggerState.addHandler(handlerState)


# Чтение конфигурационного файла
config = configparser.ConfigParser()
config.read("config.ini")


# Класс Машина состояний для бота Вконтакте с использованием sqlite3, где будет сохраняться id пользователя и его
class StatesMachine:
    state = None  # Атрибут для хранения текущего состояния

    def __init__(self):
        loggerState.info("Машина состояний инициализируется")
        self.initCheck()
        self.state = self.getState()  # Установка текущего состояния

    def initCheck(self) -> None:
        # Проверка на существование файла текущего состояния
        if os.path.isfile("states/currentState.txt"):
            try:
                # Чтение текущего состояния из файла
                with open("states/currentState.txt", "r") as file:
                    self.state = file.read().strip()
                loggerState.info("Файл состояния загружен")
            except Exception as ex:
                loggerState.error(f"Ошибка при чтении файла состояния. Ошибка: {ex}")
        else:
            with open("states/currentState.txt", "w") as file:
                file.write("start")

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
