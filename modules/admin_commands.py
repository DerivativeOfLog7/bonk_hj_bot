import telegram.ext

import modules.chat_settings as chat_settings
import modules.common as common
import modules.strings


async def cmd_settings(update: telegram.Update, context: telegram.ext.CallbackContext):
    """/settings"""
    if common.is_group(update.effective_chat):
        common.ensure_chat_in_db(update.effective_chat)
        # Get show_help_msgs for group
        shm = chat_settings.get_group_settings(update.effective_chat, settings=chat_settings.show_help_msgs)
        # Show help message if message isn't a reply and group is set to show help messages
        if await common.is_admin(update.effective_chat, update.effective_user.id):
            await update.effective_chat.send_message(text="🔧 Group settings",
                                                     reply_markup=chat_settings.generate_ilk(update.effective_chat),
                                                     reply_to_message_id=update.effective_message.id)
        elif shm:
            await update.effective_chat.send_message(text=modules.strings.ADMINS_ONLY,
                                                     reply_to_message_id=update.effective_message.id)
    else:
        await update.effective_chat.send_message(text=modules.strings.GROUPS_ONLY)
