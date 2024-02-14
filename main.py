from parserBotModule import ParserBot
import os
from threading import Timer

def main():
    # Timer(10, os._exit, [1]).start()
    bot = ParserBot()
    bot.run_long_poll()


if __name__ == "__main__":
    main()
