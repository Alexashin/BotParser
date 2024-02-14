import configparser
import vk_api
from vk_api.utils import get_random_id
import logging


loggerBotCore = logging.getLogger(__name__)
loggerBotCore.setLevel(logging.INFO)
handler_botCore = logging.FileHandler(f"logs/{__name__}.log", mode="w")
formatter_botCore = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler_botCore.setFormatter(formatter_botCore)
loggerBotCore.addHandler(handler_botCore)

# Чтение конфига
config = configparser.ConfigParser()
config.read("config.ini")


class BotCore:
    vk_session = None
    vk_api_access = None
    authorized = False
    group_token = config.get("DEFAULT", "BOT_GROUP_TOKEN")
    owner_id = config.getint("DEFAULT", "USER_ID")

    # Инициализация бота
    def __init__(self) -> None:
        loggerBotCore.info("Ядро бота инициализируется")
        self.vk_api_access = self.doAuth(self.group_token)
        if self.vk_api_access is not None:
            self.authorized = True

    # Авторизация пользователя
    def doAuth(self, token: str) -> any:
        try:
            self.vk_session = vk_api.VkApi(token=token)
            loggerBotCore.info("Сессия бота создана")
            return self.vk_session.get_api()
        except Exception as ex:
            loggerBotCore.error(f"Сессия бота не создана. Ошибка: {ex}")
            return None

    # Отправка сообщения
    def sendMessage(self, message_text: str, kb=None) -> None:
        if not self.authorized:
            loggerBotCore.error("Нет авторизации. Проверьте работоспособность токена")
            return
        try:
            if kb != None:
                self.vk_api_access.messages.send(
                    user_id=self.owner_id,
                    message=message_text,
                    random_id=get_random_id(),
                    keyboard=kb.get_keyboard(),
                )
            else:
                self.vk_api_access.messages.send(
                    user_id=self.owner_id,
                    message=message_text,
                    random_id=get_random_id(),
                )
            loggerBotCore.debug(f"Отправлено сообщение: {message_text}")
        except Exception as ex:
            loggerBotCore.error(f"Сообщение не отправлено. Ошибка: {ex}")
