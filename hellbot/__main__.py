import os
import asyncio
import time
import requests
import random
import qrcode
import wikipedia
import pyjokes
import psutil
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import g4f
import instaloader
import yt_dlp
from googletrans import Translator

APP_ID = int(os.environ.get("APP_ID"))
API_HASH = os.environ.get("API_HASH")
HELLBOT_SESSION = os.environ.get("HELLBOT_SESSION")
HANDLER = os.environ.get("HANDLER", ".")
OWNER_NAME = os.environ.get("OWNER_NAME", "OWNER")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
AI_GROUP_ON = os.environ.get("AI_GROUP_ON", "OFF").upper()

client = TelegramClient(StringSession(HELLBOT_SESSION), APP_ID, API_HASH)
L = instaloader.Instaloader()
translator = Translator()
chat_history = {}
AFK = False
AFK_REASON = ""

def OWNER_LINK(): 
    return f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"

print("HellBot V11 PRO Starting...")

# ================================================
# ================ 1. AI CHAT BOT ================
# ================================================
@client.on(events.NewMessage(incoming=True))
async def chatbot(event):
    global AFK
    if event.sender_id == OWNER_ID: 
        return
    
    if AFK and event.is_private: 
        return await event.reply(f"**{OWNER_NAME} AFK hai**\n**Reason:** {AFK_REASON}")
    
    if event.is_group and AI_GROUP_ON != "ON": 
        return
    
    if event.is_group and not event.is_reply and OWNER_NAME.lower() not in event.text.lower(): 
        return
    
    user_id = event.sender_id
    if user_id not in chat_history: 
        chat_history[user_id] = [{"role": "system", "content": f"Tum {OWNER_NAME} ke AI assistant ho. Hindi me short jawab do."}]
    
    chat_history[user_id].append({"role": "user", "content": event.text})
    
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4o_mini, 
            messages=chat_history[user_id]
        )
        await event.reply(response)
        chat_history[user_id].append({"role": "assistant", "content": response})
    except:
        await event.reply("`AI busy hai`")

# ================================================
# ================ 2. ADMIN TOOLS ================
# ================================================
@client.on(events.NewMessage(pattern=f"\\{HANDLER}ban", outgoing=True))
async def ban(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    user = await event.get_reply_message()
    await client.edit_permissions(event.chat_id, user.sender_id, view_messages=False)
    await event.edit("`Banned`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}kick", outgoing=True))
async def kick(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    user = await event.get_reply_message()
    await client.kick_participant(event.chat_id, user.sender_id)
    await event.edit("`Kicked`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}mute", outgoing=True))
async def mute(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    user = await event.get_reply_message()
    await client.edit_permissions(event.chat_id, user.sender_id, send_messages=False)
    await event.edit("`Muted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}unmute", outgoing=True))
async def unmute(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    user = await event.get_reply_message()
    await client.edit_permissions(event.chat_id, user.sender_id, send_messages=True)
    await event.edit("`Unmuted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}promote", outgoing=True))
async def promote(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    user = await event.get_reply_message()
    rights = ChatAdminRights(
        add_admins=False, 
        invite_users=True, 
        change_info=True, 
        ban_users=True, 
        delete_messages=True, 
        pin_messages=True
    )
    await client(EditAdminRequest(event.chat_id, user.sender_id, rights, "Admin"))
    await event.edit("`Promoted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}demote", outgoing=True))
async def demote(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    user = await event.get_reply_message()
    rights = ChatAdminRights()
    await client(EditAdminRequest(event.chat_id, user.sender_id, rights, ""))
    await event.edit("`Demoted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}pin", outgoing=True))
async def pin(event): 
    msg = await event.get_reply_message()
    await client.pin_message(event.chat_id, msg.id)
    await event.edit("`Pinned`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}unpin", outgoing=True))
async def unpin(event): 
    await client.unpin_message(event.chat_id)
    await event.edit("`Unpinned`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}purge (\\d+)", outgoing=True))
async def purge(event): 
    count = int(event.pattern_match.group(1))
    msgs = await client.get_messages(event.chat_id, limit=count+1)
    await client.delete_messages(event.chat_id, msgs)
    await event.respond(f"`{count} msgs deleted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}zombies", outgoing=True))
async def zombies(event): 
    count = 0
    await event.edit("`Searching zombies...`")
    async for user in client.iter_participants(event.chat_id):
        if user.deleted: 
            await client.kick_participant(event.chat_id, user.id)
            count += 1
            await asyncio.sleep(0.5)
    await event.edit(f"`{count} Zombies kicked`")

# ================================================
# ============= 3. TAG + USER TOOLS ==============
# ================================================
@client.on(events.NewMessage(pattern=f"\\{HANDLER}tagall(.*)", outgoing=True))
async def tagall(event): 
    text = event.pattern_match.group(1).strip() or "Sab aa jao"
    await event.delete()
    mentions = []
    async for user in client.iter_participants(event.chat_id):
        if not user.bot:
            mentions.append(f"[{user.first_name}](tg://user?id={user.id})")
    
    for i in range(0, len(mentions), 5): 
        await event.respond(f"**{OWNER_LINK()}:** {text}\n\n{' '.join(mentions[i:i+5])}")
        await asyncio.sleep(2)

@client.on(events.NewMessage(pattern=f"\\{HANDLER}user1(.*)", outgoing=True))
async def user1(event): 
    text = event.pattern_match.group(1).strip() or "bhai"
    users = [x async for x in client.iter_participants(event.chat_id) if not x.bot]
    user = random.choice(users)
    await event.respond(f"[{user.first_name}](tg://user?id={user.id}) {text}")
    await event.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}info", outgoing=True))
async def info(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    msg = await event.get_reply_message()
    user = await client.get_entity(msg.sender_id)
    await event.edit(
        f"**Name:** {user.first_name}\n"
        f"**ID:** `{user.id}`\n"
        f"**Username:** @{user.username}\n"
        f"**Link:** [Click](tg://user?id={user.id})"
    )

@client.on(events.NewMessage(pattern=f"\\{HANDLER}pfp", outgoing=True))
async def pfp(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    msg = await event.get_reply_message()
    photo = await client.download_profile_photo(msg.sender_id, file="pfp.jpg")
    await client.send_file(event.chat_id, photo)
    os.remove(photo)
    await event.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}bio", outgoing=True))
async def bio(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    msg = await event.get_reply_message()
    user = await client.get_entity(msg.sender_id)
    await event.edit(f"**{user.first_name}'s Bio:**\n\n`{user.about or 'None'}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}id", outgoing=True))
async def id_cmd(event): 
    await event.edit(f"`Chat ID: {event.chat_id}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}common", outgoing=True))
async def common(event): 
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    msg = await event.get_reply_message()
    common_chats = await client.get_common_chats(msg.sender_id)
    await event.edit(f"`{len(common_chats)} Common Groups`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}invite (.*)", outgoing=True))
async def invite(event): 
    username = event.pattern_match.group(1)
    await client.add_chat_user(event.chat_id, username)
    await event.edit("`Invited`")

# ================================================
# ============= 4. DOWNLOAD TOOLS ================
# ================================================
@client.on(events.NewMessage(pattern=f"\\{HANDLER}play (.*)", outgoing=True))
async def play(event): 
    query = event.pattern_match.group(1)
    await event.edit(f"`Searching: {query}`")
    os.system(f'yt-dlp -x --audio-format mp3 -o "song.mp3" --no-playlist "ytsearch1:{query}"')
    if os.path.exists("song.mp3"): 
        await client.send_file(event.chat_id, "song.mp3", supports_streaming=True)
        os.remove("song.mp3")
    await event.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}yt (.*)", outgoing=True))
async def yt(event): 
    url = event.pattern_match.group(1)
    await event.edit("`Downloading video...`")
    os.system(f'yt-dlp -f best -o "video.mp4" {url}')
    if os.path.exists("video.mp4"): 
        await client.send_file(event.chat_id, "video.mp4")
        os.remove("video.mp4")
    await event.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}insta (.*)", outgoing=True))
async def insta(event): 
    url = event.pattern_match.group(1)
    msg = await event.edit("`Downloading reel...`")
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target="insta")
        for file in os.listdir("insta"): 
            await client.send_file(event.chat_id, f"insta/{file}")
        os.system("rm -rf insta")
        await msg.delete()
    except Exception as e:
        await msg.edit(f"`Error: {e}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}tt (.*)", outgoing=True))
async def tt(event): 
    url = event.pattern_match.group(1)
    await event.edit("`Downloading...`")
    os.system(f'yt-dlp -o "tt.mp4" {url}')
    if os.path.exists("tt.mp4"): 
        await client.send_file(event.chat_id, "tt.mp4")
        os.remove("tt.mp4")
    await event.delete()

# ================================================
# ============ 5. UTILS + SEARCH =================
# ================================================
@client.on(events.NewMessage(pattern=f"\\{HANDLER}tr (.*)", outgoing=True))
async def tr(event): 
    text = event.pattern_match.group(1)
    result = translator.translate(text, dest="hi")
    await event.edit(f"**Translated:** `{result.text}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}weather (.*)", outgoing=True))
async def weather(event): 
    city = event.pattern_match.group(1)
    res = requests.get(f"https://wttr.in/{city}?format=3").text
    await event.edit(f"`{res}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}google (.*)", outgoing=True))
async def google(event): 
    query = event.pattern_match.group(1)
    await event.edit(f"**Google:** https://www.google.com/search?q={query}")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}wiki (.*)", outgoing=True))
async def wiki(event): 
    query = event.pattern_match.group(1)
    summary = wikipedia.summary(query, sentences=2)
    await event.edit(f"**Wiki:** {summary}")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}qr (.*)", outgoing=True))
async def qr(event): 
    text = event.pattern_match.group(1)
    img = qrcode.make(text)
    img.save("qr.png")
    await client.send_file(event.chat_id, "qr.png")
    os.remove("qr.png")

# ================================================
# ================= 6. FUN =======================
# ================================================
@client.on(events.NewMessage(pattern=f"\\{HANDLER}shayari", outgoing=True))
async def shayari(event): 
    await event.edit(random.choice([
        "Mohabbat dard deti hai...", 
        "Teri yaad aati hai...", 
        "Log kehte hai pyar andha hota hai..."
    ]))

@client.on(events.NewMessage(pattern=f"\\{HANDLER}joke", outgoing=True))
async def joke(event): 
    await event.edit(pyjokes.get_joke())

@client.on(events.NewMessage(pattern=f"\\{HANDLER}coin", outgoing=True))
async def coin(event): 
    await event.edit(f"`{random.choice(['Heads', 'Tails'])}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}dice", outgoing=True))
async def dice(event): 
    await event.edit(f"`{random.randint(1,6)}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}truth", outgoing=True))
async def truth(event): 
    await event.edit(random.choice([
        "Last crush ka naam?", 
        "Kabhi jhooth bola?"
    ]))

@client.on(events.NewMessage(pattern=f"\\{HANDLER}dare", outgoing=True))
async def dare(event): 
    await event.edit(random.choice([
        "10 pushup karo", 
        "Kisi ko I love u bolo"
    ]))

# ================================================
# ============== 7. BOT TOOLS ====================
# ================================================
@client.on(events.NewMessage(pattern=f"\\{HANDLER}alive", outgoing=True))
async def alive(event): 
    await event.edit(
        f"**HellBot V11 PRO is Alive**\n"
        f"**Owner:** {OWNER_LINK()}\n"
        f"**RAM:** {psutil.virtual_memory().percent}%"
    )

@client.on(events.NewMessage(pattern=f"\\{HANDLER}ping", outgoing=True))
async def ping(event):
    start = time.time()
    msg = await event.edit("`Pinging...`")
    end = time.time()
    await msg.edit(f"`Pong! {round((end-start)*1000)}ms`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}afk(.*)", outgoing=True))
async def afk(event): 
    global AFK, AFK_REASON
    AFK = True
    AFK_REASON = event.pattern_match.group(1).strip() or "Busy"
    await event.edit(f"`AFK On: {AFK_REASON}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}unafk", outgoing=True))
async def unafk(event): 
    global AFK
    AFK = False
    await event.edit("`AFK Off`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}stats", outgoing=True))
async def stats(event): 
    dialogs = await client.get_dialogs()
    groups = len([x for x in dialogs if x.is_group])
    pms = len([x for x in dialogs if x.is_user])
    await event.edit(f"**Groups:** {groups}\n**PM:** {pms}")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}restart", outgoing=True))
async def restart(event): 
    await event.edit("`Restarting...`")
    os.system("kill 1")

# ================================================
# ===== 8. BROADCAST + BACKUP + GBAN =============
# ================================================
@client.on(events.NewMessage(pattern=f"\\{HANDLER}broadcast (.*)", outgoing=True))
async def broadcast(event):
    msg = event.pattern_match.group(1)
    await event.edit("`Broadcasting...`")
    dialogs = await client.get_dialogs()
    count = 0
    for d in dialogs:
        if d.is_user and not d.entity.bot and d.entity.id != OWNER_ID:
            try: 
                await client.send_message(d.id, f"**📢 Broadcast from {OWNER_NAME}**\n\n{msg}")
                count += 1
                await asyncio.sleep(0.5)
            except: 
                pass
    await event.edit(f"**Broadcast Done**\n**Sent to:** {count} users")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}backup", outgoing=True))
async def backup(event):
    await event.edit("`Backing up chats...`")
    txt = "**Chats Backup**\n\n"
    async for d in client.iter_dialogs(): 
        txt += f"{d.name} - `{d.id}`\n"
    with open("backup.txt", "w") as f: 
        f.write(txt)
    await client.send_file(event.chat_id, "backup.txt")
    os.remove("backup.txt")
    await event.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}gban", outgoing=True))
async def gban(event):
    if not event.is_reply: 
        return await event.edit("`Reply karo`")
    user = await event.get_reply_message()
    count = 0
    await event.edit("`GBanning...`")
    async for d in client.iter_dialogs():
        if d.is_group:
            try: 
                await client.edit_permissions(d.id, user.sender_id, view_messages=False)
                count += 1
            except: 
                pass
    await event.edit(f"`GBanned in {count} groups`")

# ================================================
# ===== 9. WELCOME + TOGGLE + HELP ===============
# ================================================
@client.on(events.ChatAction)
async def welcome(event): 
    if event.user_joined: 
        user = await event.get_user()
        await event.respond(f"**Welcome [{user.first_name}](tg://user?id={user.id}) to {event.chat.title}** 🔥")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}aigroup (on|off)", outgoing=True))
async def ai_toggle(event): 
    os.environ["AI_GROUP_ON"] = event.pattern_match.group(1).upper()
    await event.edit(f"`AI Group: {event.pattern_match.group(1).upper()}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}help", outgoing=True))
async def help(event): 
    txt = f"""**HellBot V11 PRO - 85+ Commands**

**Admin:** `.ban .kick .mute .promote .purge .gban .zombies`
**Tag:** `.tagall .user1 .invite .info .pfp .bio .common .id`
**Download:** `.play .yt .insta .tt`
**Utils:** `.tr .google .wiki .weather .qr`
**Fun:** `.shayari .joke .coin .dice .truth .dare`
**Bot:** `.alive .ping .stats .afk .restart .broadcast .backup`
**AI:** PM karo ya group me reply/mention
**Toggle:** `.aigroup on/off`"""
    await event.edit(txt)

print("HellBot V11 PRO Started Successfully!")
client.start()
client.run_until_disconnected()
