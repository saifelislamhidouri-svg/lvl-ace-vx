

import asyncio 
import json 
import time 
import logging 
from typing import Optional ,Dict 

from protobuf_decoder .protobuf_decoder import Parser 


from xHeaders import (
OpEnSq ,cHSq ,SEnd_InV ,GenJoinSquadsPacket ,ExiT ,Fix_PackEt 
)

log =logging .getLogger ("squad")


async def parse_incoming_packet (data_bytes :bytes )->Optional [dict ]:

    try :
        hex_text =data_bytes .hex ()
        parsed =Parser ().parse (hex_text )
        result =await Fix_PackEt (parsed )
        return result 
    except Exception as e :
        log .debug (f"parse_incoming_packet failed: {e }")
        return None 


def _extract_str (d ,*keys ):

    cur =d 
    for k in keys :
        if not isinstance (cur ,dict ):
            return None 
        if k not in cur :
            return None 
        cur =cur [k ]
        if isinstance (cur ,dict )and "data"in cur :
            inner =cur ["data"]
            cur =inner 
    return cur 


async def try_extract_squad_code (parsed :dict )->Optional [str ]:

    try :
        d5 =parsed .get ("5",{}).get ("data",{})
        if not isinstance (d5 ,dict ):
            return None 

        if "31"in d5 :
            v =d5 ["31"].get ("data")
            if v :
                return str (v )

        d3 =d5 .get ("3",{}).get ("data",{})if isinstance (d5 .get ("3"),dict )else {}
        if isinstance (d3 ,dict )and "31"in d3 :
            v =d3 ["31"].get ("data")
            if v :
                return str (v )

        if "17"in d5 :
            v =d5 ["17"].get ("data")
            if v :
                return str (v )
    except Exception as e :
        log .debug (f"try_extract_squad_code failed: {e }")
    return None 


class SquadCoordinator :


    def __init__ (self ):
        self .squad_code :Optional [str ]=None 
        self .leader_uid :Optional [str ]=None 

        self .code_ready :asyncio .Event =asyncio .Event ()

        self ._lock =asyncio .Lock ()

    def reset (self ):
        self .squad_code =None 
        self .leader_uid =None 
        self .code_ready =asyncio .Event ()

    async def set_code (self ,code :str ,leader_uid :str ):
        async with self ._lock :
            self .squad_code =str (code )
            self .leader_uid =str (leader_uid )
            self .code_ready .set ()
            log .info (f"[Squad] squad_code={code } leader={leader_uid }")

    async def wait_for_code (self ,timeout :float =15.0 )->Optional [str ]:
        try :
            await asyncio .wait_for (self .code_ready .wait (),timeout =timeout )
            return self .squad_code 
        except asyncio .TimeoutError :
            return None 


async def send_open_squad (worker )->bool :

    try :
        pkt =await OpEnSq (worker ._key ,worker ._iv ,worker ._region )
        if worker ._online_writer is None :
            return False 
        worker ._online_writer .write (pkt )
        await worker ._online_writer .drain ()
        return True 
    except Exception as e :
        log .exception (f"send_open_squad failed: {e }")
        return False 


async def send_invite (worker ,invite_number :int ,target_uid :int )->bool :

    try :
        pkt =await SEnd_InV (invite_number ,int (target_uid ),
        worker ._key ,worker ._iv ,worker ._region )
        if worker ._online_writer is None :
            return False 
        worker ._online_writer .write (pkt )
        await worker ._online_writer .drain ()
        return True 
    except Exception as e :
        log .exception (f"send_invite failed: {e }")
        return False 


async def join_squad_by_code (worker ,code :str )->bool :

    try :
        pkt =await GenJoinSquadsPacket (code ,worker ._key ,worker ._iv )
        if worker ._online_writer is None :
            return False 
        worker ._online_writer .write (pkt )
        await worker ._online_writer .drain ()
        return True 
    except Exception as e :
        log .exception (f"join_squad_by_code failed: {e }")
        return False 


async def leave_squad (worker )->bool :

    try :

        pkt =await ExiT (int (worker .uid ),worker ._key ,worker ._iv )
        if worker ._online_writer is None :
            return False 
        worker ._online_writer .write (pkt )
        await worker ._online_writer .drain ()
        return True 
    except Exception as e :
        log .debug (f"leave_squad failed: {e }")
        return False 
