CMD_PRIVACY_TEXT = """
<b>What data is collected?</b>
1. Unique Telegram user ID of bonked users
2. Unique Telegram chat ID for groups where /bonk or /settings was used
3. IDs of messages am user was bonked for (message IDs are group specific - message #1 in group A is not the same as message #1 in group B)
4. Total number of bonks per user and per chat
IDs by themselves contain little private data regarding the user. This bot doesn't memorize any other personal data (eg: username, name, phone number etc.)
/top pulls usernames and names on the fly using Telegram's APIs without storing them

<b>Why is privacy mode disabled? Are you reading all my group chat messages?</b>
Privacy mode is disabled because if it weren't, the bot wouldn't be even able to know which user was bonked
I'm not reading any of your group chat messages. No data regarding the messages is ever stored, and logging is set to a level that doesn't show details about the messages

<b>I still don't trust you with my data</b>
This project is open source, meaning you can dive in the inner workings and check how it works by yourself, or even self host the bot
Run /about to get to the GitHub page of this bot (or here's a shortcut to the <a href="https://github.com/DerivativeOfLog7/bonk_hj_bot/blob/main/modules/sql.py#L6">SQL structure</a>)

<b>Can I delete the data this bot has stored about me or a group I'm in?</b>
You can erase your data by running /erase_data and confirming
Note however that erasing the data will reset your bonk counts for <i>all</i> group chats
Additionally, a group admin can run the same command in a group, which will reset the bonk counts in that group for all users"""

CMD_HELP_TEXT = """List of commands

<i>Group chat:</i>
<b>/bonk (in reply to a message in a group)</b> - Bonk an user for a horny message
<b>/settings (admins only)</b> - Open group settings in private chat
<b>/erase_data (admins only) - Ask confirmation to delete all data about the group from this bot</b> 
<i>Private chat:</i>
<b>/privacy</b> - See info about which data this bot collects
<b>/erase_data</b> - Ask confirmation to delete all about your user from this 
<b>/about</b> - About this bot and source code"""

CMD_ABOUT_TEXT = """Bot developed and hosted by @DerivativeOfLog7

This bot is <b>open source</b>! (if you want to look at my horrible code)
https://github.com/DerivativeOfLog7/bonk_hj_bot"""

ADMINS_ONLY = "⛔️ Only admins can run this command"
ADMINS_ONLY_ALERT = "⛔️ Only admins can interact with this button"
GROUPS_ONLY = "🚫 This command can only be run in groups"
