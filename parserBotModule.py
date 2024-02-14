import configparser  # Импорт модуля для работы с конфигурационными файлами
import json  # Импорт модуля для работы с JSON данными
import logging  # Импорт моля для логирования
import os  # Импорт модуля для работы с операционной системой
from threading import Timer, Thread  # Импорт модуля для работы с потоками
import requests  # Импорт модуля для работы с HTTP запросами
import time  # Импорт модуля для работы с временем
from longpollBot import LongPollBot  # Импорт класса LongPollBot

config = configparser.ConfigParser()
config.read("config.ini")

loggerParser = logging.getLogger(__name__)
loggerParser.setLevel(logging.INFO)
handler_parser = logging.FileHandler(f"logs/{__name__}.log", mode="w")
formatter_parser = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler_parser.setFormatter(formatter_parser)
loggerParser.addHandler(handler_parser)


class ParserBot(LongPollBot):
    user_access_token = config.get("DEFAULT", "USER_ACCESS_TOKEN")

    def __init__(self):
        super().__init__()
        loggerParser.info("Парсер бот инициализируется")
        # Создание расписания отправки сообщений
        Timer(60, self.sendNewParsedPosts).start()

    def sendNewParsedPosts(self) -> None:
        groups = self.getGroupList
        if groups != []:
            for group in groups:
                self.parsePosts(group)
                time.sleep(0.5)
                loggerParser.debug(f"Парсинг группы {group}")
            loggerParser.info("Автоматический парсинг записей завершён")

    # Парсинг постов
    def parsePosts(self, group_domen: str) -> None:
        try:
            keywords = self.getKeywordList()
            url = f"https://api.vk.com/method/wall.get?domain={group_domen}&count=10&access_token={self.user_access_token}&v=5.199"
            req = requests.get(url)
            src = req.json()
            if os.path.exists(f"parserData/groups/{group_domen}"):
                loggerParser.debug(f"Директория с именем {group_domen} уже существует!")
            else:
                os.mkdir(f"parserData/groups/{group_domen}")

            # сохраняем данные в json файл, чтобы видеть структуру
            with open(
                f"parserData/groups/{group_domen}/{group_domen}.json",
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(src, file, indent=4, ensure_ascii=False)

            # собираем ID новых постов в список
            fresh_posts_id = []
            posts = src["response"]["items"]

            for fresh_post_id in posts:
                fresh_post_id = fresh_post_id["id"]
                fresh_posts_id.append(fresh_post_id)

            # Проверка, если файла не существует, значит это первый
            # парсинг группы(отправляем все новые посты). Иначе начинаем
            # проверку и отправляем только новые посты.

            if not os.path.exists(
                f"parserData/groups/{group_domen}/exist_posts_{group_domen}.txt"
            ):
                loggerParser.info("Файла с ID постов не существует, создаём файл!")

                with open(
                    f"parserData/groups/{group_domen}/exist_posts_{group_domen}.txt",
                    "w",
                ) as file:
                    for item in fresh_posts_id:
                        file.write(str(item) + "\n")
                for post in posts:
                    if post["text"] != "":
                        if keywords != []:
                            if any(
                                kw.lower() in post["text"].lower() for kw in keywords
                            ):
                                self.sendPost(post, group_domen)
                    else:
                        self.sendPost(post, group_domen)
            else:  # перенести значения из exist в last
                with open(
                    f"parserData/groups/{group_domen}/last_posts_{group_domen}.txt", "w"
                ) as f_last:
                    with open(
                        f"parserData/groups/{group_domen}/exist_posts_{group_domen}.txt",
                        "r",
                    ) as f_exist:
                        lines = f_exist.readlines()
                        last_ids = []
                        for line in lines:
                            last_ids.append(str(int(line.strip())))
                        f_last.writelines(lines)
                with open(
                    f"parserData/groups/{group_domen}/exist_posts_{group_domen}.txt",
                    "w",
                ) as file:
                    for item in fresh_posts_id:
                        file.write(str(item) + "\n")
                for post in posts:
                    if post["text"] != "" and not any(
                        post_id == str(post["id"]) for post_id in last_ids
                    ):
                        if keywords != []:
                            if any(
                                kw.lower() in post["text"].lower() for kw in keywords
                            ):
                                self.sendPost(post, group_domen)
                    else:
                        self.sendPost(post, group_domen)
        except Exception as ex:
            loggerParser.error(f"Парсинг группы не выполнен. Ошибка: {ex}")

    # Отправка нового поста
    def sendPost(self, post, domain) -> None:
        if int(post["from_id"]) < 0:
            self.sendMessage(
                message_text=f"&#127381;Новый пост!\n&#128101;Группа: @{domain}\n&#128279;Ссылка: https://vk.com/wall-{abs(int(post['owner_id']))}_{post['id']}\n&#128172;Текст:\n~~~\n{post['text']}\n~~~\nАвтор: vk.com/{domain}"
            )
        else:
            self.sendMessage(
                message_text=f"&#127381;Новый пост!\n&#128101;Группа: @{domain}\n&#128279;Ссылка: https://vk.com/wall-{abs(int(post['owner_id']))}_{post['id']}\n&#128172;Текст:\n~~~\n{post['text']}\n~~~\nАвтор: vk.com/{post['from_id']}"
            )
        loggerParser.debug("Запись отправлена")
