from vk_api.keyboard import VkKeyboard


# Класс, возвращающий клавиатуры с помощью методов
class KeyBoard:
    # Метод для создания обычной клавиатуры
    @staticmethod
    def create(buttons: list, one_time: bool = False):
        keyboard = VkKeyboard(one_time=one_time)  # Создание обычной клавиатуры
        for button in buttons:
            if len(button) == 2:
                buttonName, color = (
                    button[0],
                    button[1],
                )  # Разделение названия кнопки и цвета на части
                keyboard.add_button(buttonName, color=color)
            else:
                keyboard.add_line()  # Добавление перехода на новую строку в клавиатуре
        return keyboard

    # Метод для создания одноразовой клавиатуры
    @staticmethod
    def create_onetime(self, buttons):
        return self.create(buttons, one_time=True)
