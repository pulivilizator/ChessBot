from aiogram.types import BotCommand
from aiogram import Bot
from lexicon import lexicon


async def set_menu_button(bot: Bot) -> None:
    menu_commands = [BotCommand(command=com, description=descr)
                     for com, descr in lexicon.LEXICON_COMMANDS_MENU.items()]
    await bot.set_my_commands(commands=menu_commands)
