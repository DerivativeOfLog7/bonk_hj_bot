import telegram
import telegram.ext
import modules.chat_settings as chat_settings
import modules.strings
import modules.common as common
import modules.sql as sql


async def cmd_help(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/help"""
    if not common.is_group(update.effective_chat):
        await update.effective_chat.send_message(parse_mode=telegram.constants.ParseMode.HTML,
                                                 text=modules.strings.CMD_HELP_TEXT)


async def cmd_privacy(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/privacy"""
    if not common.is_group(update.effective_chat):
        await update.effective_chat.send_message(parse_mode=telegram.constants.ParseMode.HTML,
                                                 text=modules.strings.CMD_PRIVACY_TEXT)


async def generic_command_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """Completely ignore channels and inline queries"""
    if update.effective_chat.type == telegram.constants.ChatType.CHANNEL or update.effective_chat.type == telegram.constants.ChatType.SENDER:
        raise telegram.ext.ApplicationHandlerStop


async def cmd_bonk(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/bonk"""
    if common.is_group(update.effective_chat):
        common.ensure_chat_in_db(update.effective_chat)

        # Get settings for group
        settings = chat_settings.get_group_settings(update.effective_chat, settings=(
            chat_settings.show_help_msgs, chat_settings.announce_top_user))
        chat_show_help_msgs = settings[chat_settings.show_help_msgs.name]
        chat_announce_top_user = settings[chat_settings.announce_top_user.name]

        # Show help message if message isn't a reply and group is set to show help messages
        if update.effective_message.reply_to_message is None:
            if chat_show_help_msgs:
                await update.effective_chat.send_message(reply_to_message_id=update.effective_message.id,
                                                         text="Reply to the horny message using this command")
        else:
            # Get top score and holder to use later if announce new top user is enabled
            if chat_announce_top_user:
                # Since message IDs are incremental and per chat, we can use them to determine if a message is newer without storing timestamps
                top_score = sql.fetchone(f"SELECT COUNT(*) AS bonks_count, user_id, MAX(message_id) AS last_message "
                                         f"FROM bonks "
                                         f"WHERE chat_id = {update.effective_chat.id} "
                                         f"GROUP BY user_id " 
                                         f"ORDER BY bonks_count DESC, last_message ASC "
                                         f"LIMIT 1")
            bonk_user_id = update.effective_message.reply_to_message.from_user.id
            bonk_message_id = update.effective_message.reply_to_message.message_id

            # Bot can't bonk itself
            if update.effective_message.reply_to_message.from_user.id == context.bot.id:
                if chat_show_help_msgs:
                    await update.effective_chat.send_message(reply_to_message_id=update.effective_message.id,
                                                             text="Sorry, I can't bonk myself!")

            # Check if user has already been bonked for that message
            elif sql.fetchone(f"SELECT * "
                              f"FROM bonks "
                              f"WHERE user_id = {bonk_user_id} "
                              f"AND chat_id = {update.effective_chat.id} "
                              f"AND message_id = {bonk_message_id}") is None:

                # Insert bonk and update bonks count for current chat
                sql.run_query_s(f"INSERT INTO bonks "
                                f"VALUES ({bonk_user_id}, {update.effective_chat.id}, {bonk_message_id})")
                res = sql.fetchone(f"SELECT COUNT(*) "
                                   f"FROM bonks "
                                   f"WHERE chat_id = {update.effective_chat.id} "
                                   f"AND user_id = {bonk_user_id}")
                await update.effective_chat.send_message(reply_to_message_id=bonk_message_id,
                                                         text="Bonk! Go to horny jail\n"
                                                              f"You were bonked a total of {res} time{'' if res == 1 else 's'} in this chat")
                # Announce new top user if that's the case
                if chat_announce_top_user and (top_score is None or (res > top_score[0] and top_score[1] != update.effective_message.reply_to_message.from_user.id)):
                    await update.effective_chat.send_message(reply_to_message_id=bonk_message_id,
                                                             text="You're now the horniest user in this chat!")
            elif chat_show_help_msgs:
                await update.effective_chat.send_message(reply_to_message_id=update.effective_message.id,
                                                         text="User was already bonked for this message")
    else:
        await update.effective_chat.send_message(text=modules.strings.GROUPS_ONLY)


async def cmd_erase_data(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/erase_data"""
    # Check if chat is group and user is admin
    if common.is_group(update.effective_chat):
        if await common.is_admin(update.effective_chat, update.effective_user.id):
            # Check if there's data stored about this group
            res = sql.fetchone(f"SELECT * "
                               f"FROM chats "
                               f"WHERE chat_id = {update.effective_chat.id}")
            if res is None:
                await update.effective_chat.send_message(text="ℹ️ There's no data associated to this group")
            else:
                await update.effective_chat.send_message(
                    text="⚠️ Erasing this group's data will reset all bonk counts for all users\n"
                         "Are you sure you want to continue?",
                    reply_markup=modules.chat_settings.erase_data_inline_keyboard)
        elif chat_settings.get_group_settings(update.effective_chat, modules.chat_settings.allow_top_cmd):
            await update.effective_chat.send_message(text=modules.strings.ADMINS_ONLY,
                                                     reply_to_message_id=update.effective_message.id)
    else:
        # Check if there's data stored about this user
        res = sql.fetchone(f"SELECT * "
                           f"FROM bonks "
                           f"WHERE user_id = {update.effective_user.id}")
        if res is None:
            await update.effective_chat.send_message(text="ℹ️ There's no data associated to this user")
        else:
            await update.effective_chat.send_message(
                text="⚠️ Erasing your data will reset all your bonk counts for all groups\n"
                     "Are you sure you want to continue?",
                reply_markup=modules.chat_settings.erase_data_inline_keyboard)


async def cmd_top(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/top"""
    # Check if chat is group and /top is allowed
    if common.is_group(update.effective_chat):
        settings = modules.chat_settings.get_group_settings(update.effective_chat,
                                                            (chat_settings.allow_top_cmd, chat_settings.show_help_msgs))
        if settings[chat_settings.allow_top_cmd.name]:
            tot_chat_bonks = sql.fetchone(f"SELECT COUNT(*) "
                                          f"FROM bonks "
                                          f"WHERE chat_id = {update.effective_chat.id}")
            msg = f"Total number of bonks: {tot_chat_bonks}\n"
            # Get top 10 users
            top10 = sql.run_query_s(f"SELECT COUNT(*) AS bonks_count, user_id, MAX(message_id) AS last_message "
                                    f"FROM bonks "
                                    f"WHERE chat_id = {update.effective_chat.id} "
                                    f"GROUP BY user_id " 
                                    f"ORDER BY bonks_count DESC, last_message ASC "
                                    f"LIMIT 10").fetchall()
            # Check if there's data about this group
            if top10 is None:
                await update.effective_chat.send_message(reply_to_message_id=update.effective_message.id,
                                                         text="ℹ️ Nobody has ever been bonked in this group")
            else:
                # Generate top 10
                for i in range(min(len(top10), 10)):
                    user = (await update.effective_chat.get_member(user_id=top10[i][1])).user
                    username = user.username
                    name = user.name
                    msg += f"{i + 1}. {name if username is None else username}: {top10[i][0]}\n"  # Show first name if user has no username set
                await update.effective_chat.send_message(reply_to_message_id=update.effective_message.id,
                                                         text=msg)
        elif settings[chat_settings.show_help_msgs.name]:
            await update.effective_chat.send_message(reply_to_message_id=update.effective_message.id,
                                                     text="🚫 The administrators have disabled this command")
    else:
        await update.effective_chat.send_message(text=modules.strings.GROUPS_ONLY)


async def cmd_stats(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/stats"""
    # Check if chat is private
    if not common.is_group(update.effective_chat):
        # Get stats
        global_bonks = common.sql.fetchone(f"SELECT COUNT(*) "
                                           f"FROM bonks "
                                           f"WHERE user_id = {update.effective_user.id}")
        most_group_bonks = common.sql.fetchone(f"SELECT COUNT(*) AS count "
                                               f"FROM bonks "
                                               f"WHERE user_id = {update.effective_user.id} "
                                               f"GROUP BY chat_id "
                                               f"ORDER BY count "
                                               f"LIMIT 1")
        if most_group_bonks is None:
            await update.effective_chat.send_message(text="ℹ️ There's no data associated to this user")
        else:
            await update.effective_chat.send_message(text=f"You were bonked a total of {global_bonks} time{'' if global_bonks == 1 else 's'}\n"
                                                          f"Your personal record is {most_group_bonks} time{'' if most_group_bonks == 1 else 's'} in a single chat")


async def cmd_start(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/start"""
    if update.effective_chat.type == telegram.Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Add this bot to a group, and use /bonk every time someone sends an horny message!")


async def cmd_about(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/about"""
    if update.effective_chat.type == telegram.Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       parse_mode=telegram.constants.ParseMode.HTML,
                                       text=modules.strings.CMD_ABOUT_TEXT)
