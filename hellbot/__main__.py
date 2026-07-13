import os
import asyncio
import time
import sys
import psutil
import requests
import random
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import User

# Config
APP_ID = int(os.environ.get("APP_ID"))
API_HASH = os.environ.get("API_HASH")
HELLBOT_SESSION = os.environ.get("HELLBOT_SESSION")
HANDLER = os.environ.get("HANDLER", ".")
ABUSE = os.environ.get("ABUSE", "OFF").upper()
OWNER_NAME = os.environ.get("OWNER_NAME", "OWNER")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
AUTO_REPLY_MSG = os.environ.get("AUTO_REPLY_MSG", f"**{OWNER_NAME} abhi busy hai**\n**Thodi der me reply dunga** 😊")
WELCOME_MSG = os.environ.get("WELCOME_MSG", "**Welcome {name} to {chat}** 🔥\n**Total Members:** {count}")

client = TelegramClient(StringSession(HELLBOT_SESSION), APP_ID, API_HASH)
StartTime = time.time()
PM_WARNS = {}

def OWNER_LINK():
    if OWNER_ID != 0:
        return f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"
    return f"**{OWNER_NAME}**"

async def get_mention(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
        name = user.first_name if user.first_name else "User"
        return f"[{name}](tg://user?id={user.id})"
    return OWNER_LINK()

# ====== DP WALA WELCOME SYSTEM ======
@client.on(events.ChatAction)
async def welcome(event):
    if event.user_joined or event.user_added:
        user = await event.get_user()
        chat = await event.get_chat()
        name = user.first_name or "User"
        mention = f"[{name}](tg://user?id={user.id})"
        chat_name = chat.title
        count = await client.get_participants(chat, limit=0)
        
        msg = WELCOME_MSG.format(name=mention, chat=chat_name, owner=OWNER_LINK(), count=len(count))
        
        try:
            user_photo = await client.download_profile_photo(user, file="user_dp.jpg")
            chat_photo = await client.download_profile_photo(chat, file="chat_dp.jpg")
            files_to_send = [f for f in [user_photo, chat_photo] if f]
            
            if files_to_send:
                await client.send_file(event.chat_id, files_to_send, caption=msg)
                for f in files_to_send:
                    if os.path.exists(f): os.remove(f)
            else:
                await client.send_message(event.chat_id, msg)
        except:
            await client.send_message(event.chat_id, msg)

@client.on(events.NewMessage(pattern=f"\\{HANDLER}setwelcome (.*)", outgoing=True))
async def set_welcome(event):
    global WELCOME_MSG
    new_msg = event.pattern_match.group(1)
    WELCOME_MSG = new_msg
    await event.edit(f"`Welcome message set ho gaya!`\n\n**New Msg:** {new_msg}\n\n**Vars:** `{{name}}` `{{chat}}` `{{owner}}` `{{count}}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}welcome", outgoing=True))
async def check_welcome(event):
    await event.edit(f"**Current Welcome Msg:**\n`{WELCOME_MSG}`\n\n**Vars:** `{{name}}` `{{chat}}` `{{owner}}` `{{count}}`")
# ====== WELCOME END ======


# ====== AUTO REPLY ======
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if event.is_private and not event.out and not event.sender_id == OWNER_ID:
        sender = await event.get_sender()
        if sender.id not in PM_WARNS:
            PM_WARNS[sender.id] = 1
            await asyncio.sleep(2)
            await event.reply(AUTO_REPLY_MSG)
        await asyncio.sleep(300)
        if sender.id in PM_WARNS: del PM_WARNS[sender.id]

@client.on(events.NewMessage(outgoing=True))
async def pmpermit_off(event):
    if event.is_private:
        chat = await event.get_chat()
        if chat.id in PM_WARNS: del PM_WARNS[chat.id]

# ====== MUSIC - FIXED ======
@client.on(events.NewMessage(pattern=f"\\{HANDLER}play (.*)", outgoing=True))
async def playmusic(event):
    query = event.pattern_match.group(1)
    msg = await event.edit(f"`🔍 Searching: {query}`")
    try:
        proc = await asyncio.create_subprocess_shell(
            f'yt-dlp -x --audio-format mp3 -o "song.%(ext)s" --no-playlist "ytsearch1:{query}"')
        await proc.communicate()
        
        if not os.path.exists("song.mp3"):
            return await msg.edit("`❌ Song download nahi hua`\n`Check: ffmpeg + yt-dlp installed?`")
            
        await msg.edit("`📤 Uploading song...`")
        await client.send_file(event.chat_id, "song.mp3", caption=f"**🎵 Playing:** `{query}`", supports_streaming=True)
        os.remove("song.mp3")
        await event.delete()
    except Exception as e: 
        await msg.edit(f"**Error:** `{e}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}vplay (.*)", outgoing=True))
async def playvideo(event):
    query = event.pattern_match.group(1)
    msg = await event.edit(f"`🔍 Searching: {query}`")
    try:
        proc = await asyncio.create_subprocess_shell(
            f'yt-dlp -f "best[ext=mp4]" -o "video.mp4" --no-playlist "ytsearch1:{query}"')
        await proc.communicate()
        
        if not os.path.exists("video.mp4"):
            return await msg.edit("`❌ Video download nahi hua`")
            
        await msg.edit("`📤 Uploading video...`")
        await client.send_file(event.chat_id, "video.mp4", caption=f"**🎬 Playing:** `{query}`", supports_streaming=True)
        os.remove("video.mp4")
        await event.delete()
    except Exception as e: 
        await msg.edit(f"**Error:** `{e}`")

# TAGALL
@client.on(events.NewMessage(pattern=f"\\{HANDLER}tagall(.*)", outgoing=True))
async def tagall(event):
    text = event.pattern_match.group(1).strip()
    if not text: text = "Sab log active ho jao 🔥"
    await event.edit(f"`{OWNER_NAME} tagging all members...`")
    mentions = []
    async for user in client.iter_participants(event.chat_id):
        if user.bot or user.deleted: continue
        mentions.append(f"[{user.first_name}](tg://user?id={user.id})")
    chunk = [mentions[i:i+5] for i in range(0, len(mentions), 5)]
    for c in chunk:
        await event.respond(f"**{OWNER_LINK()}:** {text}\n\n{' '.join(c)}")
        await asyncio.sleep(2)
    await event.delete()

# ALL
@client.on(events.NewMessage(pattern=f"\\{HANDLER}all(.*)", outgoing=True))
async def all_tag(event):
    text = event.pattern_match.group(1).strip()
    if not text and event.is_reply:
        reply = await event.get_reply_message()
        text = reply.text
    if not text: return await event.edit(f"`Usage: {HANDLER}all <text>`")
    await event.edit("`Tagging all...`")
    mentions = []
    async for user in client.iter_participants(event.chat_id):
        if user.bot or user.deleted: continue
        mentions.append(f"[{user.first_name}](tg://user?id={user.id})")
    chunk = [mentions[i:i+5] for i in range(0, len(mentions), 5)]
    for c in chunk:
        await event.respond(f"**{text}**\n\n{' '.join(c)}")
        await asyncio.sleep(2)
    await event.delete()

# HELP
@client.on(events.NewMessage(pattern=f"\\{HANDLER}help", outgoing=True))
async def help_cmd(event):
    basic = f"""
**🔥 HellBot V6 - {OWNER_LINK()}'s Bot 🔥**

**DP Welcome:** Join pe User DP + Group DP
`.setwelcome <msg>` - Welcome msg set
`.welcome` - Current msg dekho

**Music:** `.play <song>` `.vplay <video>`
**Tag:** `.tagall <text>` `.all <text>`
"""
    await event.edit(basic)

async def main():
    print(f"HellBot Userbot V6 Starting... Owner: {OWNER_NAME}")
    await client.start()
    print("Userbot Started Successfully!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
