import asyncio
import json
from protobuf_decoder.protobuf_decoder import Parser

# --- دوال التشفير الأساسية (مطلوبة من XcT.py و player_info.py) ---
async def EnC_AEs(HeX):
    # هذه الدالة غير مستخدمة بشكل مباشر لكن可能存在 استدعاء
    return HeX

async def EnC_Uid(H, Tp):
    e, H = [], int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0))
        H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

async def DeCode_PackEt(input_text):
    try:
        parsed = Parser().parse(input_text)
        result = await Fix_PackEt(parsed)
        return json.dumps(result)
    except Exception as e:
        print(f"DeCode_PackEt error: {e}")
        return None

async def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {'wire_type': result.wire_type}
        if result.wire_type in ("varint", "string", "bytes"):
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = await Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

# --- دوال إضافية قد تحتاجها XcT.py (مثل xMsGFixinG) ---
def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i+3] for i in range(0, len(str(n)), 3))

# دوال فارغة لتجنب أخطاء الاستيراد إذا استدعيت
async def EnC_Vr(N):
    return b''

async def CrEaTe_ProTo(fields):
    return b''

async def GeneRaTePk(Pk, N, K, V):
    return b''

async def EnC_PacKeT(hex_str, K, V):
    return hex_str

def DEc_Uid(H):
    return 0