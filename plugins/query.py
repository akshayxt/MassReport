import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import psutil
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from info import Config, Txt

config_path = Path("config.json")


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'


@Client.on_callback_query()
async def handle_Query(bot: Client, query: CallbackQuery):

    data = query.data

    if data == "help":

        HelpBtn = [
            [InlineKeyboardButton(text='Tᴀʀɢᴇᴛ 🎯', callback_data='targetchnl'), InlineKeyboardButton
                (text='Dᴇʟᴇᴛᴇ Cᴏɴғɪɢ ❌', callback_data='delete_conf')],
            [InlineKeyboardButton(text='Tɢ Aᴄᴄᴏᴜɴᴛs 👥', callback_data='account_config'),
             InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='home')]
        ]

        await query.message.edit(text=Txt.HELP_MSG, reply_markup=InlineKeyboardMarkup(HelpBtn))

    elif data == "server":
        try:
            msg = await query.message.edit(text="__Processing...__")
            currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(
                time.time() - Config.BOT_START_TIME))
            total, used, free = shutil.disk_usage(".")
            total = humanbytes(total)
            used = humanbytes(used)
            free = humanbytes(free)
            cpu_usage = psutil.cpu_percent()
            ram_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            ms_g = f"""<b><u>Bot Status</b></u>

# Uptime: <code>{currentTime}</code>
# CPU Usage: <code>{cpu_usage}%</code>
# RAM Usage: <code>{ram_usage}%</code>
# Total Disk Space: <code>{total}</code>
# Used Space: <code>{used} ({disk_usage}%)</code>
# Free Space: <code>{free}</code> """

            await msg.edit_text(text=ms_g, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='home')]]))
        except Exception as e:
            print('Error on line {}'.format(
                sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    elif data == "about":
        botuser = await bot.get_me()
        await query.message.edit(text=Txt.ABOUT_MSG.format(botuser.username, botuser.username), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='home')]]))

    elif data == "home":
        Btn = [
            [InlineKeyboardButton(text='❗Hᴇʟᴘ', callback_data='help'), InlineKeyboardButton(
                text='🌀Sᴇʀᴠᴇʀ Sᴛᴀᴛs', callback_data='server')],
            [InlineKeyboardButton(text='🌻Uᴘᴅᴀᴛᴇs', url='https://t.me/ALLTYPECC'),
             InlineKeyboardButton(text='🌨️Aʙᴏᴜᴛ', callback_data='about')],
            [InlineKeyboardButton(text='❄️Dᴇᴠᴇʟᴏᴘᴇʀ',
                                  url='https://t.me/RAXX_xt')]
        ]

        await query.message.edit(text=Txt.START_MSG.format(query.from_user.mention), reply_markup=InlineKeyboardMarkup(Btn))

    elif data == "delete_conf":

        if query.from_user.id != Config.OWNER:
            return await query.message.edit("**You're Not Admin To Perform this task ❌**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='help')]]))
            
        btn = [
            [InlineKeyboardButton(text='Yes', callback_data='delconfig-yes')],
            [InlineKeyboardButton(text='No', callback_data='delconfig-no')]
        ]

        await query.message.edit(text="**⚠️ Are you Sure ?**\n\nYou want to delete the Config.", reply_markup=InlineKeyboardMarkup(btn))

    elif data == "targetchnl":

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)

        else:
            return await query.message.edit(text="You didn't make a config yet !\n\n Firstly make config by using /make_config", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='help')]]))

        Info = await bot.get_chat(config['Target'])

        btn = [
            [InlineKeyboardButton(text='Change Target',
                                  callback_data='chgtarget')],
            [InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='help')]
        ]

        text = f"Channel Name :- <code> {Info.title} </code>\nChannel Username :- <code> @{Info.username} </code>\nChannel Chat Id :- <code> {Info.id} </code>"

        await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(btn))

    elif data == "chgtarget":

        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)

            try:
                target = await bot.ask(text=Txt.SEND_TARGET_CHANNEL, chat_id=query.message.chat.id, filters=filters.text, timeout=60)
            except:

                await bot.send_message(query.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /target", reply_to_message_id=target.id)
                return

            ms = await query.message.reply_text("**Please Wait...**", reply_to_message_id=query.message.id)

            group_target_id = target.text
            gi = re.sub("(@)|(https://)|(http://)|(t.me/)",
                        "", group_target_id)

            for account in config['accounts']:
                # Run a shell command and capture its output
                try:

                    process = subprocess.Popen(
                        ["python", f"login.py", f"{gi}",
                            f"{account['Session_String']}"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                except Exception as err:
                    await bot.send_message(msg.chat.id, text=f"<b>ERROR :</b>\n<pre>{err}</pre>")

                # Use communicate() to interact with the process
                stdout, stderr = process.communicate()

                # Get the return code
                return_code = process.wait()

                # Check the return code to see if the command was successful
                if return_code == 0:
                    # Print the output of the command
                    print("Command output:")
                    # Assuming output is a bytes object
                    output_bytes = stdout
                    # Decode bytes to string and replace "\r\n" with newlines
                    output_string = output_bytes.decode(
                        'utf-8').replace('\r\n', '\n')
                    print(output_string)

                else:
                    # Print the error message if the command failed
                    print("Command failed with error:")
                    print(stderr)
                    return await query.message.edit('**Something Went Wrong Kindly Check your Inputs Whether You Have Filled Correctly or Not !**')

            newConfig = {
                "Target": gi,
                "accounts": config['accounts']
            }

            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(newConfig, file, indent=4)

            await ms.edit("**Target Updated ✅**\n\nUse /target to check your target")
        except Exception as e:
            print('Error on line {}'.format(
                sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    elif data.startswith('delconfig'):
        condition = data.split('-')[1]
        try:
            if condition == 'yes':
                os.remove('config.json')
                await query.message.edit("**Successfully Deleted ✅**")
            else:
                await query.message.edit("**You Canceled The Process ❌**")
        except Exception as e:
            await query.message.edit(f"{e}\n\n Error 😵")

    elif data == "account_config":

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)

        else:
            return await query.message.edit(text="You didn't make a config yet !\n\n Firstly make config by using /make_config", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='help')]]))

        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)

        UserInfo = []
        for account in config["accounts"]:
            OwnerUid = account["OwnerUid"]
            OwnerName = account['OwnerName']
            UserInfo.append([InlineKeyboardButton(
                text=f"{OwnerName}", callback_data=f"{OwnerUid}")])

        UserInfo.append([InlineKeyboardButton(
            text='⟸ Bᴀᴄᴋ', callback_data='help')])

        await query.message.edit(text="**The Telegram Account You have Added 👇**", reply_markup=InlineKeyboardMarkup(UserInfo))

    elif int(data) in [userId['OwnerUid'] for userId in (json.load(open("config.json")))['accounts']]:
        accountData = {}
        for account in (json.load(open("config.json")))['accounts']:
            if int(data) == account["OwnerUid"]:
                accountData.update({'Name': account['OwnerName']})
                accountData.update({'UserId': account['OwnerUid']})

        await query.message.edit(text=Txt.ACCOUNT_INFO.format(accountData.get('Name'), accountData.get('UserId')), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='help')]]))
        accountData = {}
