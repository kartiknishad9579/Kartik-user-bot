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

client = TelegramClient(StringSession(HELLBOT_SESSION), APP_ID, API_HASH)
StartTime = time.time()

# Owner mention helper
def OWNER_LINK():
    if OWNER_ID!= 0:
        return f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"
    return f"**{OWNER_NAME}**"

# NAYA HELPER - Reply wale ko tag karega
async def get_mention(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
        name = user.first_name if user.first_name else "User"
        return f"[{name}](tg://user?id={user.id})"
    return OWNER_LINK()

# Shayari Database
SHAYARI_LIST = [
    "Mohabbat ka junoon jab had se badh jata hai,\nDard bhi muskurata hai...",
    "Teri yaadon ka silsila kuch aisa hai,\nRaaton ko neend aati nahi, din me chain milta nahi...",
    "Dil se kheli hai mohabbat maine,\nTabhi to har mod pe tanha hun main...",
    "Zindagi ki raahon me akele chalna seekh lo,\nKyunki yahan har koi matlabi hai..."
]

# Tag Lines Database
TAG_LINES = [
    "Sab log active ho jao 🔥", "Kahan mar gaye sab? 😂", "Attendance lagao sab 👊",
    "GC me aao jaldi 🏃", "Important baat hai suno 📢", "Party karni hai aa jao 🎉"
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
        if seconds == 0 and remainder == 0: break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)): time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4: up_time += f"{time_list.pop()}, "
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

# 3. TAGALL - Purana wala
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

# 4. ALL - NAYA COMMAND - Reply + All Tag
@client.on(events.NewMessage(pattern=f"\\{HANDLER}all(.*)", outgoing=True))
async def all_tag(event):
    text = event.pattern_match.group(1).strip()
    if not text and event.is_reply:
        reply = await event.get_reply_message()
        text = reply.text
    if not text: return await event.edit(f"`Usage: {HANDLER}all <text>` ya kisi msg ko reply karke `.all`")
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

# 5. SHAYARI
@client.on(events.NewMessage(pattern=f"\\{HANDLER}shayari", outgoing=True))
async def shayari(event):
    await event.edit(f"**✨ {OWNER_LINK()} Ki Shayari ✨**\n\n{random.choice(SHAYARI_LIST)}")

# 6. ID
@client.on(events.NewMessage(pattern=f"\\{HANDLER}id", outgoing=True))
async def id_cmd(event):
    reply = await event.get_reply_message()
    if reply:
        await event.edit(f"**User ID:** `{reply.sender_id}`\n**Chat ID:** `{event.chat_id}`")
    else:
        await event.edit(f"**Your ID:** `{OWNER_ID}`\n**Chat ID:** `{event.chat_id}`")

# 7. RESTART
@client.on(events.NewMessage(pattern=f"\\{HANDLER}restart", outgoing=True))
async def restart(event):
    await event.edit("`Restarting...`")
    os.execl(sys.executable, sys.executable, "-m", "hellbot")

# 8. SYS
@client.on(events.NewMessage(pattern=f"\\{HANDLER}sys", outgoing=True))
async def sysinfo(event):
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    await event.edit(f"**{OWNER_LINK()}'s Bot Stats**\n**CPU:** `{cpu}%`\n**RAM:** `{ram}%`")

# ABUSE COMMANDS
if ABUSE == "ON":
    @client.on(events.NewMessage(pattern=f"\\{HANDLER}spam (.*)", outgoing=True))
    async def spam(event):
        args = event.pattern_match.group(1).split(" ", 1)
        if len(args)!= 2: return await event.edit(f"`Usage: {HANDLER}spam 10 hello`")
        count, text = int(args[0]), args[1]
        mention = await get_mention(event) # CHANGE KIYA
        await event.delete()
        for _ in range(count):
            await event.respond(f"{mention}: {text}")
            await asyncio.sleep(0.3)

    @client.on(events.NewMessage(pattern=f"\\{HANDLER}loop (.*)", outgoing=True))
    async def loop_cmd(event):
        args = event.pattern_match.group(1).split(" ", 1)
        if len(args)!= 2: return await event.edit(f"`Usage: {HANDLER}loop 5 hi`")
        count, text = int(args[0]), args[1]
        mention = await get_mention(event) # CHANGE KIYA
        await event.delete()
        for i in range(count):
            await event.respond(f"{mention}: {i+1}. {text}")
            await asyncio.sleep(1)

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

# HELP
@client.on(events.NewMessage(pattern=f"\\{HANDLER}help", outgoing=True))
async def help_cmd(event):
    basic = f"""
**🔥 HellBot V6 - {OWNER_LINK()}'s Bot 🔥**

**Tag Commands:**
`.tagall <msg>` - Sabko tag + apna msg
`.all <msg>` - Sabko tag. Reply msg bhi chalega

**Fun:**
`.shayari`
`.spam <count> <text>` - Reply wale ko tag karke spam
`.loop <count> <text>` - Reply wale ko tag karke loop

**Utility:**
`.alive` `.ping` `.restart` `.id` `.sys`
"""
    abuse = """
**Abuse ON:**
`.paste` `.eval <code>` `.term <cmd>`
""" if ABUSE == "ON" else "\n**ABUSE=ON karo extra commands ke liye**"
    await event.edit(basic + abuse + f"\n**Owner:** {OWNER_LINK()}\n**Handler:** `{HANDLER}`")

async def main():
    print(f"HellBot Userbot V6 Starting... Owner: {OWNER_NAME}")
    await client.start()
    print("Userbot Started Successfully!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
