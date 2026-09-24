import requests ,os ,json ,binascii ,time ,urllib3 ,base64 ,datetime ,re ,socket ,ssl ,asyncio ,aiohttp ,random ,traceback 
from protobuf_decoder .protobuf_decoder import Parser 
from xHeaders import *
from XcT import *
from XcTxTeaM import *
from datetime import datetime 
from concurrent .futures import ThreadPoolExecutor 
from Pb2 import DEcwHisPErMsG_pb2 ,MajoRLoGinrEs_pb2 ,PorTs_pb2 ,MajoRLoGinrEq_pb2 
import google .protobuf .json_format as json_format 

def rot13 (text ):
    result =""
    for c in text :
        if 'a'<=c <='z':
            result +=chr ((ord (c )-ord ('a')+13 )%26 +ord ('a'))
        elif 'A'<=c <='Z':
            result +=chr ((ord (c )-ord ('A')+13 )%26 +ord ('A'))
        else :
            result +=c 
    return result 

LEVEL_UP =rot13 ("XcT x TeaM BoT LvL")

urllib3 .disable_warnings (urllib3 .exceptions .InsecureRequestWarning )

online_writer =None 
whisper_writer =None 
last_online_packet =None 
last_chat_packet =None 
insquad =None 
joining_team =False 
last_squad_uid =None 
last_squad_code =None 

login_url ,ob ,version =AuToUpDaTE ()
Hr ={
'User-Agent':Uaa (),
'Connection':"Keep-Alive",
'Accept-Encoding':"gzip",
'Content-Type':"application/x-www-form-urlencoded",
'Expect':"100-continue",
'X-Unity-Version':"2018.4.11f1",
'X-GA':"v1 1",
'ReleaseVersion':ob 
}
CURRENT_BOT_UID =None 
region ='IN'

async def SEndPacKeT (ChaT ,OnLinE ,TypE ,PacKeT ):
    global last_online_packet ,last_chat_packet 
    try :
        if TypE =='ChaT'and ChaT :
            ChaT .write (PacKeT )
            await ChaT .drain ()
            last_chat_packet =PacKeT 
        elif TypE =='OnLine'and OnLinE :
            OnLinE .write (PacKeT )
            await OnLinE .drain ()
            last_online_packet =PacKeT 
    except Exception as e :
        print (f"[SEND] error: {e }")

async def GeNeRaTeAccEss (uid ,password ):
    url ="https://100067.connect.garena.com/oauth/guest/token/grant"
    headers ={
    "Host":"100067.connect.garena.com",
    "User-Agent":await Ua (),
    "Content-Type":"application/x-www-form-urlencoded",
    "Accept-Encoding":"gzip, deflate, br",
    "Connection":"close"
    }
    data ={
    "uid":uid ,
    "password":password ,
    "response_type":"token",
    "client_type":"2",
    "client_secret":"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
    "client_id":"100067"
    }
    async with aiohttp .ClientSession ()as session :
        async with session .post (url ,headers =headers ,data =data )as response :
            if response .status ==200 :
                data =await response .json ()
                return data .get ("open_id"),data .get ("access_token")
            return None ,None 

async def encrypted_proto (encoded_hex ):
    key =b'Yg&tc%DEuh6%Zc^8'
    iv =b'6oyZDr22E3ychjM%'
    cipher =AES .new (key ,AES .MODE_CBC ,iv )
    padded_message =pad (encoded_hex ,AES .block_size )
    encrypted_payload =cipher .encrypt (padded_message )
    return encrypted_payload 

async def EncRypTMajoRLoGin (open_id ,access_token ):
    major_login =MajoRLoGinrEq_pb2 .MajorLogin ()
    major_login .event_time =str (datetime .now ())[:-7 ]
    major_login .game_name ="free fire"
    major_login .platform_id =1 
    major_login .client_version =version 
    major_login .system_software ="Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login .system_hardware ="Handheld"
    major_login .telecom_operator ="Verizon"
    major_login .network_type ="WIFI"
    major_login .screen_width =1920 
    major_login .screen_height =1080 
    major_login .screen_dpi ="280"
    major_login .processor_details ="ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login .memory =3003 
    major_login .gpu_renderer ="Adreno (TM) 640"
    major_login .gpu_version ="OpenGL ES 3.1 v1.46"
    major_login .unique_device_id =f"Google|{random .getrandbits (128 ):032x}"
    major_login .client_ip ="223.191.51.89"
    major_login .language ="en"
    major_login .open_id =open_id 
    major_login .open_id_type ="4"
    major_login .device_type ="Handheld"
    memory_available =major_login .memory_available 
    memory_available .version =55 
    memory_available .hidden_value =81 
    major_login .access_token =access_token 
    major_login .platform_sdk_id =1 
    major_login .network_operator_a ="Verizon"
    major_login .network_type_a ="WIFI"
    major_login .client_using_version ="7428b253defc164018c604a1ebbfebdf"
    major_login .external_storage_total =36235 
    major_login .external_storage_available =31335 
    major_login .internal_storage_total =2519 
    major_login .internal_storage_available =703 
    major_login .game_disk_storage_available =25010 
    major_login .game_disk_storage_total =26628 
    major_login .external_sdcard_avail_storage =32992 
    major_login .external_sdcard_total_storage =36235 
    major_login .login_by =3 
    major_login .library_path ="/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login .reg_avatar =1 
    major_login .library_token ="5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login .channel_type =3 
    major_login .cpu_type =2 
    major_login .cpu_architecture ="64"
    major_login .client_version_code ="2019118695"
    major_login .graphics_api ="OpenGLES2"
    major_login .supported_astc_bitset =16383 
    major_login .login_open_id_type =4 
    major_login .analytics_detail =b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login .loading_time =13564 
    major_login .release_channel ="android"
    major_login .extra_info ="KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login .android_engine_init_flag =110009 
    major_login .if_push =1 
    major_login .is_vpn =1 
    major_login .origin_platform_type ="4"
    major_login .primary_platform_type ="4"
    string =major_login .SerializeToString ()
    return await encrypted_proto (string )

async def MajorLogin (payload ):
    url =f"{login_url }MajorLogin"
    ssl_context =ssl .create_default_context ()
    ssl_context .check_hostname =False 
    ssl_context .verify_mode =ssl .CERT_NONE 
    async with aiohttp .ClientSession ()as session :
        async with session .post (url ,data =payload ,headers =Hr ,ssl =ssl_context )as response :
            if response .status ==200 :
                return await response .read ()
            return None 

async def GetLoginData (base_url ,payload ,token ):
    url =f"{base_url }/GetLoginData"
    ssl_context =ssl .create_default_context ()
    ssl_context .check_hostname =False 
    ssl_context .verify_mode =ssl .CERT_NONE 
    Hr ['Authorization']=f"Bearer {token }"
    async with aiohttp .ClientSession ()as session :
        async with session .post (url ,data =payload ,headers =Hr ,ssl =ssl_context )as response :
            if response .status ==200 :
                return await response .read ()
            return None 

async def DecRypTMajoRLoGin (data ):
    proto =MajoRLoGinrEs_pb2 .MajorLoginRes ()
    proto .ParseFromString (data )
    return proto 

async def DecRypTLoGinDaTa (data ):
    proto =PorTs_pb2 .GetLoginData ()
    proto .ParseFromString (data )
    return proto 

async def DecodeWhisperMessage (hex_packet ):
    packet =bytes .fromhex (hex_packet )
    proto =DEcwHisPErMsG_pb2 .DecodeWhisper ()
    proto .ParseFromString (packet )
    return proto 

async def xAuThSTarTuP (TarGeT ,token ,timestamp ,key ,iv ):
    uid_hex =hex (TarGeT )[2 :]
    uid_length =len (uid_hex )
    encrypted_timestamp =await DecodE_HeX (timestamp )
    encrypted_account_token =token .encode ().hex ()
    encrypted_packet =await EnC_PacKeT (encrypted_account_token ,key ,iv )
    encrypted_packet_length =hex (len (encrypted_packet )//2 )[2 :]
    if uid_length ==9 :
        headers ='0000000'
    elif uid_length ==8 :
        headers ='00000000'
    elif uid_length ==10 :
        headers ='000000'
    elif uid_length ==7 :
        headers ='000000000'
    else :
        headers ='0000000'
    return f"0115{headers }{uid_hex }{encrypted_timestamp }00000{encrypted_packet_length }{encrypted_packet }"

async def join_teamcode_packet (team_code ,key ,iv ,region ):
    fields ={
    1 :4 ,
    2 :{
    4 :bytes .fromhex ("01090a0b121920"),
    5 :str (team_code ),
    6 :6 ,
    8 :1 ,
    9 :{2 :800 ,6 :11 ,8 :"1.111.1",9 :5 ,10 :1 }
    }
    }
    if region .lower ()=="me":
        packet_type ='0514'
    elif region .lower ()=="bd":
        packet_type ="0519"
    elif region .lower ()=="ind":
        packet_type ='0514'
    else :
        packet_type ="0515"
    return await GeneRaTePk ((await CrEaTe_ProTo (fields )).hex (),packet_type ,key ,iv )

async def leave_squad_packet (idT ,key ,iv ,region ):
    fields ={1 :7 ,2 :{1 :int (idT )if idT else 11037044965 }}
    if region .lower ()=="me":
        packet_type ='0514'
    elif region .lower ()=="bd":
        packet_type ="0519"
    elif region .lower ()=="ind":
        packet_type ='0514'
    else :
        packet_type ="0515"
    return await GeneRaTePk ((await CrEaTe_ProTo (fields )).hex (),packet_type ,key ,iv )

async def ghost_lvl_packet (player_id ,secret_code ,key ,iv ,region ):
    fields ={
    1 :61 ,
    2 :{
    1 :int (player_id ),
    2 :{
    1 :int (player_id ),
    2 :int (time .time ()),
    3 :"[FFFFFF]LVL",
    5 :12 ,
    6 :9999999 ,
    7 :1 ,
    8 :{2 :1 ,3 :1 },
    9 :3 ,
    },
    3 :secret_code ,
    },
    }
    if region .lower ()=="me":
        packet_type ='0514'
    elif region .lower ()=="bd":
        packet_type ="0519"
    elif region .lower ()=="ind":
        packet_type ='0514'
    else :
        packet_type ="0515"
    return await GeneRaTePk ((await CrEaTe_ProTo (fields )).hex (),packet_type ,key ,iv )

# ============================================================
# الدوال الإضافية للوضع "Lone Wolf / Attack" المستخدمة من telegram_bot.py
#   - start_auto_packet     : بدء المباراة تلقائياً (auto-start)
#   - attack_packet         : إرسال هجوم (دخول قيم)
#   - attack_in_squad_packet: فتح سكواد + بدء هجوم في حزمة واحدة
#   - open_squad_packet     : فتح سكواد جديد (للذئب الوحيد)
#   - send_invite_packet    : إرسال دعوة لعضو
#   - join_by_code_packet   : الانضمام بالكود
#   - try_parse_squad_code  : استخراج squad_code من حزمة protobuf
# ============================================================
async def start_auto_packet (key ,iv ,region ):
    """باكت بدء المباراة تلقائيًا (start_auto) — الدخول للجيم/القيم تلقائيًا."""
    fields ={1 :9 ,2 :{1 :12480598706 }}
    if region .lower ()=="me":
        packet_type ='0514'
    elif region .lower ()=="bd":
        packet_type ="0519"
    elif region .lower ()=="ind":
        packet_type ='0514'
    else :
        packet_type ="0515"
    return await GeneRaTePk ((await CrEaTe_ProTo (fields )).hex (),packet_type ,key ,iv )

async def attack_packet (key ,iv ,region ):
    """باكت الهجوم — يدخل البوت للمباراة بسرعة من داخل السكواد."""
    fields ={
    1 :9 ,
    2 :{
    1 :12480598706 ,
    2 :1 ,
    3 :1 ,
    4 :330 ,
    }
    }
    if region .lower ()=="me":
        packet_type ='0514'
    elif region .lower ()=="bd":
        packet_type ="0519"
    elif region .lower ()=="ind":
        packet_type ='0514'
    else :
        packet_type ="0515"
    return await GeneRaTePk ((await CrEaTe_ProTo (fields )).hex (),packet_type ,key ,iv )

async def attack_in_squad_packet (key ,iv ,region ):
    """باكت يجمع فتح السكواد + بدء الهجوم في حزمة واحدة."""
    fields ={
    1 :1 ,
    2 :{
    2 :"\u0001",3 :1 ,4 :1 ,5 :"en",
    9 :1 ,11 :1 ,13 :1 ,
    14 :{2 :5756 ,6 :11 ,8 :"1.111.5",9 :2 ,10 :4 },
    15 :1 ,
    16 :1 ,
    }
    }
    if region .lower ()=="me":
        packet_type ='0514'
    elif region .lower ()=="bd":
        packet_type ="0519"
    elif region .lower ()=="ind":
        packet_type ='0514'
    else :
        packet_type ="0515"
    return await GeneRaTePk ((await CrEaTe_ProTo (fields )).hex (),packet_type ,key ,iv )

async def open_squad_packet (key ,iv ,region ):
    """يفتح squad جديداً — الرد من السيرفر سيحتوي على squad_code."""
    fields ={
    1 :1 ,
    2 :{
    2 :"\u0001",
    3 :1 ,
    4 :1 ,
    5 :"en",
    9 :1 ,
    11 :1 ,
    13 :1 ,
    14 :{2 :5756 ,6 :11 ,8 :"1.111.5",9 :2 ,10 :4 }
    }
    }
    if region .lower ()=="me":
        packet_type ='0514'
    elif region .lower ()=="bd":
        packet_type ="0519"
    elif region .lower ()=="ind":
        packet_type ='0514'
    else :
        packet_type ="0515"
    return await GeneRaTePk ((await CrEaTe_ProTo (fields )).hex (),packet_type ,key ,iv )

async def send_invite_packet (invite_number ,target_uid ,key ,iv ,region ):
    """يرسل دعوة لـ target_uid للانضمام للـ squad الذي فتحه القائد."""
    fields ={1 :2 ,2 :{1 :int (target_uid ),2 :region ,4 :int (invite_number )}}
    if region .lower ()=="me":
        packet_type ='0514'
    elif region .lower ()=="bd":
        packet_type ="0519"
    elif region .lower ()=="ind":
        packet_type ='0514'
    else :
        packet_type ="0515"
    return await GeneRaTePk ((await CrEaTe_ProTo (fields )).hex (),packet_type ,key ,iv )

async def join_by_code_packet (code ,key ,iv ,region ):
    """عضو ينضم للـ squad باستخدام squad_code (نفس منطق join_teamcode_packet)."""
    fields ={
    1 :4 ,
    2 :{
    4 :bytes .fromhex ("01090a0b121920"),
    5 :str (code ),
    6 :6 ,
    8 :1 ,
    9 :{2 :800 ,6 :11 ,8 :"1.111.1",9 :5 ,10 :1 }
    }
    }
    if region .lower ()=="me":
        packet_type ='0514'
    elif region .lower ()=="bd":
        packet_type ="0519"
    elif region .lower ()=="ind":
        packet_type ='0514'
    else :
        packet_type ="0515"
    return await GeneRaTePk ((await CrEaTe_ProTo (fields )).hex (),packet_type ,key ,iv )

def try_parse_squad_code (plaintext_hex ):
    """يحاول استخراج squad_code من حزمة protobuf مفكوكة (hex نصي).
    يعيد None إذا فشل."""
    try :
        from protobuf_decoder .protobuf_decoder import Parser 
        parsed =Parser ().parse (plaintext_hex )
        def walk (results ,depth =0 ):
            for r in results :
                if r .wire_type =='length_delimited':
                    inner =walk (r .data .results ,depth +1 )
                    if inner :
                        return inner 
                elif r .wire_type =='string':
                    s =str (r .data )
                    if s .isalnum ()and 4 <=len (s )<=12 and any (c .isdigit ()for c in s ):
                        if s .lower ()not in ("en","ar","fr","br","me","ind","bd","or","me-en"):
                            return s 
            return None 
        return walk (parsed )
    except Exception :
        return None 

auto_running =False 
stop_auto =False 
auto_task =None 

LVL_CYCLE_BURSTS =99 
LVL_BURST_DELAY =0.10 
LVL_WAIT_FOR_RESPONSE =8.0 
LVL_BETWEEN_CYCLES =2.0 

async def wait_for_squad_data (timeout =LVL_WAIT_FOR_RESPONSE ):
    global last_squad_uid ,last_squad_code 
    last_squad_uid =None 
    last_squad_code =None 
    end =time .time ()+timeout 
    while time .time ()<end :
        if last_squad_uid is not None and last_squad_code is not None :
            return last_squad_uid ,last_squad_code 
        await asyncio .sleep (0.1 )
    return None ,None 

async def auto_lvl_loop (team_code ,uid ,chat_id ,chat_type ,key ,iv ,region ):
    global auto_running ,stop_auto ,last_squad_uid ,last_squad_code 
    cycle =0 
    print (f"[LVL] starting auto level for team_code={team_code } region={region }")
    while not stop_auto :
        try :
            cycle +=1 
            print (f"[LVL] cycle #{cycle }")

            last_squad_uid =None 
            last_squad_code =None 

            join_pkt =await join_teamcode_packet (team_code ,key ,iv ,region )
            await SEndPacKeT (whisper_writer ,online_writer ,'OnLine',join_pkt )

            idT ,sq =await wait_for_squad_data (LVL_WAIT_FOR_RESPONSE )

            if not idT or not sq :
                print (f"[LVL] failed to extract idT/sq for code={team_code }, retrying in 3s")
                await asyncio .sleep (3 )
                continue 

            print (f"[LVL] joined ok -> idT={idT } sq={sq }, spamming ghost packets...")

            for i in range (LVL_CYCLE_BURSTS ):
                if stop_auto :
                    break 
                try :
                    rejoin =await join_teamcode_packet (team_code ,key ,iv ,region )
                    await SEndPacKeT (whisper_writer ,online_writer ,'OnLine',rejoin )

                    ghost =await ghost_lvl_packet (idT ,sq ,key ,iv ,region )
                    await SEndPacKeT (whisper_writer ,online_writer ,'OnLine',ghost )

                    await asyncio .sleep (LVL_BURST_DELAY )

                    exit_pkt =await leave_squad_packet (idT ,key ,iv ,region )
                    await SEndPacKeT (whisper_writer ,online_writer ,'OnLine',exit_pkt )

                    ghost2 =await ghost_lvl_packet (idT ,sq ,key ,iv ,region )
                    await SEndPacKeT (whisper_writer ,online_writer ,'OnLine',ghost2 )
                except Exception as ge :
                    print (f"[LVL] burst err: {ge }")
                    break 

            if stop_auto :
                break 

            try :
                leave_pkt =await leave_squad_packet (idT ,key ,iv ,region )
                await SEndPacKeT (whisper_writer ,online_writer ,'OnLine',leave_pkt )
            except Exception :
                pass 

            await asyncio .sleep (LVL_BETWEEN_CYCLES )

        except Exception as e :
            print (f"[LVL] cycle error: {e }")
            traceback .print_exc ()
            await asyncio .sleep (2 )

    auto_running =False 
    stop_auto =False 
    print ("[LVL] auto stopped")

async def stop_auto_loop ():
    global auto_running ,stop_auto ,auto_task 
    stop_auto =True 
    if auto_task and not auto_task .done ():
        auto_task .cancel ()
        try :
            await auto_task 
        except asyncio .CancelledError :
            pass 
    auto_running =False 

async def safe_send_message (chat_type ,message ,target_uid ,chat_id ,key ,iv ,max_retries =3 ):
    for attempt in range (max_retries ):
        try :
            P =await SEndMsG (chat_type ,message ,target_uid ,chat_id ,key ,iv ,region )
            await SEndPacKeT (whisper_writer ,online_writer ,'ChaT',P )
            return True 
        except Exception :
            if attempt <max_retries -1 :
                await asyncio .sleep (0.5 )
    return False 

async def send_http_request (command_num ,target_uid ,sender_uid ,chat_id ,chat_type ,key ,iv ):
    try :
        url =f"http://127.0.0.1:5880/{command_num }?uid={target_uid }"
        async with aiohttp .ClientSession ()as session :
            async with session .get (url ,timeout =aiohttp .ClientTimeout (total =10 ))as resp :
                if resp .status ==200 :
                    response_text =await resp .text ()
                    if response_text and len (response_text )>150 :
                        response_text =response_text [:147 ]+"..."
                    return f"[B][C][00FF00]Command /{command_num } sent to {target_uid }\nResponse: {response_text if response_text else 'OK'}"
                else :
                    return f"[B][C][FF0000]Command /{command_num } failed: HTTP {resp .status }"
    except asyncio .TimeoutError :
        return f"[B][C][FF0000]Command /{command_num } timeout (10s)"
    except aiohttp .ClientConnectorError :
        return f"[B][C][FF0000]Cannot connect to 127.0.0.1:5880\nMake sure HTTP server is running"
    except Exception as e :
        return f"[B][C][FF0000]Error: {str (e )[:100 ]}"

async def TcPOnLine (ip ,port ,jwt_token ,bot_uid ,key ,iv ,AutHToKen ,reconnect_delay =0.5 ):
    global online_writer ,last_squad_uid ,last_squad_code 
    while True :
        try :
            reader ,writer =await asyncio .open_connection (ip ,int (port ))
            online_writer =writer 
            writer .write (bytes .fromhex (AutHToKen ))
            await writer .drain ()
            print (f"[ONLINE] connected {ip }:{port }")
            while True :
                data =await reader .read (9999 )
                if not data :
                    break 

                hex_data =data .hex ()

                if hex_data .startswith ("0500"):
                    try :
                        try :
                            decoded =await DeCode_PackEt (hex_data [10 :])
                        except Exception :
                            decoded =None 
                        if not decoded and "08"in hex_data :
                            try :
                                decoded =await DeCode_PackEt (f'08{hex_data .split ("08",1 )[1 ]}')
                            except Exception :
                                decoded =None 
                        if decoded :
                            dT =json .loads (decoded )
                            if "5"in dT and "data"in dT ["5"]:
                                team_data =dT ["5"]["data"]
                                if "31"in team_data and "data"in team_data ["31"]and "1"in team_data and "data"in team_data ["1"]:
                                    sq =team_data ["31"]["data"]
                                    idT =team_data ["1"]["data"]
                                    last_squad_uid =idT 
                                    last_squad_code =sq 
                                    print (f"[ONLINE] squad data parsed -> uid={idT }, sq={sq }")
                    except Exception as e :
                        pass 

            try :
                online_writer .close ()
                await online_writer .wait_closed ()
            except Exception :
                pass 
            online_writer =None 
        except Exception as e :
            print (f"[ONLINE] error: {e }")
            if online_writer :
                try :
                    online_writer .close ()
                    await online_writer .wait_closed ()
                except Exception :
                    pass 
                online_writer =None 
        await asyncio .sleep (reconnect_delay )

async def TcPChaT (ip ,port ,AutHToKen ,key ,iv ,LoGinDaTaUncRypTinG ,ready_event ,region ,reconnect_delay =0.5 ):
    global whisper_writer ,online_writer ,auto_running ,auto_task ,stop_auto 
    while True :
        try :
            reader ,writer =await asyncio .open_connection (ip ,int (port ))
            whisper_writer =writer 
            writer .write (bytes .fromhex (AutHToKen ))
            await writer .drain ()
            ready_event .set ()
            print (f"[CHAT] connected {ip }:{port }")

            if LoGinDaTaUncRypTinG .Clan_ID :
                clan_id =LoGinDaTaUncRypTinG .Clan_ID 
                clan_compiled_data =LoGinDaTaUncRypTinG .Clan_Compiled_Data 
                pK =await AuthClan (clan_id ,clan_compiled_data ,key ,iv )
                if whisper_writer :
                    writer .write (pK )
                    await writer .drain ()

            while True :
                data =await reader .read (9999 )
                if not data :
                    break 

                if data .hex ().startswith ("120000"):
                    try :
                        response =await DecodeWhisperMessage (data .hex ()[10 :])
                        uid =response .Data .uid 
                        chat_id =response .Data .Chat_ID 
                        inPuTMsG =response .Data .msg .strip ()
                        msg_lower =inPuTMsG .lower ()
                        print (f"Msg: '{inPuTMsG }' from {uid }")

                        if msg_lower .startswith ('/3 '):
                            parts =inPuTMsG .split ()
                            if len (parts )<2 :
                                await safe_send_message (response .Data .chat_type ,"[B][C][FF0000]Usage: /3 <target_uid>",uid ,chat_id ,key ,iv )
                                continue 
                            target_uid =parts [1 ]
                            reply =await send_http_request (3 ,target_uid ,uid ,chat_id ,response .Data .chat_type ,key ,iv )
                            await safe_send_message (response .Data .chat_type ,reply ,response .Data .uid ,chat_id ,key ,iv )

                        elif msg_lower .startswith ('/5 '):
                            parts =inPuTMsG .split ()
                            if len (parts )<2 :
                                await safe_send_message (response .Data .chat_type ,"[B][C][FF0000]Usage: /5 <target_uid>",uid ,chat_id ,key ,iv )
                                continue 
                            target_uid =parts [1 ]
                            reply =await send_http_request (5 ,target_uid ,uid ,chat_id ,response .Data .chat_type ,key ,iv )
                            await safe_send_message (response .Data .chat_type ,reply ,response .Data .uid ,chat_id ,key ,iv )

                        elif msg_lower .startswith ('/6 '):
                            parts =inPuTMsG .split ()
                            if len (parts )<2 :
                                await safe_send_message (response .Data .chat_type ,"[B][C][FF0000]Usage: /6 <target_uid>",uid ,chat_id ,key ,iv )
                                continue 
                            target_uid =parts [1 ]
                            reply =await send_http_request (6 ,target_uid ,uid ,chat_id ,response .Data .chat_type ,key ,iv )
                            await safe_send_message (response .Data .chat_type ,reply ,response .Data .uid ,chat_id ,key ,iv )

                        elif msg_lower .startswith ('/lw '):
                            parts =inPuTMsG .split ()
                            if len (parts )<2 :
                                await safe_send_message (response .Data .chat_type ,"[B][C][FF0000]Usage: /lw <team_code>",uid ,chat_id ,key ,iv )
                                continue 
                            team_code =parts [1 ]
                            if not team_code .isdigit ():
                                await safe_send_message (response .Data .chat_type ,"[B][C][FF0000]Team code must be numbers",uid ,chat_id ,key ,iv )
                                continue 
                            if auto_running :
                                await safe_send_message (response .Data .chat_type ,"[B][C][FF0000]Auto LVL already running. Use /stop_auto",uid ,chat_id ,key ,iv )
                                continue 
                            stop_auto =False 
                            auto_running =True 
                            await safe_send_message (response .Data .chat_type ,f"[B][C][00FF00]Auto LVL started for team {team_code }\nUse /stop_auto to stop",uid ,chat_id ,key ,iv )
                            auto_task =asyncio .create_task (auto_lvl_loop (team_code ,uid ,chat_id ,response .Data .chat_type ,key ,iv ,region ))

                        elif msg_lower .strip ()=='/stop_auto':
                            if auto_running :
                                await stop_auto_loop ()
                                await safe_send_message (response .Data .chat_type ,"[B][C][00FF00]Auto LVL stopped",uid ,chat_id ,key ,iv )
                            else :
                                await safe_send_message (response .Data .chat_type ,"[B][C][FF0000]No auto LVL running",uid ,chat_id ,key ,iv )

                        elif msg_lower .strip ()in ('/help','help','/menu','menu'):
                            help_msg =(
                            "[B][C][00FF00]------------------------\n"
                            "         BOT COMMANDS\n"
                            "------------------------\n"
                            "[FFFFFF]/lw <team_code>   [00FF00]- Auto LVL UP (real)\n"
                            "[FFFFFF]/stop_auto        [00FF00]- Stop auto LVL\n"
                            "[FFFFFF]/3 <uid>          [00FF00]- HTTP command 3\n"
                            "[FFFFFF]/5 <uid>          [00FF00]- HTTP command 5\n"
                            "[FFFFFF]/6 <uid>          [00FF00]- HTTP command 6\n"
                            "[FFFFFF]/help             [00FF00]- This menu\n"
                            "------------------------\n"
                            f"[00FF00]Developer : {LEVEL_UP }\n"
                            )
                            await safe_send_message (response .Data .chat_type ,help_msg ,uid ,chat_id ,key ,iv )

                    except Exception as e :
                        print (f"Decode error: {e }")
                        traceback .print_exc ()

            try :
                whisper_writer .close ()
                await whisper_writer .wait_closed ()
            except Exception :
                pass 
            whisper_writer =None 
        except Exception as e :
            print (f"[CHAT] error: {e }")
            if whisper_writer :
                try :
                    whisper_writer .close ()
                    await whisper_writer .wait_closed ()
                except Exception :
                    pass 
                whisper_writer =None 
        await asyncio .sleep (reconnect_delay )

async def MaiiiinE ():
    global CURRENT_BOT_UID ,region 
    if not os .path .exists ("bot.txt"):
        print ("bot.txt not found. Create it with {\"UID\": \"PASSWORD\"}")
        return None 
    with open ("bot.txt","r")as f :
        creds =json .load (f )
    if not creds :
        print ("bot.txt is empty or invalid JSON")
        return None 
    uid ,password =list (creds .items ())[0 ]
    print (f"Logging in with UID: {uid }")

    open_id ,access_token =await GeNeRaTeAccEss (uid ,password )
    if not open_id :
        print ("Failed to get open_id/access_token")
        return None 

    payload =await EncRypTMajoRLoGin (open_id ,access_token )
    login_resp =await MajorLogin (payload )
    if not login_resp :
        print ("MajorLogin failed")
        return None 
    auth =await DecRypTMajoRLoGin (login_resp )
    token =auth .token 
    if not token :
        print ("No token")
        return None 

    token_data ={
    "token":token ,
    "saved_at":time .time (),
    "timestamp":datetime .now ().strftime ("%Y-%m-%d %H:%M:%S"),
    "bot_uid":str (auth .account_uid ),
    "region":getattr (auth ,'region','me')
    }
    with open ("token.json","w")as f :
        json .dump (token_data ,f ,indent =2 )

    url =auth .url 
    region =getattr (auth ,'region','me')
    bot_uid =auth .account_uid 
    CURRENT_BOT_UID =str (bot_uid )
    key =auth .key 
    iv =auth .iv 
    timestamp =auth .timestamp 

    login_data =await GetLoginData (url ,payload ,token )
    if not login_data :
        print ("GetLoginData failed")
        return None 
    ports =await DecRypTLoGinDaTa (login_data )
    online_ip ,online_port =ports .Online_IP_Port .split (":")
    chat_ip ,chat_port =ports .AccountIP_Port .split (":")

    auth_token =await xAuThSTarTuP (int (bot_uid ),token ,int (timestamp ),key ,iv )

    ready =asyncio .Event ()
    task1 =asyncio .create_task (TcPChaT (chat_ip ,chat_port ,auth_token ,key ,iv ,ports ,ready ,region ))
    task2 =asyncio .create_task (TcPOnLine (online_ip ,online_port ,token ,bot_uid ,key ,iv ,auth_token ))

    print ("Bot online - Commands: /lw, /stop_auto, /3, /5, /6, /help")
    await asyncio .gather (task1 ,task2 )

async def StarTinG ():
    while True :
        try :
            await MaiiiinE ()
        except Exception as e :
            print (f"Restarting due to error: {e }")
            traceback .print_exc ()
            await asyncio .sleep (5 )

if __name__ =='__main__':
    asyncio .run (StarTinG ())
