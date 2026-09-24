import os
import re
import json
import time
import asyncio
import logging
import threading
from collections import deque
from typing import Optional, List, Dict, Deque
from pathlib import Path
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify, redirect,
    url_for, session, send_from_directory
)

# ---- Core (from original bot) ----
from xHeaders import Ua, Uaa
from XcT import AuToUpDaTE
from Pb2 import MajoRLoGinrEq_pb2, MajoRLoGinrEs_pb2, PorTs_pb2

from main import (
    GeNeRaTeAccEss, EncRypTMajoRLoGin, MajorLogin, GetLoginData,
    DecRypTMajoRLoGin, DecRypTLoGinDaTa, xAuThSTarTuP,
    join_teamcode_packet, start_auto_packet, leave_squad_packet,
    open_squad_packet, send_invite_packet, join_by_code_packet,
    try_parse_squad_code,
    attack_packet, attack_in_squad_packet,
)
from player_info import fetch_player_info, calc_xp_progress

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# =====================================================
# CONFIG
# =====================================================
APP_USERNAME = os.environ.get("APP_USERNAME", "@xCTx_AyOuB")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "@xCTx_AyOuB")
SECRET_KEY   = os.environ.get("SECRET_KEY", "xCTx_AyOuB_super_secret_change_me")
ACCOUNTS_FILE = os.environ.get("ACCOUNTS_FILE", "web_accounts.json")

# Squad / Match timings (same as original bot)
ATTACK_BURST_DURATION = 6
ATTACK_BURST_DELAY = 0.12
MATCH_HOLD_DURATION = 900
MATCH_KEEP_INTERVAL = 5.0
MATCH_MIN_DURATION = 240
MATCH_LEVEL_CHECK_INTERVAL = 30
NEXT_MATCH_GAP = 3.0

KEEPALIVE_INTERVAL = 12
RECONNECT_DELAY = 0.5
MAX_RECONNECT_ATTEMPTS = 999
TEAMCODE_AUTO_JOIN_DELAY = 0.8
START_SPAM_DELAY = 0.15

MAX_LOGS_PER_ACCOUNT = 120
MAX_GLOBAL_LOGS = 500
LOGS_PAGE_SIZE = 50

# =====================================================
# LOGGING
# =====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("web-app")


def _aes_decrypt_packet(hex_body: str, key: bytes, iv: bytes) -> Optional[str]:
    try:
        raw = bytes.fromhex(hex_body)
        if len(raw) == 0 or len(raw) % 16 != 0:
            return None
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plain = unpad(cipher.decrypt(raw), 16)
        return plain.hex()
    except Exception:
        return None


def _now_hms() -> str:
    return time.strftime("%H:%M:%S")


# =====================================================
# ACCOUNT WORKER — adapted from telegram_bot.py
# =====================================================
class AccountWorker:
    def __init__(self, uid: str, password: str, manager: "AccountsManager"):
        self.uid = str(uid)
        self.password = str(password)
        self.manager = manager

        self.name: str = ""
        self.level: int = 0
        self.initial_level: int = 0
        self.levels_gained: int = 0
        self.progress_pct: int = 0
        self.exp: Optional[int] = None
        self.likes: int = 0
        self._last_info_fetch: float = 0.0
        self._match_entered: bool = False
        self.status: str = "idle"
        self.status_detail: str = ""
        self.last_error: str = ""
        self.level_ups_count: int = 0
        self.started_at: float = 0.0
        self.last_action_at: float = 0.0
        self._squad_opened: bool = False
        self._squad_joined: bool = False

        self.logs: Deque[str] = deque(maxlen=MAX_LOGS_PER_ACCOUNT)

        self._online_writer = None
        self._chat_writer = None
        self._online_reader = None
        self._chat_reader = None
        self._key = None
        self._iv = None
        self._region = "me"
        self.account_uid_int: Optional[int] = None

        self._stop_flag = asyncio.Event()
        self._tasks: List[asyncio.Task] = []

        self._team_code: Optional[str] = None
        self._squad_code_found: asyncio.Event = asyncio.Event()
        self._extracted_squad_code: Optional[str] = None

        self._online_connected: bool = False
        self._chat_connected: bool = False

        self._session_data: Dict = {}
        self._jwt_token: Optional[str] = None
        self._auth_token_hex: Optional[str] = None
        self._online_ip: Optional[str] = None
        self._online_port: Optional[str] = None
        self._chat_ip: Optional[str] = None
        self._chat_port: Optional[str] = None

    # --- LOG / STATUS ---
    def add_log(self, text: str, level: str = "info"):
        emoji = {"info": "ℹ️", "ok": "✅", "warn": "⚠️", "err": "❌",
                 "net": "🔌", "match": "⚔️", "sq": "🛡",
                 "tx": "📤", "rx": "📥", "atk": "⚡"}.get(level, "•")
        line = f"[{_now_hms()}] {emoji} {text}"
        self.logs.append(line)
        self.manager.add_global_log(self.uid, line)
        log.info(f"[{self.uid}] {text}")

    def set_status(self, status: str, detail: str = ""):
        if status != self.status or detail != self.status_detail:
            self.status = status
            self.status_detail = detail

    # --- LOGIN ---
    async def login(self):
        self.set_status("logging_in", "تسجيل دخول…")
        self.add_log("بدء تسجيل الدخول", "info")
        self.last_error = ""
        try:
            open_id, access_token = await GeNeRaTeAccEss(self.uid, self.password)
            if not open_id:
                raise RuntimeError("فشل في الحصول على open_id/access_token")

            payload = await EncRypTMajoRLoGin(open_id, access_token)
            login_resp = await MajorLogin(payload)
            if not login_resp:
                raise RuntimeError("MajorLogin فشل")

            auth = await DecRypTMajoRLoGin(login_resp)
            if not auth.token:
                raise RuntimeError("لا يوجد token من MajorLogin")

            token = auth.token
            url = auth.url
            self._region = getattr(auth, "region", "me") or "me"
            self._key = auth.key
            self._iv = auth.iv
            timestamp = auth.timestamp
            bot_uid = auth.account_uid
            self.account_uid_int = int(bot_uid)

            self._session_data = {
                "open_id": open_id, "access_token": access_token,
                "payload": payload, "token": token, "url": url,
                "region": self._region, "timestamp": timestamp,
                "key": self._key, "iv": self._iv, "bot_uid": bot_uid,
            }

            login_data = await GetLoginData(url, payload, token)
            if not login_data:
                raise RuntimeError("GetLoginData فشل")
            ports = await DecRypTLoGinDaTa(login_data)

            real_name = getattr(ports, "AccountName", None)
            if real_name:
                self.name = str(real_name).strip()
            if not self.name:
                self.name = f"Guest_{self.uid[-4:]}"

            self._jwt_token = token

            try:
                info = await fetch_player_info(int(bot_uid), token)
                if info:
                    if info.get("name"):
                        self.name = str(info["name"]).strip()
                    if info.get("level") is not None:
                        self.level = int(info["level"])
                        if self.initial_level == 0:
                            self.initial_level = self.level
                    if info.get("likes") is not None:
                        self.likes = int(info["likes"])
                    if info.get("exp") is not None:
                        self.exp = int(info["exp"])
                        pct = calc_xp_progress(self.level, self.exp)
                        if pct is not None:
                            self.progress_pct = pct
                    self._last_info_fetch = time.time()
                    self.add_log(f"معلومات اللاعب: lvl={self.level} • likes={self.likes}", "ok")
            except Exception as e:
                self.add_log(f"خطأ جلب معلومات اللاعب: {e}", "warn")

            self._auth_token_hex = await xAuThSTarTuP(
                int(bot_uid), token, int(timestamp), self._key, self._iv
            )
            self._online_ip, self._online_port = ports.Online_IP_Port.split(":")
            self._chat_ip, self._chat_port = ports.AccountIP_Port.split(":")

            self.add_log(f"تم تسجيل الدخول — {self.name} (region={self._region})", "ok")
            self.set_status("online", "تم تسجيل الدخول")
            self.last_action_at = time.time()
            return True
        except Exception as e:
            self.set_status("error", str(e)[:60])
            self.last_error = str(e)
            self.add_log(f"فشل تسجيل الدخول: {e}", "err")
            return False

    async def _open_connections(self):
        try:
            self._online_reader, self._online_writer = await asyncio.open_connection(
                self._online_ip, int(self._online_port)
            )
            self._online_writer.write(bytes.fromhex(self._auth_token_hex))
            await self._online_writer.drain()
            self._online_connected = True
            self.add_log(f"اتصال Online مفتوح — {self._online_ip}:{self._online_port}", "net")
        except Exception as e:
            self._online_connected = False
            raise RuntimeError(f"فشل اتصال Online: {e}")

        try:
            self._chat_reader, self._chat_writer = await asyncio.open_connection(
                self._chat_ip, int(self._chat_port)
            )
            self._chat_writer.write(bytes.fromhex(self._auth_token_hex))
            await self._chat_writer.drain()
            self._chat_connected = True
            self.add_log(f"اتصال Chat مفتوح — {self._chat_ip}:{self._chat_port}", "net")
        except Exception as e:
            self._chat_connected = False
            self.add_log(f"فشل اتصال Chat: {e} — متابعة", "warn")

    async def _safe_write_online(self, data: bytes) -> bool:
        if not self._online_writer or self._online_writer.is_closing():
            return False
        try:
            self._online_writer.write(data)
            await self._online_writer.drain()
            return True
        except Exception as e:
            self.add_log(f"خطأ كتابة Online: {e}", "warn")
            return False

    async def _drain_reader(self, reader, name: str):
        try:
            while not self._stop_flag.is_set():
                try:
                    data = await asyncio.wait_for(reader.read(9999), timeout=60)
                except asyncio.TimeoutError:
                    continue
                if not data:
                    self.add_log(f"الاتصال {name} أُغلق", "warn")
                    if name == "online":
                        self._online_connected = False
                    else:
                        self._chat_connected = False
                    break
                if (name == "online" and not self._squad_code_found.is_set()
                        and self._key and self._iv):
                    self._try_extract_squad_code(data)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.add_log(f"reader {name} خطأ: {e}", "warn")

    def _try_extract_squad_code(self, data: bytes):
        try:
            hex_data = data.hex()
            for skip in (8, 10, 12, 14, 16, 4, 6):
                if len(hex_data) <= skip + 32:
                    continue
                body = hex_data[skip:]
                usable_len = (len(body) // 32) * 32
                if usable_len == 0:
                    continue
                plain_hex = _aes_decrypt_packet(body[:usable_len], self._key, self._iv)
                if plain_hex:
                    code = try_parse_squad_code(plain_hex)
                    if code:
                        self._extracted_squad_code = code
                        self._squad_code_found.set()
                        self.add_log(f"squad_code = {code}", "sq")
                        return
        except Exception:
            pass

    async def _refresh_player_info(self, force: bool = False) -> bool:
        if not getattr(self, "_jwt_token", None) or not self.account_uid_int:
            return False
        now = time.time()
        if not force and (now - self._last_info_fetch) < 15:
            return False
        try:
            info = await fetch_player_info(int(self.account_uid_int), self._jwt_token)
        except Exception as e:
            self.add_log(f"refresh info فشل: {e}", "warn")
            return False
        self._last_info_fetch = now
        if not info:
            return False
        leveled_up = False
        if info.get("level") is not None:
            new_lvl = int(info["level"])
            if new_lvl > self.level:
                diff = new_lvl - self.level
                self.levels_gained += diff
                self.level = new_lvl
                self.add_log(f"🔝 ارتفع اللفل إلى {self.level} (+{self.levels_gained})", "ok")
                leveled_up = True
            elif self.level == 0:
                self.level = new_lvl
                if self.initial_level == 0:
                    self.initial_level = new_lvl
        if info.get("likes") is not None:
            self.likes = int(info["likes"])
        if info.get("exp") is not None:
            self.exp = int(info["exp"])
            pct = calc_xp_progress(self.level, self.exp)
            if pct is not None:
                self.progress_pct = pct
        if info.get("name") and (not self.name or self.name.startswith("Guest_")):
            self.name = str(info["name"]).strip()
        return leveled_up

    async def _keepalive_loop(self):
        while not self._stop_flag.is_set():
            for _ in range(KEEPALIVE_INTERVAL):
                if self._stop_flag.is_set():
                    return
                await asyncio.sleep(1)
            if self._online_writer and not self._online_writer.is_closing():
                try:
                    self._online_writer.write(b"\x00")
                    await self._online_writer.drain()
                except Exception:
                    pass

    async def _info_refresh_loop(self):
        await asyncio.sleep(30)
        while not self._stop_flag.is_set():
            try:
                await self._refresh_player_info(force=False)
            except Exception:
                pass
            for _ in range(60):
                if self._stop_flag.is_set():
                    return
                await asyncio.sleep(1)

    async def _start_auto_loop(self):
        """Main auto level-up loop."""
        while not self._stop_flag.is_set():
            try:
                pkt = await start_auto_packet(
                    int(self.account_uid_int), self._key, self._iv
                )
                ok = await self._safe_write_online(bytes.fromhex(pkt))
                if not ok:
                    await asyncio.sleep(2)
                    continue
                self.set_status("matching", "في المباراة")
                self.add_log("start_auto مُرسل", "match")
                self._match_entered = True
                match_start = time.time()
                last_lvl_check = 0
                while not self._stop_flag.is_set():
                    elapsed = time.time() - match_start
                    if elapsed >= MATCH_HOLD_DURATION:
                        break
                    if (elapsed > MATCH_MIN_DURATION and
                            time.time() - last_lvl_check > MATCH_LEVEL_CHECK_INTERVAL):
                        last_lvl_check = time.time()
                        leveled = await self._refresh_player_info(force=True)
                        if leveled:
                            self.add_log("لفل ارتفع — خروج مبكر", "ok")
                            break
                    await asyncio.sleep(MATCH_KEEP_INTERVAL)

                # leave squad
                try:
                    leave = await leave_squad_packet(
                        int(self.account_uid_int), self._key, self._iv
                    )
                    await self._safe_write_online(bytes.fromhex(leave))
                    self.add_log("leave_squad مُرسل", "tx")
                except Exception as e:
                    self.add_log(f"leave فشل: {e}", "warn")

                self.set_status("idle", "بانتظار الجولة التالية")
                self._match_entered = False
                await asyncio.sleep(NEXT_MATCH_GAP)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.add_log(f"start_auto loop خطأ: {e}", "err")
                await asyncio.sleep(3)

    async def run(self):
        if not await self.login():
            return
        try:
            await self._open_connections()
        except Exception as e:
            self.add_log(f"connections فشل: {e}", "err")
            self.set_status("error", "اتصال فشل")
            return
        self.started_at = time.time()
        self._tasks = [
            asyncio.create_task(self._drain_reader(self._online_reader, "online")),
            asyncio.create_task(self._keepalive_loop()),
            asyncio.create_task(self._info_refresh_loop()),
            asyncio.create_task(self._start_auto_loop()),
        ]
        if self._chat_reader:
            self._tasks.append(asyncio.create_task(
                self._drain_reader(self._chat_reader, "chat")))
        try:
            await self._stop_flag.wait()
        finally:
            for t in self._tasks:
                t.cancel()
            await asyncio.gather(*self._tasks, return_exceptions=True)
            try:
                if self._online_writer:
                    self._online_writer.close()
                if self._chat_writer:
                    self._chat_writer.close()
            except Exception:
                pass
            self.set_status("stopped", "متوقف")
            self.add_log("توقف الحساب", "info")

    def stop(self):
        self._stop_flag.set()

    def to_dict(self):
        return {
            "uid": self.uid,
            "name": self.name or f"Guest_{self.uid[-4:]}",
            "level": self.level,
            "initial_level": self.initial_level,
            "levels_gained": self.levels_gained,
            "progress_pct": self.progress_pct,
            "exp": self.exp,
            "likes": self.likes,
            "status": self.status,
            "status_detail": self.status_detail,
            "last_error": self.last_error,
            "online": self._online_connected,
            "chat": self._chat_connected,
            "match": self._match_entered,
            "started_at": self.started_at,
            "uptime": int(time.time() - self.started_at) if self.started_at else 0,
        }


# =====================================================
# ACCOUNTS MANAGER — runs asyncio loop in background thread
# =====================================================
class AccountsManager:
    def __init__(self):
        self.workers: Dict[str, AccountWorker] = {}
        self.global_logs: Deque[Dict] = deque(maxlen=MAX_GLOBAL_LOGS)
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._load_accounts()

    def _load_accounts(self):
        try:
            if Path(ACCOUNTS_FILE).exists():
                data = json.loads(Path(ACCOUNTS_FILE).read_text(encoding="utf-8"))
                for a in data:
                    uid = str(a.get("uid", "")).strip()
                    pw = str(a.get("password", "")).strip()
                    if uid and pw and uid not in self.workers:
                        self.workers[uid] = AccountWorker(uid, pw, self)
        except Exception as e:
            log.warning(f"load accounts failed: {e}")

    def _save_accounts(self):
        try:
            data = [{"uid": w.uid, "password": w.password} for w in self.workers.values()]
            Path(ACCOUNTS_FILE).write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            log.warning(f"save accounts failed: {e}")

    def add_global_log(self, uid: str, line: str):
        self.global_logs.append({
            "ts": time.time(), "uid": uid, "text": line
        })

    def start_loop(self):
        if self._loop_thread and self._loop_thread.is_alive():
            return
        def _runner():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        self._loop_thread = threading.Thread(target=_runner, daemon=True)
        self._loop_thread.start()
        # wait until loop is set
        for _ in range(50):
            if self.loop is not None:
                break
            time.sleep(0.02)

    def add_account(self, uid: str, password: str) -> bool:
        uid = str(uid).strip()
        password = str(password).strip()
        if not uid or not password:
            return False
        if uid in self.workers:
            self.workers[uid].password = password
        else:
            self.workers[uid] = AccountWorker(uid, password, self)
        self._save_accounts()
        return True

    def remove_account(self, uid: str) -> bool:
        uid = str(uid).strip()
        w = self.workers.get(uid)
        if not w:
            return False
        if self.loop:
            try:
                asyncio.run_coroutine_threadsafe(self._cancel_worker(w), self.loop)
            except Exception:
                pass
        del self.workers[uid]
        self._save_accounts()
        return True

    async def _cancel_worker(self, w: AccountWorker):
        w.stop()

    def start_account(self, uid: str) -> bool:
        self.start_loop()
        w = self.workers.get(uid)
        if not w:
            return False
        if w.status in ("online", "matching", "logging_in"):
            return True
        w._stop_flag = asyncio.Event()
        asyncio.run_coroutine_threadsafe(w.run(), self.loop)
        return True

    def stop_account(self, uid: str) -> bool:
        w = self.workers.get(uid)
        if not w:
            return False
        w.stop()
        return True

    def start_all(self) -> int:
        self.start_loop()
        count = 0
        for uid in list(self.workers.keys()):
            if self.start_account(uid):
                count += 1
        return count

    def stop_all(self) -> int:
        count = 0
        for w in self.workers.values():
            if w.status not in ("stopped", "idle", "error"):
                w.stop()
                count += 1
        return count

    def snapshot(self) -> Dict:
        return {
            "accounts": [w.to_dict() for w in self.workers.values()],
            "total": len(self.workers),
            "running": sum(1 for w in self.workers.values()
                           if w.status in ("online", "matching", "logging_in")),
            "total_levels_gained": sum(w.levels_gained for w in self.workers.values()),
            "ts": time.time(),
        }

    def recent_logs(self, limit: int = 50, uid: Optional[str] = None):
        items = list(self.global_logs)
        if uid:
            items = [x for x in items if x["uid"] == uid]
        return items[-limit:]


manager = AccountsManager()

# =====================================================
# FLASK APP
# =====================================================
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def login_required(f):
    @wraps(f)
    def deco(*a, **kw):
        if not session.get("logged_in"):
            if request.path.startswith("/api/"):
                return jsonify({"ok": False, "error": "unauthorized"}), 401
            return redirect(url_for("login"))
        return f(*a, **kw)
    return deco


# -------------- ROUTES --------------
@app.route("/")
def index():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "").strip()
        if u == APP_USERNAME and p == APP_PASSWORD:
            session["logged_in"] = True
            session["user"] = u
            return redirect(url_for("dashboard"))
        return render_template("login.html",
                               error="❌ بيانات الدخول غير صحيحة")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=session.get("user", ""))


# ---- APIs ----
@app.route("/api/snapshot")
@login_required
def api_snapshot():
    return jsonify(manager.snapshot())


@app.route("/api/logs")
@login_required
def api_logs():
    limit = int(request.args.get("limit", 80))
    uid = request.args.get("uid")
    return jsonify({"logs": manager.recent_logs(limit, uid)})


@app.route("/api/accounts/add", methods=["POST"])
@login_required
def api_add():
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()
    added = 0
    failed = []
    # Accept multiple lines  UID:PASSWORD  or  UID PASSWORD
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # split by : or whitespace
        parts = re.split(r"[:\s]+", line, maxsplit=1)
        if len(parts) != 2:
            failed.append(line)
            continue
        uid, pw = parts[0].strip(), parts[1].strip()
        if manager.add_account(uid, pw):
            added += 1
        else:
            failed.append(line)
    return jsonify({"ok": True, "added": added, "failed": failed})


@app.route("/api/accounts/remove", methods=["POST"])
@login_required
def api_remove():
    data = request.get_json(force=True, silent=True) or {}
    uid = (data.get("uid") or "").strip()
    ok = manager.remove_account(uid)
    return jsonify({"ok": ok})


@app.route("/api/accounts/start", methods=["POST"])
@login_required
def api_start():
    data = request.get_json(force=True, silent=True) or {}
    uid = (data.get("uid") or "").strip()
    ok = manager.start_account(uid)
    return jsonify({"ok": ok})


@app.route("/api/accounts/stop", methods=["POST"])
@login_required
def api_stop():
    data = request.get_json(force=True, silent=True) or {}
    uid = (data.get("uid") or "").strip()
    ok = manager.stop_account(uid)
    return jsonify({"ok": ok})


@app.route("/api/start_all", methods=["POST"])
@login_required
def api_start_all():
    n = manager.start_all()
    return jsonify({"ok": True, "started": n})


@app.route("/api/stop_all", methods=["POST"])
@login_required
def api_stop_all():
    n = manager.stop_all()
    return jsonify({"ok": True, "stopped": n})


@app.route("/health")
def health():
    return "OK", 200


# =====================================================
# ENTRY
# =====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    log.info(f"🚀 LVL UP Web starting on :{port}")
    manager.start_loop()
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
