import os, asyncio, time, requests, random, qrcode, wikipedia, pyjokes, psutil
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import g4f, instaloader, yt_dlp
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

def OWNER_LINK(): return f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"

print("HellBot V11 Starting...")

# ===== 1. AI CHAT BOT - PM + GROUP =====
@client.on(events.NewMessage(incoming=True))
async def chatbot(event):
    global AFK
    if event.sender_id == OWNER_ID: return
    if AFK and event.is_private: return await event.reply(f"**{OWNER_NAME} AFK hai**\n**Reason:** {AFK_REASON}")
    if event.is_group and AI_GROUP_ON != "ON": return
    if event.is_group and not event.is_reply and OWNER_NAME.lower() not in event.text.lower(): return
    
    user_id = event.sender_id
    if user_id not in chat_history: chat_history[user_id] = [{"role": "system", "content": f"Tum {OWNER_NAME} ke AI assistant ho. Hindi me short jawab do."}]
    chat_history[user_id].append({"role": "user", "content": event.text})
    try:
        response = await g4f.ChatCompletion.create_async(model=g4f.models.gpt_4o_mini, messages=chat_history[user_id])
        await event.reply(response)
    except: await event.reply("`AI busy hai`")

# ===== 2. ADMIN TOOLS =====
@client.on(events.NewMessage(pattern=f"\\{HANDLER}ban", outgoing=True))
async def ban(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    u=await e.get_reply_message(); await client.edit_permissions(e.chat_id, u.sender_id, view_messages=False); await e.edit("`Banned`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}kick", outgoing=True))
async def kick(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    u=await e.get_reply_message(); await client.kick_participant(e.chat_id, u.sender_id); await e.edit("`Kicked`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}mute", outgoing=True))
async def mute(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    u=await e.get_reply_message(); await client.edit_permissions(e.chat_id, u.sender_id, send_messages=False); await e.edit("`Muted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}unmute", outgoing=True))
async def unmute(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    u=await e.get_reply_message(); await client.edit_permissions(e.chat_id, u.sender_id, send_messages=True); await e.edit("`Unmuted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}promote", outgoing=True))
async def promote(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    u=await e.get_reply_message(); rights=ChatAdminRights(add_admins=False, invite_users=True, change_info=True, ban_users=True, delete_messages=True, pin_messages=True); await client(EditAdminRequest(e.chat_id, u.sender_id, rights, "Admin")); await e.edit("`Promoted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}demote", outgoing=True))
async def demote(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    u=await e.get_reply_message(); rights=ChatAdminRights(); await client(EditAdminRequest(e.chat_id, u.sender_id, rights, "")); await e.edit("`Demoted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}pin", outgoing=True))
async def pin(e): await client.pin_message(e.chat_id, (await e.get_reply_message()).id); await e.edit("`Pinned`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}unpin", outgoing=True))
async def unpin(e): await client.unpin_message(e.chat_id); await e.edit("`Unpinned`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}purge (\\d+)", outgoing=True))
async def purge(e): c=int(e.pattern_match.group(1)); msgs=await client.get_messages(e.chat_id, limit=c+1); await client.delete_messages(e.chat_id, msgs); await e.respond(f"`{c} msgs deleted`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}zombies", outgoing=True))
async def zombies(e): 
    c=0
    async for u in client.iter_participants(e.chat_id):
        if u.deleted: await client.kick_participant(e.chat_id, u.id); c+=1
    await e.edit(f"`{c} Zombies kicked`")

# ===== 3. TAG + USER TOOLS =====
@client.on(events.NewMessage(pattern=f"\\{HANDLER}tagall(.*)", outgoing=True))
async def tagall(e): t=e.pattern_match.group(1).strip() or "Sab aa jao"; await e.delete(); m=[f"[{u.first_name}](tg://user?id={u.id})" async for u in client.iter_participants(e.chat_id) if not u.bot]; 
for i in range(0, len(m), 5): await e.respond(f"**{OWNER_LINK()}:** {t}\n\n{' '.join(m[i:i+5])}"); await asyncio.sleep(2)

@client.on(events.NewMessage(pattern=f"\\{HANDLER}user1(.*)", outgoing=True))
async def user1(e): t=e.pattern_match.group(1).strip() or "bhai"; u=random.choice([x async for x in client.iter_participants(e.chat_id) if not x.bot]); await e.respond(f"[{u.first_name}](tg://user?id={u.id}) {t}"); await e.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}info", outgoing=True))
async def info(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    u=await client.get_entity((await e.get_reply_message()).sender_id); await e.edit(f"**Name:** {u.first_name}\n**ID:** `{u.id}`\n**Username:** @{u.username}\n**Link:** [Click](tg://user?id={u.id})")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}pfp", outgoing=True))
async def pfp(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    p=await client.download_profile_photo((await e.get_reply_message()).sender_id, file="pfp.jpg"); await client.send_file(e.chat_id, p); os.remove(p); await e.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}bio", outgoing=True))
async def bio(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    u=await client.get_entity((await e.get_reply_message()).sender_id); await e.edit(f"**{u.first_name}'s Bio:**\n\n`{u.about or 'None'}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}id", outgoing=True))
async def id(e): await e.edit(f"`Chat ID: {e.chat_id}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}common", outgoing=True))
async def common(e): 
    if not e.is_reply: return await e.edit("`Reply karo`")
    u=await e.get_reply_message(); c=await client.get_common_chats(u.sender_id); await e.edit(f"`{len(c)} Common Groups`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}invite (.*)", outgoing=True))
async def invite(e): u=e.pattern_match.group(1); await client.add_chat_user(e.chat_id, u); await e.edit("`Invited`")

# ===== 4. DOWNLOAD TOOLS =====
@client.on(events.NewMessage(pattern=f"\\{HANDLER}play (.*)", outgoing=True))
async def play(e): q=e.pattern_match.group(1); await e.edit(f"`Searching: {q}`"); os.system(f'yt-dlp -x --audio-format mp3 -o "song.mp3" --no-playlist "ytsearch1:{q}"'); 
if os.path.exists("song.mp3"): await client.send_file(e.chat_id, "song.mp3", supports_streaming=True); os.remove("song.mp3"); await e.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}yt (.*)", outgoing=True))
async def yt(e): u=e.pattern_match.group(1); await e.edit("`Downloading video...`"); os.system(f'yt-dlp -f best -o "video.mp4" {u}'); 
if os.path.exists("video.mp4"): await client.send_file(e.chat_id, "video.mp4"); os.remove("video.mp4"); await e.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}insta (.*)", outgoing=True))
async def insta(e): u=e.pattern_match.group(1); await e.edit("`Downloading reel...`"); 
try: L.download_post(instaloader.Post.from_shortcode(L.context, u.split("/")[-2]), target="insta"); 
for f in os.listdir("insta"): await client.send_file(e.chat_id, f"insta/{f}"); os.system("rm -rf insta"); await e.delete()
except: await e.edit("`Error: Private ya galat link`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}tt (.*)", outgoing=True))
async def tt(e): u=e.pattern_match.group(1); await e.edit("`Downloading...`"); os.system(f'yt-dlp -o "tt.mp4" {u}'); 
if os.path.exists("tt.mp4"): await client.send_file(e.chat_id, "tt.mp4"); os.remove("tt.mp4"); await e.delete()

# ===== 5. UTILS + SEARCH =====
@client.on(events.NewMessage(pattern=f"\\{HANDLER}tr (.*)", outgoing=True))
async def tr(e): t=e.pattern_match.group(1); r=translator.translate(t, dest="hi"); await e.edit(f"**Translated:** `{r.text}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}weather (.*)", outgoing=True))
async def weather(e): c=e.pattern_match.group(1); r=requests.get(f"https://wttr.in/{c}?format=3").text; await e.edit(f"`{r}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}google (.*)", outgoing=True))
async def google(e): q=e.pattern_match.group(1); await e.edit(f"**Google:** https://www.google.com/search?q={q}")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}wiki (.*)", outgoing=True))
async def wiki(e): q=e.pattern_match.group(1); s=wikipedia.summary(q, sentences=2); await e.edit(f"**Wiki:** {s}")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}qr (.*)", outgoing=True))
async def qr(e): t=e.pattern_match.group(1); img=qrcode.make(t); img.save("qr.png"); await client.send_file(e.chat_id, "qr.png"); os.remove("qr.png")

# ===== 6. FUN =====
@client.on(events.NewMessage(pattern=f"\\{HANDLER}shayari", outgoing=True))
async def shayari(e): await e.edit(random.choice(["Mohabbat dard deti hai...", "Teri yaad aati hai...", "Log kehte hai pyar andha hota hai..."]))

@client.on(events.NewMessage(pattern=f"\\{HANDLER}joke", outgoing=True))
async def joke(e): await e.edit(pyjokes.get_joke())

@client.on(events.NewMessage(pattern=f"\\{HANDLER}coin", outgoing=True))
async def coin(e): await e.edit(f"`{random.choice(['Heads', 'Tails'])}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}dice", outgoing=True))
async def dice(e): await e.edit(f"`{random.randint(1,6)}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}truth", outgoing=True))
async def truth(e): await e.edit(random.choice(["Last crush ka naam?", "Kabhi jhooth bola?"]))

@client.on(events.NewMessage(pattern=f"\\{HANDLER}dare", outgoing=True))
async def dare(e): await e.edit(random.choice(["10 pushup karo", "Kisi ko I love u bolo"]))

# ===== 7. BOT TOOLS =====
@client.on(events.NewMessage(pattern=f"\\{HANDLER}alive", outgoing=True))
async def alive(e): await e.edit(f"**HellBot V11 is Alive**\n**Owner:** {OWNER_LINK()}\n**RAM:** {psutil.virtual_memory().percent}%")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}ping", outgoing=True))
async def ping(e): s=time.time(); m=await e.edit("`Pinging...`"); await m.edit(f"`Pong! {round((time.time()-s)*1000)}ms`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}afk(.*)", outgoing=True))
async def afk(e): global AFK,AFK_REASON; AFK=True; AFK_REASON=e.pattern_match.group(1).strip() or "Busy"; await e.edit(f"`AFK On: {AFK_REASON}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}unafk", outgoing=True))
async def unafk(e): global AFK; AFK=False; await e.edit("`AFK Off`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}stats", outgoing=True))
async def stats(e): d=await client.get_dialogs(); g=len([x for x in d if x.is_group]); p=len([x for x in d if x.is_user]); await e.edit(f"**Groups:** {g}\n**PM:** {p}")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}restart", outgoing=True))
async def restart(e): await e.edit("`Restarting...`"); os.system("kill 1")

# ===== 8. BROADCAST + BACKUP + GBAN =====
@client.on(events.NewMessage(pattern=f"\\{HANDLER}broadcast (.*)", outgoing=True))
async def broadcast(e):
    msg = e.pattern_match.group(1)
    await e.edit("`Broadcasting...`")
    dialogs = await client.get_dialogs()
    count = 0
    for d in dialogs:
        if d.is_user and not d.entity.bot and d.entity.id != OWNER_ID:
            try: await client.send_message(d.id, f"**📢 Broadcast from {OWNER_NAME}**\n\n{msg}"); count += 1; await asyncio.sleep(0.5)
            except: pass
    await e.edit(f"**Broadcast Done**\n**Sent to:** {count} users")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}backup", outgoing=True))
async def backup(e):
    await e.edit("`Backing up chats...`")
    txt = "**Chats Backup**\n\n"
    async for d in client.iter_dialogs(): txt += f"{d.name} - `{d.id}`\n"
    with open("backup.txt", "w") as f: f.write(txt)
    await client.send_file(e.chat_id, "backup.txt"); os.remove("backup.txt"); await e.delete()

@client.on(events.NewMessage(pattern=f"\\{HANDLER}gban", outgoing=True))
async def gban(e):
    if not e.is_reply: return await e.edit("`Reply karo`")
    u = await e.get_reply_message(); count = 0
    async for d in client.iter_dialogs():
        if d.is_group:
            try: await client.edit_permissions(d.id, u.sender_id, view_messages=False); count+=1
            except: pass
    await e.edit(f"`GBanned in {count} groups`")

# ===== 9. WELCOME + TOGGLE + HELP =====
@client.on(events.ChatAction)
async def welcome(e): 
    if e.user_joined: u=await e.get_user(); await e.respond(f"**Welcome [{u.first_name}](tg://user?id={u.id}) to {e.chat.title}** 🔥")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}aigroup (on|off)", outgoing=True))
async def ai_toggle(e): os.environ["AI_GROUP_ON"]=e.pattern_match.group(1).upper(); await e.edit(f"`AI Group: {e.pattern_match.group(1).upper()}`")

@client.on(events.NewMessage(pattern=f"\\{HANDLER}help", outgoing=True))
async def help(e): 
    txt = f"""**HellBot V11 - 85+ Commands**
**Admin:** `.ban .kick .mute .promote .purge .gban`
**Tag:** `.tagall .user1 .invite`
**Download:** `.play .yt .insta .tt`
**Utils:** `.tr .google .wiki .weather .qr`
**Fun:** `.shayari .joke .coin .dice .truth .dare`
**Bot:** `.alive .ping .stats .afk .broadcast .backup`
**AI:** PM karo ya group me reply/mention
**Toggle:** `.aigroup on/off`"""
    await e.edit(txt)

print("HellBot V11 Started Successfully!")
client.start()
client.run_until_disconnected()
