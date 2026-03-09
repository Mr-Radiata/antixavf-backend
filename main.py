import json
import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid
from thefuzz import fuzz

app = FastAPI(title="Antixavf API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_ID = 33639561  
API_HASH = "666f7ed3f66ebfa3b85be8e6ca743dc9" 
BANNED_NAMES = ["a_toshqulov", "najot nuri", "xalifalik sari", "hikmatlar olami", "a toshqulov"]

try:
    with open("credentials.json", "r") as f:
        creds_data = json.load(f)
        client_config = list(creds_data.values())[0]
        CLIENT_ID = client_config["client_id"]
        CLIENT_SECRET = client_config["client_secret"]
except FileNotFoundError:
    CLIENT_ID = None
    CLIENT_SECRET = None

tg_sessions = {}

class PhoneRequest(BaseModel):
    phone: str

class CodeRequest(BaseModel):
    phone: str
    phone_code_hash: str
    code: str

# YANGI: Parol uchun model
class PasswordRequest(BaseModel):
    phone: str
    password: str

class YTDeviceRequest(BaseModel):
    device_code: str

@app.get("/")
async def root():
    return {"status": "success", "message": "Antixavf API ishmoqda!"}

# --- YORDAMCHI FUNKSIYA: Kanallarni tekshirish va xotirani tozalash ---
async def check_channels_and_cleanup(client: Client, phone: str):
    found_channels = []
    try:
        async for dialog in client.get_dialogs():
            if dialog.chat.type.value == "channel":
                for banned in BANNED_NAMES:
                    title_match = dialog.chat.title and fuzz.ratio(dialog.chat.title.lower(), banned.lower()) > 90
                    banned_clean = banned.replace("https://t.me/", "").replace("@", "").lower()
                    username_match = dialog.chat.username and dialog.chat.username.lower() == banned_clean

                    if title_match or username_match:
                        channel_info = f"{dialog.chat.title}"
                        if dialog.chat.username:
                            channel_info += f" (@{dialog.chat.username})"
                        if channel_info not in found_channels:
                            found_channels.append(channel_info)
    finally:
        await client.disconnect()
        if phone in tg_sessions:
            del tg_sessions[phone]
            
    return {"status": "success", "banned_channels": found_channels}

# ==========================================
# 1. TELEGRAM API YO'LAKLARI
# ==========================================
@app.post("/api/tg/send-code")
async def tg_send_code(req: PhoneRequest):
    clean_phone = req.phone.replace("+", "").replace(" ", "")
    client = Client(name=f"temp_{clean_phone}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    
    await client.connect()
    try:
        sent_code = await client.send_code(req.phone)
        tg_sessions[req.phone] = client 
        return {"status": "success", "phone_code_hash": sent_code.phone_code_hash}
    except Exception as e:
        await client.disconnect()
        raise HTTPException(status_code=400, detail=f"Xatolik: {str(e)}")

@app.post("/api/tg/verify-code")
async def tg_verify_code(req: CodeRequest):
    if req.phone not in tg_sessions:
        raise HTTPException(status_code=400, detail="Sessiya topilmadi.")

    client = tg_sessions[req.phone]
    try:
        await client.sign_in(req.phone, req.phone_code_hash, req.code)
        # Agar parol so'ramasa, to'g'ridan-to'g'ri tekshiradi
        return await check_channels_and_cleanup(client, req.phone)

    except SessionPasswordNeeded:
        # YANGI: Parol kerakligini React'ga aytamiz (aloqani uzmaymiz!)
        return {"status": "password_needed"}

    except Exception as e:
        await client.disconnect()
        del tg_sessions[req.phone]
        raise HTTPException(status_code=400, detail=f"Xatolik: {str(e)}")

# YANGI: Parolni tekshirish yo'lagi
@app.post("/api/tg/verify-password")
async def tg_verify_password(req: PasswordRequest):
    if req.phone not in tg_sessions:
        raise HTTPException(status_code=400, detail="Sessiya topilmadi.")

    client = tg_sessions[req.phone]
    try:
        await client.check_password(req.password)
        # Parol to'g'ri bo'lsa, tekshiruvni boshlaydi
        return await check_channels_and_cleanup(client, req.phone)
    except Exception as e:
        await client.disconnect()
        del tg_sessions[req.phone]
        raise HTTPException(status_code=400, detail="Parol noto'g'ri yoki xatolik yuz berdi.")

# ==========================================
# 2. YOUTUBE API YO'LAKLARI
# ==========================================
@app.get("/api/yt/get-code")
async def yt_get_code():
    if not CLIENT_ID:
        raise HTTPException(status_code=500, detail="YouTube sozlamalari (credentials.json) topilmadi")
    
    auth_url = "https://oauth2.googleapis.com/device/code"
    async with aiohttp.ClientSession() as session:
        payload = {"client_id": CLIENT_ID, "scope": "https://www.googleapis.com/auth/youtube.readonly"}
        async with session.post(auth_url, data=payload) as resp:
            return await resp.json()

@app.post("/api/yt/verify-and-check")
async def yt_verify_check(req: YTDeviceRequest):
    token_url = "https://oauth2.googleapis.com/token"
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
            "device_code": req.device_code, "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }
        async with session.post(token_url, data=payload) as resp:
            data = await resp.json()

            if data.get("error") == "authorization_pending":
                return {"status": "pending"}
            elif "access_token" in data:
                access_token = data["access_token"]
                found_channels = []
                url = "https://youtube.googleapis.com/youtube/v3/subscriptions"
                params = {"part": "snippet", "mine": "true", "maxResults": "50"}
                headers = {"Authorization": f"Bearer {access_token}"}
                
                while True:
                    async with session.get(url, params=params, headers=headers) as yt_resp:
                        if yt_resp.status != 200: break
                        yt_data = await yt_resp.json()
                        for item in yt_data.get("items", []):
                            title = item["snippet"]["title"]
                            for banned in BANNED_NAMES:
                                if fuzz.ratio(title.lower(), banned.lower()) > 85:
                                    if title not in found_channels: found_channels.append(title)
                        next_token = yt_data.get("nextPageToken")
                        if not next_token: break
                        params["pageToken"] = next_token
                return {"status": "success", "banned_channels": found_channels}
            else:
                raise HTTPException(status_code=400, detail="Xatolik yuz berdi.")