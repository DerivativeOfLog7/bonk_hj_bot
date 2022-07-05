import typing
import sys
import telegram
import telegram.ext
import config.SECRETS
import config.CONFIG
import modules.common as common
import modules.sql as sql


def is_owners_private_chat(update: telegram.Update) -> bool:
    """Check if update was fired from the owner's private chat with the bot"""
    if update.effective_user.id == config.SECRETS.OWNER_USER_ID and update.effective_chat.type == telegram.constants.ChatType.PRIVATE:
        return True
    else:
        return False


async def cmd_kill(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/kill"""
    if is_owners_private_chat(update):
        await common.send_system_message(
            f"‼️ KILLING BOT ({update.effective_user.username} {update.effective_user.id})", context.bot)
        sql.close_db()
        sys.exit(0)


async def cmd_bot_stats(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/bot_stats"""
    if is_owners_private_chat(update):
        res = []
        res.append(sql.fetchone("SELECT COUNT(*) "
                                "FROM bonks"))
        res.append(sql.fetchone("SELECT COUNT(*) "
                                "FROM chats"))
        res.append(sql.fetchone("SELECT COUNT(*) user_id "
                                "FROM bonks"))

        await update.effective_chat.send_message(parse_mode=telegram.constants.ParseMode.HTML,
                                                 text=f"<b>Total number of bonks:</b> {res[0]}\n"
                                                      f"<b>Total number of groups:</b> {res[1]}\n"
                                                      f"<b>Total number of users bonked:</b> {res[2]}")


async def cmd_get_log_file(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/get_log_file"""
    if is_owners_private_chat(update):
        with open(config.CONFIG.PATH_TO_LOG, "rb") as f:
            await update.effective_chat.send_document(document=f)


async def error_callback(update: typing.Optional[object], context: telegram.ext.CallbackContext):
    """Error handler"""
    await common.send_system_message(f"❗️️ AN ERROR HAS OCCURRED!\n"
                                     f"{context.error}\n", context.bot)
    raise context.error
