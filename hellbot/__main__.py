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
OWNER_ID = int(os.environ.get("OWNER_ID", "0")) # NAYA - Tera Telegram ID

client = TelegramClient(StringSession(HELLBOT_SESSION), APP_ID, API_HASH)
StartTime = time.time()

# Owner mention helper
def OWNER_LINK():
    if OWNER_ID!= 0:
        return f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"
    return f"**{OWNER_NAME}**"

# Shayari Database
SHAYARI_LIST = [
    "Mohabbat ka junoon jab had se badh jata hai,\nDard bhi muskurata hai...",
    "Teri yaadon ka silsila kuch aisa hai,\nRaaton ko neend aati nahi, din me chain milta nahi...",
    "Dil se kheli hai mohabbat maine,\nTabhi to har mod pe tanha hun main...",
    "Zindagi ki raahon me akele chalna seekh lo,\nKyunki yahan har koi matlabi hai...",
    "Tere ishq me main khud ko bhool baitha,\nAb tu hi bata main kahan se laaun khud ko...",
    "Wafa ki umeed kisse karein,\nJab khud apne saaye bhi bewafa nikle...",
    "Khamoshiyon me bhi ek baat hoti hai,\nJo lafzon me kahi nahi ja sakti...",
    "Ishq karna hai to dard sehna seekh lo,\nKyunki yahan har khushi ke badle aansu milte hai..."
]

# Tag Lines Database
TAG_LINES = [
    "Sab log active ho jao 🔥",
    "Kahan mar gaye sab? 😂",
    "Attendance lagao sab 👊",
    "GC me aao jaldi 🏃",
    "Important baat hai suno 📢",
    "Party karni hai aa jao 🎉",
    "Online aao sab jhat se ⚡",
    "Chai peene chale? ☕",
    "Game khelte hai aa jao 🎮",
    "VC join karo sab 🎙️"
]

# Helper
def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

# 1. ALIVE
@client.on(events.NewMessage(pattern=f"\\{HANDLER}alive", outgoing=True))
async def alive(event):
    uptime = get_readable_time(int(time.time() - StartTime))
    await event.edit(f"**🔥 HellBot Userbot V6 🔥**\n\n**Owner:** {OWNER_LINK()}\n**Version:** 6.0\n**Uptime:** `{uptime}`\n**Handler:** `{HANDLER}`\n**Abuse:** `{ABUSE}`")

# 2. PING
@client.on(events.NewMessage(pattern=f"\\{HANDLER}ping", outgoing=True))
async def ping(event):
    start = datetime.now()
    await event.edit("`Pong!`")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await event.edit(f"**🏓 Pong!**\n**Speed:** `{ms}ms`\n**Owner:** {OWNER_LINK()}")

# 3. RESTART
@client.on(events.NewMessage(pattern=f"\\{HANDLER}restart", outgoing=True))
async def restart(event):
    await event.edit("`Restarting...`")
    os.execl(sys.executable, sys.executable, "-m", "hellbot")

# 4. ID
@client.on(events.NewMessage(pattern=f"\\{HANDLER}id", outgoing=True))
async def id_cmd(event):
    reply = await event.get_reply_message()
    if reply:
        await event.edit(f"**User ID:** `{reply.sender_id}`\n**Chat ID:** `{event.chat_id}`\n**Your ID:** `{OWNER_ID}`")
    else:
        await event.edit(f"**Your ID:** `{OWNER_ID}`\n**Chat ID:** `{event.chat_id}`")

# 5. INFO
@client.on(events.NewMessage(pattern=f"\\{HANDLER}info", outgoing=True))
async def info(event):
    reply = await event.get_reply_message()
    user = await event.client.get_entity(reply.sender_id if reply else event.sender_id)
    await event.edit(f"**Info:**\n**Name:** {user.first_name}\n**ID:** `{user.id}`\n**Username:** @{user.username}")

# 6. YT DOWNLOAD
@client.on(events.NewMessage(pattern=f"\\{HANDLER}yt (.*)", outgoing=True))
async def yt_download(event):
    url = event.pattern_match.group(1)
    await event.edit("`Downloading...`")
    try:
        proc = await asyncio.create_subprocess_shell(f'yt-dlp -f "best[ext=mp4]" -o "video.mp4" {url}')
        await proc.communicate()
        await client.send_file(event.chat_id, "video.mp4", caption=f"**Downloaded by {OWNER_LINK()}**")
        os.remove("video.mp4")
        await event.delete()
    except Exception as e:
        await event.edit(f"**Error:** `{e}`")

# 7. TIKTOK
@client.on(events.NewMessage(pattern=f"\\{HANDLER}tiktok (.*)", outgoing=True))
async def tiktok(event):
    url = event.pattern_match.group(1)
    await event.edit("`Downloading TikTok...`")
    try:
        proc = await asyncio.create_subprocess_shell(f'yt-dlp -f "mp4" -o "tiktok.mp4" {url}')
        await proc.communicate()
        await client.send_file(event.chat_id, "tiktok.mp4", caption=f"**By {OWNER_LINK()}**")
        os.remove("tiktok.mp4")
        await event.delete()
    except: await event.edit("`Error`")

# 8. INSTA
@client.on(events.NewMessage(pattern=f"\\{HANDLER}insta (.*)", outgoing=True))
async def insta(event):
    url = event.pattern_match.group(1)
    await event.edit("`Downloading...`")
    try:
        proc = await asyncio.create_subprocess_shell(f'yt-dlp -o "insta.mp4" {url}')
        await proc.communicate()
        await client.send_file(event.chat_id, "insta.mp4", caption=f"**By {OWNER_LINK()}**")
        os.remove("insta.mp4")
        await event.delete()
    except: await event.edit("`Error`")

# 9. STICKER
@client.on(events.NewMessage(pattern=f"\\{HANDLER}sticker", outgoing=True))
async def sticker(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media: return await event.edit("`Reply to image/video`")
    await event.edit("`Making sticker...`")
    await client.send_file(event.chat_id, reply.media, force_document=False)
    await event.delete()

# 10. SHAYARI
@client.on(events.NewMessage(pattern=f"\\{HANDLER}shayari", outgoing=True))
async def shayari(event):
    await event.edit(f"**✨ {OWNER_LINK()} Ki Shayari ✨**\n\n{random.choice(SHAYARI_LIST)}")

# 11. TAGALL
@client.on(events.NewMessage(pattern=f"\\{HANDLER}tagall(.*)", outgoing=True))
async def tagall(event):
    text = event.pattern_match.group(1).strip()
    if not text: text = random.choice(TAG_LINES)
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

# 12. AI CHAT - LINK WALA
@client.on(events.NewMessage(pattern=f"\\{HANDLER}ai (.*)", outgoing=True))
async def ai_chat(event):
    query = event.pattern_match.group(1)
    await event.edit(f"`{OWNER_NAME} soch raha hu...`")
    try:
        url = f"https://api.simsimi.net/v2/?text={query}&lc=hi"
        r = requests.get(url).json()
        if r.get("success"):
            await event.edit(f"**👑 OWNER: {OWNER_LINK()}**\n**❓ Question:** {query}\n**🤖 AI Reply:** {r['success']}")
        else:
            await event.edit(f"**👑 OWNER: {OWNER_LINK()}**\n`AI reply nahi mila`")
    except:
        await event.edit(f"**👑 OWNER: {OWNER_LINK()}**\n`AI error`")

# 13. BAN
@client.on(events.NewMessage(pattern=f"\\{HANDLER}ban", outgoing=True))
async def ban(event):
    reply = await event.get_reply_message()
    if not reply: return await event.edit("`Reply to user`")
    await client.edit_permissions(event.chat_id, reply.sender_id, view_messages=False)
    await event.edit(f"`{OWNER_LINK()} ne ban kiya:` [{reply.sender.first_name}](tg://user?id={reply.sender_id})")

# 14. UNBAN
@client.on(events.NewMessage(pattern=f"\\{HANDLER}unban", outgoing=True))
async def unban(event):
    reply = await event.get_reply_message()
    if not reply: return await event.edit("`Reply to user`")
    await client.edit_permissions(event.chat_id, reply.sender_id, view_messages=True)
    await event.edit(f"`{OWNER_LINK()} ne unban kiya:` [{reply.sender.first_name}](tg://user?id={reply.sender_id})")

# 15. KICK
@client.on(events.NewMessage(pattern=f"\\{HANDLER}kick", outgoing=True))
async def kick(event):
    reply = await event.get_reply_message()
    if not reply: return await event.edit("`Reply to user`")
    await client.kick_participant(event.chat_id, reply.sender_id)
    await event.edit(f"`{OWNER_LINK()} ne kick kiya`")

# 16. MUTE
@client.on(events.NewMessage(pattern=f"\\{HANDLER}mute", outgoing=True))
async def mute(event):
    reply = await event.get_reply_message()
    if not reply: return await event.edit("`Reply to user`")
    await client.edit_permissions(event.chat_id, reply.sender_id, send_messages=False)
    await event.edit(f"`{OWNER_LINK()} ne mute kiya`")

# 17. UNMUTE
@client.on(events.NewMessage(pattern=f"\\{HANDLER}unmute", outgoing=True))
async def unmute(event):
    reply = await event.get_reply_message()
    if not reply: return await event.edit("`Reply to user`")
    await client.edit_permissions(event.chat_id, reply.sender_id, send_messages=True)
    await event.edit(f"`{OWNER_LINK()} ne unmute kiya`")

# 18. PURGE
@client.on(events.NewMessage(pattern=f"\\{HANDLER}purge", outgoing=True))
async def purge(event):
    reply = await event.get_reply_message()
    if not reply: return await event.edit("`Reply to message`")
    msgs = []
    async for msg in client.iter_messages(event.chat_id, min_id=reply.id, max_id=event.id):
        msgs.append(msg.id)
    await client.delete_messages(event.chat_id, msgs)
    await event.respond(f"`{OWNER_LINK()} ne {len(msgs)} messages purge kiye`", delete_in=3)

# 19. DEL
@client.on(events.NewMessage(pattern=f"\\{HANDLER}del", outgoing=True))
async def delete(event):
    reply = await event.get_reply_message()
    if reply: await reply.delete()
    await event.delete()

# 20. SYS
@client.on(events.NewMessage(pattern=f"\\{HANDLER}sys", outgoing=True))
async def sysinfo(event):
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    await event.edit(f"**{OWNER_LINK()}'s Bot Stats**\n**CPU:** `{cpu}%`\n**RAM:** `{ram}%`")

# 21. GOOGLE
@client.on(events.NewMessage(pattern=f"\\{HANDLER}google (.*)", outgoing=True))
async def google(event):
    query = event.pattern_match.group(1)
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    await event.edit(f"**{OWNER_LINK()} searched:**\n[{query}]({url})")

# 22. CALC
@client.on(events.NewMessage(pattern=f"\\{HANDLER}calc (.*)", outgoing=True))
async def calc(event):
    expr = event.pattern_match.group(1)
    try:
        result = eval(expr)
        await event.edit(f"**{OWNER_LINK()}'s Calc:** `{expr} = {result}`")
    except: await event.edit("`Invalid`")

# 23. WEATHER
@client.on(events.NewMessage(pattern=f"\\{HANDLER}weather (.*)", outgoing=True))
async def weather(event):
    city = event.pattern_match.group(1)
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3").text
        await event.edit(f"**{OWNER_LINK()} checked weather:** `{r}`")
    except: await event.edit("`Error`")

# ABUSE COMMANDS
if ABUSE == "ON":
    @client.on(events.NewMessage(pattern=f"\\{HANDLER}spam (.*)", outgoing=True))
    async def spam(event):
        args = event.pattern_match.group(1).split(" ", 1)
        if len(args)!= 2: return await event.edit("`Usage:.spam 10 hello`")
        count, text = int(args[0]), args[1]
        await event.delete()
        for _ in range(count):
            await event.respond(f"{OWNER_LINK()}: {text}")
            await asyncio.sleep(0.3)

    @client.on(events.NewMessage(pattern=f"\\{HANDLER}paste", outgoing=True))
    async def paste(event):
        reply = await event.get_reply_message()
        text = reply.text if reply else event.raw_text.split(" ", 1)[1]
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post("https://nekobin.com/api/documents", json={"content": text}) as r:
                res = await r.json()
                await event.edit(f"**{OWNER_LINK()} pasted:** https://nekobin.com/{res['result']['key']}")

    @client.on(events.NewMessage(pattern=f"\\{HANDLER}eval (.*)", outgoing=True))
    async def evaluate(event):
        cmd = event.pattern_match.group(1)
        try:
            result = eval(cmd)
            await event.edit(f"**{OWNER_LINK()}'s Eval:** `{result}`")
        except Exception as e: await event.edit(f"**Error:** `{e}`")

    @client.on(events.NewMessage(pattern=f"\\{HANDLER}term (.*)", outgoing=True))
    async def terminal(event):
        cmd = event.pattern_match.group(1)
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        result = str(stdout.decode().strip()) + str(stderr.decode().strip())
        await event.edit(f"**{OWNER_LINK()}'s Terminal:**\n`{result}`")

    @client.on(events.NewMessage(pattern=f"\\{HANDLER}loop (.*)", outgoing=True))
    async def loop_cmd(event):
        args = event.pattern_match.group(1).split(" ", 1)
        if len(args)!= 2: return await event.edit("`Usage:.loop 5 hi`")
        count, text = int(args[0]), args[1]
        await event.delete()
        for i in range(count):
            await event.respond(f"{OWNER_LINK()}: {i+1}. {text}")
            await asyncio.sleep(1)

# 28. HELP
@client.on(events.NewMessage(pattern=f"\\{HANDLER}help", outgoing=True))
async def help_cmd(event):
    basic = f"""
**🔥 HellBot V6 - {OWNER_LINK()}'s Bot 🔥**

**Fun:**
`.shayari` - {OWNER_NAME} ki shayari
`.ai <text>` - AI se baat karo
`.tagall <msg>` - Sabko tag karo

**Download:**
`.yt <url>` `.tiktok <url>` `.insta <url>` `.sticker`

**Utility:**
`.alive` `.ping` `.restart` `.id` `.info` `.sys`
`.google <query>` `.calc 2+2` `.weather Delhi`

**Admin:**
`.ban` `.unban` `.kick` `.mute` `.unmute`
`.purge` `.del`
"""
    abuse = """
**Abuse ON:**
`.spam <count> <text>` `.loop <count> <text>`
`.paste` `.eval <code>` `.term <cmd>`
""" if ABUSE == "ON" else "\n**ABUSE=ON karo 5 extra commands ke liye**"
    await event.edit(basic + abuse + f"\n**Owner:** {OWNER_LINK()}\n**Handler:** `{HANDLER}`")

async def main():
    print(f"HellBot Userbot V6 Starting... Owner: {OWNER_NAME}")
    await client.start()
    print("Userbot Started Successfully!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import aiohttp
    asyncio.run(main())
