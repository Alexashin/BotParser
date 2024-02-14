# Импорт необходимых модулей
import os
from botCore import BotCore  # Модуль с основными функциями бота
import logging
from vk_api.longpoll import VkLongPoll, VkEventType  # Модуль для работы с Long Poll API
from kbGenerator import KeyBoard  # Модуль для генерации клавиатур
from keyboards.keyboards import kb  # Импортируем список доступных клавиатур

# Инициализируем логгер для Long Poll
loggerLongpoll = logging.getLogger(__name__)
loggerLongpoll.setLevel(logging.INFO)
handler_longpoll = logging.FileHandler(f"logs/{__name__}.log", mode="w")
formatter_longpoll = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler_longpoll.setFormatter(formatter_longpoll)
loggerLongpoll.addHandler(handler_longpoll)

# Импортируем класс с машиной состояний
from statesMachine import StatesMachine


# Класс нашего бота, наследуем от класса BotCore
class LongPollBot(BotCore):
    long_poll = None  # Атрибут для long_poll

    # Инициализация бота
    def __init__(self):
        super().__init__()  # Вызываем конструктор родителя
        loggerLongpoll.info("Longpoll бот инициализируется")
        self.long_poll = VkLongPoll(self.vk_session)  # Инициализируем long_poll

    # Основной цикл long_poll
    def run_long_poll(self):
        for event in self.long_poll.listen():  # Бесконечный цикл прослушивания событий
            if (
                event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text
            ):  # Фильтрация событий
                if int(event.user_id) == self.owner_id:  # Фильтрация по id владельца
                    loggerLongpoll.debug("Получено сообщение")
                    # Обработка введённого текста
                    match event.text:
                        case "Начать":
                            self.states.setState("start")
                            self.sendMessage(
                                message_text="Привет!", kb=KeyBoard.create(kb["start"])
                            )
                        case "Группы":
                            self.states.setState("groups_control")
                            groups = self.getGroupList()
                            if groups != []:
                                self.sendMessage(
                                    message_text=f"Текущий список групп:\n{str(self.getGroupList())}",
                                    kb=KeyBoard.create(kb["control"]),
                                )
                            else:
                                self.sendMessage(
                                    message_text='Группы в списке отсутствуют. Нажмите "Добавить" и введите котороткое имя группы (то, что идёт после vk.com/)',
                                    kb=KeyBoard.create(kb["control"]),
                                )
                        case "Ключевые слова":
                            self.states.setState("keywords_control")
                            keywords = self.getKeywordList()
                            if keywords != []:
                                self.sendMessage(
                                    message_text=f"Текущий список ключевых слов:\n{str(keywords)}",
                                    kb=KeyBoard.create(kb["control"]),
                                )
                            else:
                                self.sendMessage(
                                    message_text="Ключевые слова отсутствуют. Давайте добавим",
                                    kb=KeyBoard.create(kb["control"]),
                                )
                        case "Добавить":
                            match self.states.getState():
                                case "groups_control":
                                    self.states.setState("add_group")
                                    self.sendMessage(
                                        message_text="Введите название группы",
                                        kb=KeyBoard.create(kb["discard"]),
                                    )
                                case "keywords_control":
                                    self.states.setState("add_keyword")
                                    self.sendMessage(
                                        message_text="Введите ключевое слово",
                                        kb=KeyBoard.create(kb["discard"]),
                                    )
                        case "Удалить":
                            match self.states.getState():
                                case "groups_control":
                                    self.states.setState("delete_group")
                                    self.sendMessage(
                                        message_text="Введите название группы",
                                        kb=KeyBoard.create(kb["discard"]),
                                    )
                                case "keywords_control":
                                    self.states.setState("delete_keyword")
                                    self.sendMessage(
                                        message_text="Введите ключевое слово",
                                        kb=KeyBoard.create(kb["discard"]),
                                    )
                        case "Назад":
                            self.states.setState("start")
                            self.sendMessage(
                                message_text="Действие отменено",
                                kb=KeyBoard.create(kb["start"]),
                            )

                        case _:
                            match self.states.getState():
                                case "add_group":
                                    self.addGroupToList(
                                        event.text.replace("https://", "").replace(
                                            "vk.com/", ""
                                        )
                                    )
                                    self.states.setState("groups_control")
                                    groups = self.getGroupList()
                                    if groups != []:
                                        self.sendMessage(
                                            message_text=f"Текущий список групп:\n{str(groups)}",
                                            kb=KeyBoard.create(kb["control"]),
                                        )
                                    else:
                                        self.sendMessage(
                                            message_text='Группы в списке отсутствуют. Нажмите "Добавить" и введите котороткое имя группы (то, что идёт после vk.com/)',
                                            kb=KeyBoard.create(kb["control"]),
                                        )
                                case "add_keyword":
                                    self.addKeywordToList(event.text)
                                    self.states.setState("keywords_control")
                                    keywords = self.getKeywordList()
                                    if keywords != []:
                                        self.sendMessage(
                                            message_text=f"Текущий список ключевых слов:\n{str(keywords)}",
                                            kb=KeyBoard.create(kb["control"]),
                                        )
                                    else:
                                        self.sendMessage(
                                            message_text="Ключевые слова отсутствуют. Давайте добавим",
                                            kb=KeyBoard.create(kb["control"]),
                                        )
                                case "delete_group":
                                    groupName = event.text
                                    groups = self.getGroupList()
                                    self.states.setState("groups_control")
                                    if groupName in groups:
                                        groups.remove(groupName)
                                        with open("parserData/groups.txt", "w") as file:
                                            file.close()
                                        if groups != []:
                                            for group in groups:
                                                self.addGroupToList(group)
                                            self.sendMessage(
                                                message_text=f"Текущий список групп:\n{str(groups)}",
                                                kb=KeyBoard.create(kb["control"]),
                                            )
                                        else:
                                            self.sendMessage(
                                                message_text='Группы в списке отсутствуют. Нажмите "Добавить" и введите котороткое имя группы (то, что идёт после vk.com/)',
                                                kb=KeyBoard.create(kb["control"]),
                                            )
                                    else:
                                        self.sendMessage(
                                            message_text="Ошибка! Проверье правильность написания id группы",
                                            kb=KeyBoard.create(kb["control"]),
                                        )
                                        if groups != []:
                                            self.sendMessage(
                                                message_text=f"Текущий список групп:\n{str(groups)}",
                                                kb=KeyBoard.create(kb["control"]),
                                            )
                                        else:
                                            self.sendMessage(
                                                message_text='Группы в списке отсутствуют. Нажмите "Добавить" и введите котороткое имя группы (то, что идёт после vk.com/)',
                                                kb=KeyBoard.create(kb["control"]),
                                            )
                                case "delete_keyword":
                                    keywordIn = str(event.text)
                                    keywords = self.getKeywordList()
                                    self.states.setState("keywords_control")
                                    if keywordIn in keywords:
                                        keywords.remove(keywordIn)
                                        with open(
                                            "parserData/keywords.txt", "w"
                                        ) as file:
                                            file.close()
                                        if keywords != []:
                                            for keyword in keywords:
                                                self.addKeywordToList(keyword)
                                            self.sendMessage(
                                                message_text=f"Текущий список ключевых слов:\n{str(keywords)}",
                                                kb=KeyBoard.create(kb["control"]),
                                            )
                                        else:
                                            self.sendMessage(
                                                message_text="Ключевые слова отсутствуют. Давайте добавим",
                                                kb=KeyBoard.create(kb["control"]),
                                            )
                                    else:
                                        self.sendMessage(
                                            message_text="Ошибка! Проверье правильность написания ключевого слова",
                                            kb=KeyBoard.create(kb["control"]),
                                        )
                                        if keywords != []:
                                            self.sendMessage(
                                                message_text=f"Текущий список ключевых слов:\n{str(keywords)}",
                                                kb=KeyBoard.create(kb["control"]),
                                            )
                                        else:
                                            self.sendMessage(
                                                message_text="Ключевые слова отсутствуют. Давайте добавим",
                                                kb=KeyBoard.create(kb["control"]),
                                            )

    # Метод для получения списка групп
    def getGroupList(self) -> list:
        if os.path.isfile("parserData/groups.txt"):
            with open("parserData/groups.txt", "r") as file:
                groups = [str(line).replace("\n", "").replace(" ", "") for line in file]
                file.close()
        else:
            groups = []
        return groups

    # Метод для добавления группы в список для парсинга
    def addGroupToList(self, group_domen: str) -> None:
        group_domen = group_domen.replace("\n", "").replace(" ", "")
        if os.path.isfile("parserData/groups.txt"):
            with open("parserData/groups.txt", "a") as file:
                file.write(f"{group_domen}\n")
                file.close()
        else:
            with open("parserData/groups.txt", "w") as file:
                file.write(f"{group_domen}\n")
                file.close()

    # Метод для получения списка ключевых слов
    def getKeywordList(self) -> list:
        if os.path.isfile("parserData/keywords.txt"):
            with open("parserData/keywords.txt", "r") as file:
                keywords = [
                    str(line).replace("\n", "").replace(" ", "") for line in file
                ]
                file.close()
        else:
            keywords = []
        return keywords

    # Метод для добавления ключевого слова в список для парсинга
    def addKeywordToList(self, keyword: str) -> None:
        keyword = keyword.replace("\n", "")
        if os.path.isfile("parserData/keywords.txt"):
            with open("parserData/keywords.txt", "a") as file:
                file.write(f"{keyword}\n")
                file.close()
        else:
            with open("parserData/keywords.txt", "w") as file:
                file.write(f"{keyword}\n")
                file.close()
