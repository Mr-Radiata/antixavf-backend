import os
import requests
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

# ==========================================
# ⚙️ UMUMIY SOZLAMALAR VA PAROLLAR
# ==========================================
# Telegram Parollari
API_ID = 33639561  
API_HASH = "666f7ed3f66ebfa3b85be8e6ca743dc9" 

# BARCHA TAQIQLANGAN KANALLAR (TELEGRAM + YOUTUBE BIRLASHGAN RO'YXATI)
# Oliy Sudning 2026-yil 6-aprel holatidagi qarori asosida 100% to'liq ro'yxat
BANNED_NAMES = [
    # ==========================================
    # 🔵 TELEGRAM KANALLAR RO'YXATI (850 dan ortiq)
    # ==========================================
    "a'ashiqul jannah", "abdulloh buxoriy darslari 01", "abdulloh buxoriy", "abdulloh zufar tavhid", "abdulloh zufar",
    "hijobim", "abduvali qori rohimahulloh", "abu abdulloh faqih", "abu saloh", "al shahid", "alfatx", "ali ansoriy",
    "alloh yo'lida", "allohning ism va sifatlari", "allohu akbar", "almuqit_", "an'om surasi tafsir", "ansooriy",
    "darslardan foydalar", "darslardan qisqa lavhalar", "darsliklar", "davatchilar", "dawatu ar rasul",
    "ahliddin_navqotiy tavhid va jihod", "eslating", "eslatma", "islom nuri", "ex-muslims i uzbekistan", "fakihun",
    "duo qilishdagi odoblar", "haligacha parhezdamiz", "haq nuri tavhid", "hidoya_sharhi_777", "hidoyat darsliklari",
    "hidoyat tv", "hijobiga sodiqlar", "himmat darsligi", "hizb sadoqat uz", "holis islom", "ilm bu nur",
    "abu ubayda ibn jarroh", "abu xolid rohimahulloh", "abu xolid xurosoniy", "abu zafar media", "abuabdulloh andijoniy",
    "abuabdulloh_alfaqih", "amniyat borasida maslahatlar", "ahli sunna imomlari", "ahli sunna wal jamaa", "ahli sunna",
    "ahluddin navqatiy", "ahluddin navqotiy darsliklari", "ahluddinnavqotiy l audio", "al-furqon", "al-haq media",
    "al-hijratstudiyasi", "alloh yolida kuchli birodarlar", "asadulloh urganchiy nasheed", "al badr media", "at-tauhid",
    "ansor media", "ansorulloh", "anti ateist", "asadulloh urganjiy", "asmoul husna", "aqiyda darslari", "aqiydatul vositiya",
    "ayollar darslari silsilasi", "azon, tilovat va duolar", "абу абдуллох шоший", "arabic nasheed", "arobiy", "da'vat uz",
    "аҳлис сунна", "bir oyat", "bismillah", "biznillah", "blvck rose", "buyuk ummat", "bahjatul majalis", "davat_uz",
    "falastin rasmiy kanal", "falastin/quddus", "fikriy ozuqasi - qisqa", "fiqh ahkomlari", "fiqh darslari", "foida mp3",
    "foida va qoidalar rasm", "foida va qoidalar", "foydalar sharhi", "aqidaga oid savol-javoblar", "abduvali qori aqida darsliklari",
    "g'ariblar", "gariblar", "hanafiy fiqhi", "hanbali kundaligi", "hadis ahli", "haq ahli", "haqdinga", "ilm izlab safar",
    "abduvali qori rohmimahulloh qisqa", "ilmi toliblar", "ilohiy sunnatlar", "imom buxoriy", "islam_news_uz", "islamiyya",
    "islom davlatiga shubhasi borlar uchun", "islom ovoz", "islom ovozi", "islom tarixi", "islom_yo'li", "islom", "islomiy oila",
    "islomiy pdf kitoblar", "ixlos. tv", "ixlosorg fatvolar", "ixlosorg sahifasi", "dinim islom", "djihad", "islomni buzuvchilar",
    "istina islam group", "izzat allohnikidir", "jahannam haqida", "jangovor dastur", "jannatga eltuvchi yo'l", "jannatga oshiqlar",
    "javziyy", "jihad media", "jihod uzbek", "jihodga shoshiling", "julaybibb", "jundulloh jihodiy nashidalari", "kafarna bikum",
    "khanifa//ayollar uchun", "khuroson lashkari", "muowiya", "muslimalarga eslatma", "mustahkam tutqich", "mustalahul hadis",
    "musulmonlar", "muvahhid", "muvahhida ayollar", "muvoiya", "muzakkir", "мисрий кутуб", "nashed114", "nashid/qiroatlar",
    "nashidalar", "nasheeda", "new_studio_o1", "nozik xilqat", "nusrat va fatih", "pdf kitoblar", "islomiy tushunchalar",
    "nashidlar/salovatlar", "nusrat yaqin inshaalloh", "qiyomatdan avvalgi fitnalar", "qomar tavhid ahli", "qovaidul_arbai_matni",
    "qur'oni karim tafsiri", "risolat soyalarida", "roddul kufr", "sahobalar siyrati", "maxfiylik darslari", "salaflar hayotidan",
    "saodat yoli sari", "savol javob", "savol va javoblar", "shams solih", "shar'iy macalalar", "shar'iymasalalar", "sevimli oyatlarim",
    "shom sadosi", "ixlostv", "rabboniy ulamolar", "rashod qori kamolov maruzalari", "muhammad_ibrohim_yusuf", "muhammad03tohir foruq rohimahulloh",
    "nusrat va tamkin asoslari", "namoz va uni tark qiluvchisini hukmi", "islomni buzuvchi amallar darslari", "namoz va benomozga taluqli masalalar",
    "sayfulloh al-maslul harbiy akademiyasi", "muslima ayol qizlar uchun", "mahmud abdulmo'min darsliklari", "muvahhid kutibxonasi",
    "maktabdagi kufr va shirklar", "manfatli bolsin inshaa allax", "shahid o'lamiz in shaa alloh", "shayh abdulvali qori darsliklari",
    "shayx abdulloh buhoriy", "shayx abdulloh buxoriy rohimahulloh", "kun foydasi sharhi mp3", "kun hikmati", "kun mavzulari",
    "islam", "ixvatun", "ma'rifatulloh", "mabdal qiroat 1", "marifatulloh media", "media_jihod", "media", "mufakkirr", "muhammad toxir",
    "muhim darslar", "muhojir_xurosoniy", "muhsintv sahifasi", "mujohid", "mujohidlar", "muoviya", "ulamolar nasihati", "qisqa darsliklar",
    "qisqa iqtiboslar", "qisqalar", "qiyomat va fitnalar", "obidxon qori nazarov", "ovozli_yangiliklar111", "qur'oni karim tafsiri",
    "quwat al ghuroba", "qur'in va tavhid", "quran & sunnat", "r_i_j_a_l", "rijollar 007", "rijol-tv", "sabr", "sahih qissalar",
    "sahihi buxoriy sharhi", "sahobalartarixi1", "абдуллох зуфар", "shomdan_maktub", "shubhalarga raddiya", "siyrat_tv", "sof aqidadagi darslar",
    "sound", "sunnat ahli", "tasdiq va inkor", "tavhid ahli", "tafsir_ibni_kasir", "tahoviy aqida kitobi", "tahvid war 360p",
    "talabalar uchun darslar", "talbisu iblis darslari", "tavhid", "terma nashid", "the muslims", "абдуллохзуфарталабалар",
    "shayx_rafiq_qori_rahimahulloh", "shayx_rafiq_qori_rahmatulloh1", "shubxalarga raddiyalar", "mp3 darslar to'plami",
    "siyrat ustoz abu muoviya", "tavhid darsliklari", "tavhid davatchilari", "tafsiri muyassar i rasmiy kanal", "tavhid jannat kaliti",
    "tavhid kanal", "асадуллох урганчий нашидалар канали", "ахлуддин навкотий дарсликлари", "asadulloh urganchiy/асадуллох урганчий",
    "абдували кори дарсликлар", "абдуллох бухорий/abdulloh buxoriy", "bandaning ibodati tavhid ustiga quriladi", "barcha paygambarlarning umumiy davati",
    "undud qissasidan ibratlar", "umdatul ahkam", "umma news_uz", "ummatka eslatma", "unutilgan sunnatlar", "usmoniylar", "ustoz abdulhadiy darslari",
    "ustoz abu saloh", "ustoz abu xolid", "ustozlarimiz", "usulul fiqh", "uygon ummat", "uzbekcha nashida", "video darsliglar", "videogram uz",
    "volidam_ilindim", "xilofat sari", "xilofat", "абу муовия", "абу салох киска", "абу салох", "абу. уккоша", "акида ал-таховия", "ал_масрук",
    "аль-фатҳ тв", "асмоул хусна", "аҳли илмлар", "аҳли сунна устозлар", "дуо ва зикр", "даъватчилар", "ғалаба шаббодаси", "джамаат",
    "дорога в рай", "жаннат ошиклари", "жиходий дарслар", "зуфар медиа", "ислом йўли", "аброр мухтор алий 11", "абу салох дарсликлари",
    "ақийда_амният_фикр", "бидъат аҳлига раддия", "демократия бу ширк", "жангавар дастур", "ustoz ahluddin navqotiy", "ustoz yahyo turkistoniy",
    "yahyo turkistoniy muxlislaridan", "ислом уммати/islom ummati", "исломда уммат мажлиси", "ишиднинг хаворижлиги", "қалб тубидаги фикрлар",
    "mahmud abdulmomin", "мазлум муминнинг йули", "мазлумларни унутманг", "мен севган устозлар", "мужохидлар сафи/mujohidlar safi",
    "воины ислама не познают страха", "куръон тафсири содик самаркандий", "мысли из глубины души|фаваид 7", "тавхидга даъват (tavhid)",
    "устоз анвар махдум ҳафизаҳуллоҳ", "устоз муҳаммад косоний", "устоз обидхон кори ҳафизаҳуллоҳ", "устоз яҳё туркистоний ҳафизаҳуллоҳ",
    "тавҳид қалами илмий изланишлар ва ёзувчилар маркази", "устоз абдуллох бухорий рохимахуллох", "abdulhadiy domla/rasmiy kanal",
    "abdulloh buhoriy/абдуллох бухорий", "mu`minlarga manfaatli", "02 устоз яҳьё туркистоний дарсликлар", "яҳьё туркистоний дарсликлар топлами",
    "эслатма/нашид/куръон", "turk tili onlayin ayollar uchun", "sekulyarizm islom mezonida", "xilofot qaytdi", "xolid", "xolis nazar", "хикмат излаб",
    "ya quratain", "yahyo turkistoniy", "yamusl1ma_h", "yaqiyn tv", "yusuf davron", "yusuf media", "munosabat_l", "преусиевшие",
    "o’zbekiston islomiy harakati", "zaytun shajarasi", "zulfiqor media", "zulmatdan nurga", "abdulvali qori", "аробий sa", "ислом тарихи",
    "исломий канал", "истории ислама", "қўрон ва суннат", "муваххиддалар", "муваххид", "мухажер", "саад мухтор", "саломат қалб", "сионистлар кимлар",
    "соғинч жиходи", "мухсинлар", "уповайю", "узр йўқ", "ўзбекча pdf китоблар", "уаджиб", "таувхид", "тавхидга даъват", "хак йоли", "хак йoли",
    "мужоҳидлар сафи/mujohid...", "нашиды без музык", "нашиды/nashedy", "очиқ хат", "рамазон сухбатлари 1436-1437", "рашод қори/rashod qori",
    "тавхид ва жиход", "исламские книги pdf", "исламская библиотека pdf", "islom yo'li", "абу юсуф", "шейх салих аль усейми", "таухид единобожие",
    "тил офати", "турли мавзулар", "усулул фикх", "учебное чтение", "устоз абдуллох бухорий", "уламолар сиёҳи", "устоз яҳё туркистоний",
    "✿iymonni ko‘taring✿", "islom ummatining 100 buyuk insonlari", "ongli ҳаёт сари! ongli hayot sari", "dard_va_davo_darsliklar",
    "nafsni poklash/tazkiya", "salomat_qalb_darslik", "mahmud abdulmo'min (норасмий канал)", "abdulloh zufar (sara darslari)",
    "ибн таймийя роҳимаҳуллоҳ", "shayx sodiq samarqandiy darslari", "ustoz abduvali qori tafsirlari", "kiiiiil1", "_abu_huzaifaaa",
    "abdullohbuhoriydarslari", "abumuhammaduzbek/93", "shomga_marhabo_uz/28", "xadis_va_hayot_nasheed", "abusaloh_1", "abuxolid88",
    "amniyat6/46", "абдували кори", "абдуллоз зуффар", "исломий кутубхона", "шахидликнинг 30 фазилати", "шайхулислом ибн таймия",
    "abduiiohzufarrrr", "хидоят сари", "шайх содик самаркандий", "шайх сулаймон улвон", "шом овози", "шайх абдували кори", "шариат максадлари",
    "шарх акыда тахавия", "фазлиддин шахобиддин", "julaybib", "военная тактика", "qur’oni karim tafsiri", "мухаммад тохир йўлдош",
    "zayd nasheed", "risolat tv | расмий канал", "устоз абдул азиз", "фикх джихада", "фойда қоидалар", "abdullah_111", "sahih_media1",
    "_soliyhin_", "исломий ҳаёт сари", "ittaqulloh_chat", "bayyinah 114", "axiy_uz", "at. tamkiyn", "коран", "nasheed", "at-tavhid",
    "muhaarrib", "qur'on va tavhid", "уламолар", "toliblar uchun darslar", "sizdan so'rashadi...", "qomondon juma namangoniy",
    "исломга мухаббат", "muslim va muslima", "абу муҳаммад касоний", "abduloh domla", "минбардаги шайтонлар", "al. muwahhid", "hadis ilmlari",
    "gozal xulq", "муваххид", "musulman", "miyassar fiqh", "rasululloh ummatlari", "qadr kechasi haqida...", "ayollar_uchun_darsliklar",
    "сакинатли оила сари", "ahluddin_mp3", "as_sodaqun", "jhodiy", "rijol_002", "rafiq_qori", "aql_uygon/152", "ustoz_abu_xolid",
    "davat_vaqti/1240", "abu_saloh3/4", "muvaxxidlar_01/805", "ochiq_xatga_raddiya", "араб ёзувида", "ahkom_oyatlar", "solixy",
    "aqidatul_vositiyya", "nahvdarslari", "hamaviyya", "haq_uchun",
    "global tahlil i rasmiy sahifa", "nashdalar texti bilan", "hurlar 3 oshiqi", "kuchli nashidalar group", "labbayk | nashid imon jasorat. jihod",
    "fulaan19", "nashedalar tekste", "ukkasha_shamiy", "абу мухаммад мадани", "исломий pdf китоблар (заҳира)", "munadiytv", "mahmud abdulmomin audio & videoroliklar",
    "jabal_kavkaz", "qanatabnaualjihad", "ohdkqijajm030duy", "jundulloh_studio", "saodat_axli", "ustoz sodiq samarqandiy tafsirlari",
    "islom yo'lim", "abduvalikaril", "ақл эгалари учун ибратлар", "асар аҳли учун дарсликлар", "wlxlkw", "tj portal 24/7 chat",
    "oxirathovlisi kutubxonasi", "тавҳидни ўрганинг", "sunantv fazliddin shahobiddin", "soğlom fikr", "sof islomiy audio va videoroliklar",
    "uch asos sharhi - umar toshkandiy rohimanulloh", "уч асос шарҳи", "марокашдаги норозилик намойишлари", "imuoviya", "muhammad", "muhajirun",
    "саломат қолб", "sayful adl", "tolibi ilmlarga eslatma", "abduvali qori", "саабііқун", "oxirat hovlisi", "д///ихад", "qalb salomatligi",
    "sahih hadislar muslim", "pdf kitoblar", "at-taqva",
    
    # ==========================================
    # 🔴 YOUTUBE KANALLAR RO'YXATI (190 ta to'liq)
    # ==========================================
    "abdulloh ayyub", "abdulloh islamiy", "abror ibn abdulloh", "foruq uz", "guraba", 
    "hidoyat izlab", "hidoyat tv", "islam abu khalil", "islamic talks", "islom tongi", 
    "alhaq_tv", "alijon aliev", "al-ixlos", "anti. kazzob", "aqiyda darslari", 
    "aqiydatul vositiya", "asl haq", "ayollar darslari silsilasi", "bayyina tv", "da'vat media", 
    "da'vat uz", "darslardan qisqa lavhalar", "darsliklar", "davat uz", "din faxri", 
    "ehson tv", "fiqh ahkomlari", "foida mp3", "ahli zikr", "ahli-sunna tv", 
    "al buhoriy tv", "ixloc tv", "jannatga yo'l", "mahmud abdulmomin", "muhim darslar", 
    "muhojir uz", "muhsin tv", "muslim tv", "mustalahul hadis", "omar alhamed", 
    "qalb nuri", "saad muhtor", "saad muxtor 2", "saad muxtor", "risolat hazinasi", 
    "savol va javoblar", "sheriyat olami", "yusuf media", "hidoyat yo'li", "zaytun tv", 
    "zufarmedia", "islom bahori", "salomat qalb", "allohu ahad", "shayx abduvali qori", 
    "al waqiyah tv-uz", "al_buhoriy_tv", "al-anfal media", "siyrat", "solixlargulshani", 
    "tafsir darslari", "qiyomatdan avvalgi fitnalar", "shom media", "silsilaviy darslar va ma'ruzalar", 
    "islom dinim media sahifasi", "islomni buzuvchi amallar darslari", "talabalar uchun darslar", 
    "talbisu iblis darslari", "tamkin media", "taqvo media tv", "tavhid darsi", "tavhid maktabi", 
    "the saroy mulla!", "turkiston", "ustozlar davatlari", "usulul fiqh", "uzbek uz", "uzr yoq", 
    "xolis media", "alfatx", "foida va qoidalar", "foruq uz", "ечим исломда", "ал-ваъй", 
    "ал-фатх тв", "аль-фатҳ тв", "аль фатх тв", "sodiqlar uz", "tavhidorg sahifasi l rasmiy", 
    "yaumma", "iymonli qalblar", "muslim tv sahifasi", "al-fatx studio", "ummat sheri", 
    "taqvo media", "таухид медиа", "hidoyat islom tarixi", "nomoz va benomozga taluqli masalalar", 
    "солиха сатторова", "қуддус хақида таҳлил", "rushda huda", "muhojir podcast", 
    "хизб-ни аъзоси ноокатлик полвон ака", "иброҳим муваҳҳидм", "islom ulamolari ислом уламолари", 
    "ўзбекистонда топмагандим яҳудийлар кўп жойда топдим", "uch_asos_27",
    "muhojir tactical", "risolat xazinasi", "saodat asri", "роя", "zaytun shajarasi", 
    "itaqillah media", "хуррият инфо", "albayan media", "said media", "global tahlil", 
    "payg'ambarlar yo'li", "o'zbekcha nashidalar", "munzir media", "xolid_jazroviy", 
    "da'vat media", "muslim tv", "nusrat yo'li", "ahluddin navqotiy", "darslik", "rabboniylar", 
    "фаластиндаги холат", "ечим исломда", "risolat tv", "da'vat tube", "syria news", 
    "rizvon tv", "payg'ambarlar davati", "muhojir uz", "yusuf media", "нажот", "zaytun shajarasi", 
    "nubuvvat media", "kelajak avlod", "rashodxon qori official", "birkam dunyo", "sog'lom e'tiqod", 
    "zaytun tv", "jannat kaliti tavhid", "tavhid maktabi", "islom yoshlari", "irshodtv", "uzbek uz", 
    "o'zbekistonda erkak qoldimi?", "tavhid yo'li", "жонли суҳбат", "нашид а души как воины", 
    "нашида, шариатни ўзларида кулламаган", "нега раддия берасизлар", "abu saloh video", 
    "alhamdulillah muslim", "aziz murodullaevich", "holislik sari davom etadi", "jannat oshiqlari", 
    "jannatgadoshiqlar", "ummatlar", "uyg'on ummat ahli", "номалум шахслар", "оллохga oshiq qalblar", 
    "uyquchi ummat", "yechim islomda.uz", "альхамдулиллях)))", "бахрамжон хатамов", 
    "диллмурод аллхамдулилах", "дневник мусульманина", "исломий савол жавоблар", "сахобалар изидан", 
    "quron va sunnat va ulamolar fatvolari", "муминларди жиходга кизихтириг", 
    "muslim va muslimalar faqat olloh yolida", "savol va javoblar", "жаннатга ошиклар бизга қўшилинг", 
    "жаннатга ошиқлар", "сизга айтолмаган сўзларим", "исомиддин ислом", "хикmathoma", 
    "ла илаха иллаллох", "mirhaid tohirov", "мансур амин", "холис инсон", "shahodat oshiqlari"
]
   
# YouTube Parollari (Render Environmentdan olinadi)
raw_id = os.environ.get("GOOGLE_CLIENT_ID", "")
raw_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
CLIENT_ID = raw_id.replace('"', '').replace("'", "").strip()
CLIENT_SECRET = raw_secret.replace('"', '').replace("'", "").strip()
REDIRECT_URI = "https://antixavf.uz"

tg_sessions = {}

# ==========================================
# 📦 PYDANTIC MODELLARI
# ==========================================
class PhoneRequest(BaseModel):
    phone: str

class CodeRequest(BaseModel):
    phone: str
    phone_code_hash: str
    code: str

class PasswordRequest(BaseModel):
    phone: str
    password: str

class WebVerifyRequest(BaseModel):
    code: str

@app.get("/")
async def root():
    return {"status": "success", "message": "Antixavf API 100% xavfsiz va maxfiy rejimda ishlamoqda!"}

# ==========================================
# 🔵 TELEGRAM API YO'LAKLARI
# ==========================================
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
        try:
            await client.log_out() 
        except Exception:
            await client.disconnect() 
            
        if phone in tg_sessions:
            del tg_sessions[phone]
            
    return {"status": "success", "banned_channels": found_channels}


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
        raise HTTPException(status_code=400, detail="Sessiya topilmadi. Iltimos, kodni qaytadan so'rang.")

    client = tg_sessions[req.phone]
    try:
        await client.sign_in(req.phone, req.phone_code_hash, req.code)
        return await check_channels_and_cleanup(client, req.phone)
    except SessionPasswordNeeded:
        return {"status": "password_needed"}
    except Exception as e:
        await client.disconnect()
        del tg_sessions[req.phone]
        raise HTTPException(status_code=400, detail=f"Xatolik: {str(e)}")


@app.post("/api/tg/verify-password")
async def tg_verify_password(req: PasswordRequest):
    if req.phone not in tg_sessions:
        raise HTTPException(status_code=400, detail="Sessiya topilmadi.")

    client = tg_sessions[req.phone]
    try:
        await client.check_password(req.password)
        return await check_channels_and_cleanup(client, req.phone)
    except Exception as e:
        await client.disconnect()
        del tg_sessions[req.phone]
        raise HTTPException(status_code=400, detail="Parol noto'g'ri yoki xatolik yuz berdi.")


# ==========================================
# 🔴 YOUTUBE API YO'LAKLARI
# ==========================================
@app.post("/api/yt/verify-web")
async def verify_yt_web(req: WebVerifyRequest):
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": req.code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    token_res = requests.post(token_url, data=token_data)
    token_json = token_res.json()
    
    if "access_token" not in token_json:
        qanday_xato = token_json.get("error_description", str(token_json))
        raise HTTPException(status_code=400, detail=f"Google aytdi: {qanday_xato}.")
        
    access_token = token_json["access_token"]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    yt_url = "https://www.googleapis.com/youtube/v3/subscriptions?part=snippet&mine=true&maxResults=50"
    
    found_banned_channels = [] 
    
    # 🛡️ DIAGNOSTIKA TUGADI! ENDI HAQIQIY FILTRNI ISHGA TUSHIRAMIZ:
    while True:
        yt_res = requests.get(yt_url, headers=headers)
        if yt_res.status_code != 200:
            break
            
        yt_data = yt_res.json()
        for item in yt_data.get("items", []):
            title = item["snippet"]["title"]
            # YouTube kanallarini THEFUZZ bilan qidiramiz
            for banned in BANNED_NAMES:
                if fuzz.ratio(title.lower(), banned.lower()) > 85:
                    if title not in found_banned_channels:
                        found_banned_channels.append(title)
                        
        next_token = yt_data.get("nextPageToken")
        if not next_token:
            break
        yt_url = f"https://www.googleapis.com/youtube/v3/subscriptions?part=snippet&mine=true&maxResults=50&pageToken={next_token}"
            
    return {
        "status": "success",
        "banned_channels": found_banned_channels
    }