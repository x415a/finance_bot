from telebot import TeleBot
import fin_bot
import bot_funcs
import tables


def main(bots_list: list[TeleBot]):
    for th in [tables.get_autoupdate_thread()] + [bot_funcs.start_bot(b) for b in bots_list]:
        th.join()


if __name__ == '__main__':
    bots = [fin_bot.get_bot()]
    main(bots)
