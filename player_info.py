

import json 
import ssl 
import binascii 
import asyncio 
import logging 
from typing import Optional ,Dict ,Any 

import aiohttp 
from Crypto .Cipher import AES 
from Crypto .Util .Padding import pad 

from gta import EnC_Uid ,DeCode_PackEt 

log =logging .getLogger ("player-info")


_AES_KEY =bytes ([89 ,103 ,38 ,116 ,99 ,37 ,68 ,69 ,117 ,104 ,54 ,37 ,90 ,99 ,94 ,56 ])
_AES_IV =bytes ([54 ,111 ,121 ,90 ,68 ,114 ,50 ,50 ,69 ,51 ,121 ,99 ,104 ,106 ,77 ,37 ])

_PERSONAL_SHOW_HOSTS =[
"https://clientbp.common.ggbluefox.com/GetPlayerPersonalShow",
"https://clientbp.ggblueshark.com/GetPlayerPersonalShow",
]


def _aes_encrypt (hex_str :str )->bytes :
    cipher =AES .new (_AES_KEY ,AES .MODE_CBC ,_AES_IV )
    return cipher .encrypt (pad (bytes .fromhex (hex_str ),AES .block_size ))


async def fetch_player_info (in_game_uid :int ,jwt_token :str ,ob_version :str ="OB52")->Optional [Dict [str ,Any ]]:

    try :
        uid_hex =await EnC_Uid (int (in_game_uid ),Tp ='Uid')
        payload_hex =f"08{uid_hex }1007"
        body =_aes_encrypt (payload_hex )
    except Exception as e :
        log .error (f"build payload failed: {e }")
        return None 

    headers_base ={
    'X-Unity-Version':'2018.4.11f1',
    'Content-Type':'application/x-www-form-urlencoded',
    'X-GA':'v1 1',
    'Authorization':f'Bearer {jwt_token }',
    'User-Agent':'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
    'Connection':'Keep-Alive',
    'Accept-Encoding':'gzip',
    }

    ssl_ctx =ssl .create_default_context ()
    ssl_ctx .check_hostname =False 
    ssl_ctx .verify_mode =ssl .CERT_NONE 

    last_err =None 
    for url in _PERSONAL_SHOW_HOSTS :
        for ob in (ob_version ,"OB52","OB51","OB50"):
            try :
                headers =dict (headers_base )
                headers ['ReleaseVersion']=ob 
                timeout =aiohttp .ClientTimeout (total =12 )
                async with aiohttp .ClientSession (timeout =timeout )as sess :
                    async with sess .post (url ,headers =headers ,data =body ,ssl =ssl_ctx )as resp :
                        if resp .status not in (200 ,201 ):
                            last_err =f"HTTP {resp .status } on {url }"
                            continue 
                        raw =await resp .read ()
                        if not raw :
                            last_err ="empty response"
                            continue 
                        hex_packet =binascii .hexlify (raw ).decode ('utf-8')
                        decoded_json =await DeCode_PackEt (hex_packet )
                        if not decoded_json :
                            last_err ="decode failed"
                            continue 
                        data =json .loads (decoded_json )
                        info =_extract_info (data )
                        if info :
                            return info 
                        last_err ="no fields extracted"
            except Exception as e :
                last_err =str (e )
                continue 
    log .warning (f"fetch_player_info failed for {in_game_uid }: {last_err }")
    return None 


def _safe_get (d :Any ,*path ):

    cur =d 
    for k in path :
        if not isinstance (cur ,dict ):
            return None 
        cur =cur .get (k )
        if cur is None :
            return None 
    return cur 


def _extract_info (data :dict )->Optional [Dict [str ,Any ]]:

    out :Dict [str ,Any ]={}
    try :
        profile =_safe_get (data ,"1","data")
        if not isinstance (profile ,dict ):
            return None 


        uid_v =_safe_get (profile ,"1","data")
        if uid_v is not None :
            try :
                out ["uid"]=int (uid_v )
            except Exception :
                out ["uid"]=str (uid_v )


        name_v =_safe_get (profile ,"3","data")
        if name_v :
            out ["name"]=str (name_v )


        lvl_v =_safe_get (profile ,"6","data")
        if lvl_v is not None :
            try :
                out ["level"]=int (lvl_v )
            except Exception :
                pass 


        for cand in ("7","8","9","11"):
            v =_safe_get (profile ,cand ,"data")
            if isinstance (v ,(int ,float ))and 0 <=v <10_000_000 :

                if v in (out .get ("uid"),out .get ("level")):
                    continue 
                out .setdefault ("exp",int (v ))


        likes_v =_safe_get (profile ,"21","data")
        if likes_v is not None :
            try :
                out ["likes"]=int (likes_v )
            except Exception :
                pass 


        region_v =_safe_get (profile ,"5","data")
        if region_v :
            out ["region"]=str (region_v )

        return out if out else None 
    except Exception as e :
        log .debug (f"_extract_info error: {e }")
        return None 


def calc_xp_progress (level :int ,exp :Optional [int ])->Optional [int ]:

    if not exp or not level or level <=0 :
        return None 
    try :
        needed =max (1000 ,level *1000 )
        pct =int ((exp %needed )*100 /needed )
        return max (0 ,min (100 ,pct ))
    except Exception :
        return None 
