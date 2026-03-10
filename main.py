# main.py - Original Logic with Manager Integration (Bad Bot Detection)

import requests, os, psutil, sys, jwt, json, binascii, time, urllib3, xKEys, base64, re, socket, threading, http.client, ssl, gzip, asyncio, gc, random
from io import BytesIO
from protobuf_decoder.protobuf_decoder import Parser
from xC4 import *
from google.protobuf.timestamp_pb2 import Timestamp
from threading import Thread, Barrier, Lock
import datetime as dt_mod

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# === GLOBAL STORAGE & SYNC ===
# ==========================================
ATTACK_TARGETS_DICT = {} 
TARGET_FILE = "targets.txt"
LIVE_STATUS_FILE = "bots_live_status.json" 

BOT_STATUS_DATA = {}
STATUS_LOCK = Lock()

SYNC_BARRIER = None 
ROTATION_STEP = 0
TOTAL_BOTS_LIST = []

IDLE_WAIT_TIME = 1.0 

# ==========================================
# === HELPER FUNCTIONS ===
# ==========================================

def Update_Bot_Status(bot_id, status_msg, uid="Unknown", nickname="Unknown", vv_key="Unknown"):
    with STATUS_LOCK:
        BOT_STATUS_DATA[str(bot_id)] = {
            "Id": vv_key,
            "Name": nickname,
            "Status": status_msg,
            "Timestamp": dt_mod.datetime.now().strftime("%H:%M:%S"),
            "Game uid": uid
        }

def Live_Status_Writer():
    while True:
        try:
            with STATUS_LOCK:
                data_to_save = BOT_STATUS_DATA.copy()
            with open(LIVE_STATUS_FILE, "w") as f:
                json.dump(data_to_save, f, indent=4)
        except: pass
        time.sleep(10) 

def ResTarTinG():
    print('\n [System] Restarting Bot... ! ')
    try:
        p = psutil.Process(os.getpid())
        for f in p.open_files():
            try: os.close(f.fd)
            except: pass
        for conn in p.net_connections(kind='inet'):
            try: os.close(conn.fd)
            except: pass
    except: pass
    time.sleep(0.5)
    os.execl(sys.executable, sys.executable, *sys.argv)

def AuTo_ResTartinG():
    while True:
        time.sleep(6 * 60 * 60)
        ResTarTinG()

def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint": field_data['data'] = result.data
        elif result.wire_type == "string": field_data['data'] = result.data
        elif result.wire_type == "bytes": field_data['data'] = result.data
        elif result.wire_type == 'length_delimited': field_data["data"] = Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

def DeCode_PackEt(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        return json.dumps(Fix_PackEt(parsed_results))
    except: return None

# ==========================================
# === LOGIN FUNCTIONS (ORIGINAL AS main.txt) ===
# ==========================================
def G_AccEss(U, P):
    UrL = "https://100067.connect.garena.com/oauth/guest/token/grant"
    HE = {
        "Host": "100067.connect.garena.com", 
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; SM-A515F Build/QP1A.190711.020)", 
        "Content-Type": "application/x-www-form-urlencoded", 
        "Accept-Encoding": "gzip", 
        "Connection": "close"
    }
    dT = {
        "uid": f"{U}", "password": f"{P}", "response_type": "token", 
        "client_type": "2", "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3", 
        "client_id": "100067"
    }
    try:
        R = requests.post(UrL, headers=HE, data=dT)
        if R.status_code == 200: return R.json()["access_token"], R.json()["open_id"]
    except: pass
    return None, None

def MajorLoGin(PyL):
    context = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection("loginbp.ggblueshark.com", context=context)
    headers = {
        "X-Unity-Version": "2018.4.11f1", 
        "ReleaseVersion": "OB52", 
        "Content-Type": "application/x-www-form-urlencoded", 
        "X-GA": "v1 1", 
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; SM-A515F Build/QP1A.190711.020)", 
        "Host": "loginbp.ggblueshark.com", 
        "Connection": "Keep-Alive", 
        "Accept-Encoding": "gzip"
    }
    try:
        conn.request("POST", "/MajorLogin", body=PyL, headers=headers)
        response = conn.getresponse()
        raw_data = response.read()
        if response.getheader("Content-Encoding") == "gzip":
            with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f: raw_data = f.read()
        return raw_data.hex() if response.status in [200, 201] else None
    finally: conn.close()

# --- [MANAGER INTEGRATION] Disabled Auto Restart (Manager handles it) ---
# Thread(target=AuTo_ResTartinG, daemon=True).start()

# ==========================================
# === FF CLIENT CLASS ===
# ==========================================

class FF_CLient:
    def __init__(self, U, P, bot_id):
        self.bot_uid = None
        self.nickname = "Unknown"
        self.vv_key = U
        self.bot_id = bot_id 
        self.writer2 = None
        self.attack_task = None
        self.Get_FiNal_ToKen_0115(U, P)

    async def STarT(self, JwT_ToKen, AutH_ToKen, ip, port, ip2, port2, key, iv, bot_uid):
        region = "BD"
        if not self.attack_task or self.attack_task.done():
            self.attack_task = asyncio.create_task(self.Self_Driving_Attack(bot_uid, region, key, iv))
            
        await self.OnLinE(ip2, port2, AutH_ToKen, bot_uid, key, iv)

    async def OnLinE(self, host2, port2, tok, bot_uid, key, iv):
        while True:
            try:
                self.reader2, self.writer2 = await asyncio.open_connection(host2, int(port2))
                self.writer2.write(bytes.fromhex(tok))
                await self.writer2.drain()
                
                # Update status with full info
                Update_Bot_Status(self.bot_id, "✅ Online & Attacking", bot_uid, self.nickname, self.vv_key)
                
                while True:
                    data = await self.reader2.read(9999)
                    if not data: break
            except Exception as e: 
                self.writer2 = None 
                Update_Bot_Status(self.bot_id, "⚠️ Reconnecting...", bot_uid, self.nickname, self.vv_key)
                await asyncio.sleep(5)

    # --- RESTORED: EXACT SPAM LOGIC FROM main.txt ---
    async def Spam_Single_Target(self, target, bot_uid, region, key, iv):
        try:
            if not self.writer2 or self.writer2.is_closing(): return
            await asyncio.sleep(0.1)
            pkts = Make_Team_Packet(bot_uid, region, key, iv)
            for p in pkts: self.writer2.write(p)
            self.writer2.write(Simple_Invite_Packet(target, region, key, iv))
            self.writer2.write(Leave_Team_Packet(bot_uid, region, key, iv))
            
            await asyncio.sleep(0.05)
            self.writer2.write(Open_Room_Packet(key, iv))
            self.writer2.write(Room_Invite_Packet(target, key, iv))
            self.writer2.write(Leave_Team_Packet(bot_uid, region, key, iv))
            
            await asyncio.sleep(0.05)
            pkts = Make_Team_Packet(bot_uid, region, key, iv)
            for p in pkts: self.writer2.write(p)
            self.writer2.write(Fake_Profile_Join(target, region, key, iv)) 
            self.writer2.write(Leave_Team_Packet(bot_uid, region, key, iv))
            
            await self.writer2.drain()
        except: 
            self.writer2 = None

    async def Self_Driving_Attack(self, bot_uid, region, key, iv):
        global ROTATION_STEP
        while SYNC_BARRIER is None: await asyncio.sleep(1)
        try: await asyncio.to_thread(SYNC_BARRIER.wait)
        except: pass

        while True:
            try:
                if not self.writer2: 
                    await asyncio.sleep(1); continue 

                if not ATTACK_TARGETS_DICT:
                    Update_Bot_Status(self.bot_id, "💤 Idle (No Targets)", bot_uid, self.nickname, self.vv_key)
                    await asyncio.sleep(2); continue
                
                total_lists = len(ATTACK_TARGETS_DICT)
                my_list_id = ((self.bot_id + ROTATION_STEP - 1) % total_lists) + 1
                my_targets = ATTACK_TARGETS_DICT.get(str(my_list_id), [])
                
                if my_targets:
                    Update_Bot_Status(self.bot_id, f"🔥 Spamming {len(my_targets)} Targets...", bot_uid, self.nickname, self.vv_key)
                    tasks = [asyncio.create_task(self.Spam_Single_Target(t, bot_uid, region, key, iv)) for t in my_targets]
                    await asyncio.gather(*tasks)
                    await asyncio.sleep(0.25) 
                else:
                    Update_Bot_Status(self.bot_id, "💤 Idle", bot_uid, self.nickname, self.vv_key)
                    await asyncio.sleep(IDLE_WAIT_TIME)

                if self.bot_id == 1: ROTATION_STEP += 1
            except:
                await asyncio.sleep(1)

    def GeT_Key_Iv(self, serialized_data):
        my_message = xKEys.MyMessage()
        my_message.ParseFromString(serialized_data)
        ts_obj = Timestamp(); ts_obj.FromNanoseconds(my_message.field21)
        return ts_obj.seconds * 1_000_000_000 + ts_obj.nanos, my_message.field22, my_message.field23

    def GeT_LoGin_PorTs(self, JwT_ToKen, PayLoad):
        url = "https://clientbp.ggwhitehawk.com/GetLoginData"
        headers = {
            "Authorization": f"Bearer {JwT_ToKen}", 
            "ReleaseVersion": "OB52", 
            "Content-Type": "application/x-www-form-urlencoded", 
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; SM-A515F Build/QP1A.190711.020)",
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4.11f1"
        }
        try:
            res = requests.post(url, headers=headers, data=PayLoad, verify=False)
            data = json.loads(DeCode_PackEt(res.content.hex()))
            # Nickname extraction added here (usually field 4) [cite: 85]
            nickname = data.get("4", {}).get("data", "Unknown")
            a1, a2 = data["32"]["data"], data["14"]["data"]
            return a1[:-6], a1[-5:], a2[:-6], a2[-5:], nickname
        except: return None, None, None, None, "Unknown"

    def ToKen_GeneRaTe(self, U, P):
        try:
            acc, open_id = G_AccEss(U, P)
            if not acc: return None
            
            pyl = {
                3: str(dt_mod.datetime.now())[:-7], 4: "free fire", 5: 1, 7: "1.120.1", 
                8: "Android OS 10 / API-29 (QP1A.190711.020/A515FXXU4CTJ1)", 9: "mt6769t", 10: "Grameenphone", 
                11: "WIFI", 12: 1080, 13: 2340, 14: "440", 15: "AArch64 Processor rev 4 (aarch64) | 8 cores", 
                16: 4096, 17: "Mali-G52 MC2", 18: "OpenGL ES 3.2 v1.r14p0-01rel0", 
                19: f"android|{random.randint(10000000,99999999)}", 20: "127.0.0.1", 21: "en", 22: open_id, 
                23: "4", 24: "Handheld", 25: {6: 55, 8: 81}, 29: acc, 30: 1, 41: "Grameenphone", 42: "WIFI", 
                57: "7428b253defc164018c604a1ebbfebdf", 60: 114441, 61: 25432, 62: 114441, 63: 25432, 
                64: 25432, 65: 114441, 66: 25432, 67: 114441, 73: 3, 
                74: "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64", 76: 1, 
                77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk", 
                78: 3, 79: 2, 81: "64", 83: "2019118695", 86: "OpenGLES2", 87: 16383, 88: 4, 
                89: b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg==", 92: random.randint(12000, 15000), 
                93: "android", 94: "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY=", 
                95: 110009, 97: 1, 98: 0, 99: "4", 100: "4"
            }
            payload_hex = CrEaTe_ProTo(pyl).hex()
            final_payload = bytes.fromhex(EnC_AEs(payload_hex))
            resp = MajorLoGin(final_payload)
            if resp:
                besto = json.loads(DeCode_PackEt(resp))
                uid = besto["1"]["data"]
                jwt_token = besto["8"]["data"]
                ts, key, iv = self.GeT_Key_Iv(bytes.fromhex(resp))
                ip, port, ip2, port2, nickname = self.GeT_LoGin_PorTs(jwt_token, final_payload)
                return (jwt_token, key, iv, ts, ip, port, ip2, port2, uid, nickname)
        except: pass
        return None

    def Get_FiNal_ToKen_0115(self, U, P):
        print(f" [Bot #{self.bot_id}] ⏳ Trying Login...")
        res = self.ToKen_GeneRaTe(U, P)
        
        # --- [MANAGER INTEGRATION] Report Bad Bots ---
        if not res: 
            print(f" [Bot #{self.bot_id}] ❌ Login Failed! Reporting to Manager...")
            Update_Bot_Status(self.bot_id, "❌ Login Failed", "Error", "Error", U)
            try:
                # Manager Bot will read this file and replace the bad account
                with open("bad_bots.txt", "a") as f:
                    f.write(f"{U}\n")
            except: pass
            return
        
        token, key, iv, ts, ip, port, ip2, port2, bot_uid, nickname = res
        self.bot_uid = bot_uid
        self.nickname = nickname
        
        # --- [NEW] NAME & UID DISPLAY IN CONSOLE ---
        print("="*50)
        print(f"✅ LOGIN SUCCESSFUL! [Bot #{self.bot_id}]")
        print(f"👤 NAME: {self.nickname}") 
        print(f"🆔 UID : {self.bot_uid}")  
        print("="*50)
        
        acc_id = jwt.decode(token, options={"verify_signature": False}).get("account_id")
        enc_acc = hex(acc_id)[2:]
        ts_hex = DecodE_HeX(ts)
        token_enc = EnC_PacKeT(token.encode().hex(), key, iv)
        zeros = "0000000" if len(enc_acc) == 9 else "00000000"
        self.AutH_ToKen = f"0115{zeros}{enc_acc}{ts_hex}00000{hex(len(token_enc)//2)[2:]}{token_enc}"
        
        TOTAL_BOTS_LIST.append(self)
        threading.Thread(target=lambda: asyncio.run(self.STarT(token, self.AutH_ToKen, ip, port, ip2, port2, key, iv, bot_uid)), daemon=True).start()

# ==========================================
# === DATA LOADERS & MAIN SERVER ===
# ==========================================

def load_accounts():
    try:
        with open("vv.json", "r") as f: return json.load(f)
    except: return {}

def Target_Loader():
    global ATTACK_TARGETS_DICT
    if not os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, "w") as f: json.dump({"1": []}, f)
    prev_targets = ""
    while True:
        try:
            with open(TARGET_FILE, "r") as f: data = json.load(f)
            curr = json.dumps(data, sort_keys=True)
            if curr != prev_targets:
                ATTACK_TARGETS_DICT = data; prev_targets = curr
                print(" [UPDATE] Target List Refreshed")
        except: pass
        time.sleep(5)

def StarT_SerVer():
    global SYNC_BARRIER
    if os.path.exists(LIVE_STATUS_FILE):
        try: os.remove(LIVE_STATUS_FILE)
        except: pass
    threading.Thread(target=Live_Status_Writer, daemon=True).start()
    
    accounts = load_accounts()
    print(f" [Info] Total Bots: {len(accounts)}")
    SYNC_BARRIER = threading.Barrier(len(accounts)) if accounts else None
    
    for idx, (u, p) in enumerate(accounts.items(), 1):
        FF_CLient(u, p, idx)
        time.sleep(1.0)
    Target_Loader()

if __name__ == "__main__":
    StarT_SerVer()