import config.CONFIG
import config.SECRETS
import modules.chat_settings as chat_settings
import modules.sql as sql
import modules.strings as strings
import telegram
import telegram.ext


def is_group(chat: telegram.Chat) -> bool:
    """Return true if chat is group or super group"""
    if chat.type == telegram.constants.ChatType.GROUP or chat.type == telegram.constants.ChatType.SUPERGROUP:
        return True
    else:
        return False


def ensure_chat_in_db(chat: telegram.Chat) -> None:
    """Insert chat in database if not already present"""
    sql.run_query_s(f"INSERT OR IGNORE INTO chats(chat_id) "
                    f"VALUES ({chat.id})")


async def is_admin(chat: telegram.Chat, user_id: int):
    """Check if user is admin of specific chat"""
    user_status = (await chat.get_member(user_id)).status
    if user_status == telegram.constants.ChatMemberStatus.ADMINISTRATOR or user_status == telegram.constants.ChatMemberStatus.OWNER:
        return True
    else:
        return False


async def callbackquery_handler(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """CallbackQuery handler"""
    # Data erasure requests
    if update.callback_query.data == "e":
        if is_group(update.effective_chat):
            if await is_admin(update.effective_chat, update.effective_user.id):
                sql.run_query_s((f"DELETE FROM bonks "
                                 f"WHERE chat_id = {update.effective_chat.id}",
                                 f"DELETE FROM chats "
                                 f"WHERE chat_id = {update.effective_chat.id}"))
                await update.effective_message.edit_reply_markup(reply_markup=None)
                await update.effective_message.edit_text(text="🗑 The data has been deleted")
            else:
                await update.callback_query.answer(text=strings.ADMINS_ONLY_ALERT, show_alert=True)
        else:
            sql.run_query_s("DELETE FROM bonks "
                            f"WHERE user_id = {update.effective_user.id}")
            await update.effective_message.edit_reply_markup(reply_markup=None)
            await update.effective_message.edit_text(text="🗑 Your data has been deleted")

    # Done / nevermind button
    elif update.callback_query.data == "c":
        if is_group(update.effective_chat):
            if await is_admin(update.effective_chat, update.effective_user.id):
                await update.callback_query.message.delete()
            else:
                await update.callback_query.answer(text=strings.ADMINS_ONLY_ALERT, show_alert=True)
        else:
            await update.callback_query.message.delete()

    #/settings buttons
    elif "s@" in update.callback_query.data:
        if await is_admin(update.effective_chat, update.effective_user.id):
            split = update.callback_query.data.split("@")
            chat_settings.set_group_setting(update.effective_chat, chat_settings.group_settings_list[int(split[1])],
                                            bool(int(split[2])))
            await update.effective_message.edit_reply_markup(chat_settings.generate_ilk(update.effective_chat))
        else:
            await update.callback_query.answer(text=strings.ADMINS_ONLY_ALERT, show_alert=True)


async def send_system_message(msg: str, app: telegram.Bot) -> None:
    """Send message to system messages channel"""
    await app.send_message(chat_id=config.SECRETS.SYSTEM_MESSAGES_CHANNEL_ID,
                           parse_mode=telegram.constants.ParseMode.HTML,
                           text=msg)


async def generic_message(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """Completely ignore channels"""
    if update.effective_chat.type == telegram.Chat.CHANNEL:
        raise telegram.ext.ApplicationHandlerStop
