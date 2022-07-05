from __future__ import annotations
import collections
import telegram
import modules.common
import modules.sql as sql
import copy
from typing import Union

Setting = collections.namedtuple("Setting", "name text")

allow_top_cmd = Setting("allow_top_cmd", "Allow /top")
show_help_msgs = Setting("show_help_msgs", "Show help/error messages")
announce_top_user = Setting("announce_top_user", "Announce new top #1 user")

group_settings_list = (allow_top_cmd, show_help_msgs, announce_top_user)
_group_settings_cache = {}

_ilk_settings_default_buttons = []
for index, value in enumerate(group_settings_list):
    _ilk_settings_default_buttons.append([telegram.InlineKeyboardButton(text=f"@ {value.text}", callback_data=f"s@{index}@")])
del index, value

erase_data_inline_keyboard = telegram.InlineKeyboardMarkup(
    [[telegram.InlineKeyboardButton(text="Yes, I'm sure", callback_data="e"),
      telegram.InlineKeyboardButton(text="Nevermind", callback_data="c")]])


def ensure_chat_settings_in_cache(chat: telegram.Chat) -> None:
    """Ensure chat settings are in cache"""
    modules.common.ensure_chat_in_db(chat)
    try:
        _group_settings_cache[chat.id]
    except KeyError:
        _group_settings_cache[chat.id] = {}
        for i in group_settings_list:
            _group_settings_cache[chat.id][i.name] = bool(int(sql.fetchone(f"SELECT {i.name} "
                                                                           f"FROM chats "
                                                                           f"WHERE chat_id = {chat.id}")))


def get_group_settings(chat: telegram.Chat, settings: Union[None, Setting, tuple[Setting]] = None) -> Union[bool, dict[str: bool]]:
    """Get settings from specific group
    Returns bool for a single setting
    Returns dictionary as 'setting_name': bool for multiple settings"""
    ensure_chat_settings_in_cache(chat)

    res = {}
    if settings is None:
        for i in group_settings_list:
            res[i.name] = _group_settings_cache[chat.id][i.name]
    elif isinstance(settings, Setting):
        res = _group_settings_cache[chat.id][settings.name]
    elif isinstance(settings, tuple):
        for i in settings:
            res[i.name] = _group_settings_cache[chat.id][i.name]
    else:
        raise TypeError("Invalid settings type")

    return res


def set_group_setting(chat: telegram.Chat, settings: Union[None, Setting, tuple[Setting]], value: bool) -> None:
    """Set a single group setting"""
    ensure_chat_settings_in_cache(chat)
    _group_settings_cache[chat.id][settings.name] = value
    sql.run_query_s(f"UPDATE chats "
                    f"SET {settings.name} = {value} "
                    f"WHERE chat_id = {chat.id} ")


def generate_ilk(chat: telegram.Chat) -> telegram.InlineKeyboardMarkup:
    """Generate settings InlineKeyboardMarkup"""
    ensure_chat_settings_in_cache(chat)
    chat_settings = get_group_settings(chat)
    ilk = copy.deepcopy(_ilk_settings_default_buttons)
    for index, value in enumerate(group_settings_list):
        ilk[index][0].text = f"{'✅' if chat_settings[value.name] else '❌'}{ilk[index][0].text[1:]}"
        ilk[index][0].callback_data += "0" if chat_settings[value.name] else "1"

    ilk.append([telegram.InlineKeyboardButton(text="Done", callback_data="c")])
    return telegram.InlineKeyboardMarkup(ilk)
