import logging
import modules.base

try:
    from telegram import Update, error, constants, Message
    from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, filters
except ModuleNotFoundError:
    modules.base.die("Make sure you have installed the python-telegram-bot library (v20)!\n"
                     "https://docs.python-telegram-bot.org/en/v20.0a0/index.html#installing", 3)

try:
    import config.SECRETS
    import config.CONFIG
except ModuleNotFoundError:
    modules.base.die("Make sure you renamed the config directory!", 2)

if config.SECRETS.OWNER_USER_ID is None or config.SECRETS.SYSTEM_MESSAGES_CHANNEL_ID is None:
    modules.base.die("Config error\n"
                     "Make sure you set all values in ./config/SECRETS.py!")


import modules.common
from modules.admin_commands import *
from modules.owner_commands import *
from modules.user_commands import *


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
    filename=config.CONFIG.PATH_TO_LOG
)


def main():
    try:
        application = ApplicationBuilder().token(config.SECRETS.TOKEN).build()
    except error.InvalidToken:
        modules.base.die("Invalid bot token\n"
                         "Make sure you entered your token in ./config/SECRETS.py!", 4)

    handlers = {0: [MessageHandler(filters.COMMAND, generic_command_handler)],
                1: [CommandHandler('start', cmd_start),
                    CommandHandler("bonk", cmd_bonk),
                    CommandHandler("erase_data", cmd_erase_data),
                    CommandHandler("privacy", cmd_privacy),
                    CommandHandler("help", cmd_help),
                    CommandHandler("stats", cmd_stats),
                    CommandHandler("settings", cmd_settings),
                    CommandHandler("top", cmd_top),
                    CommandHandler("bot_stats", cmd_bot_stats),
                    CommandHandler("kill", cmd_kill),
                    CommandHandler("get_log_file", cmd_get_log_file),
                    CallbackQueryHandler(modules.common.callbackquery_handler)
                    ]}
    application.add_error_handler(callback=error_callback)
    application.add_handlers(handlers)
    application.run_polling()


if __name__ == '__main__':
    main()
