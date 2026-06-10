import struct,re,os
from fontTools.ttLib import TTFont
import opencc
cc=opencc.OpenCC('s2tw'); ccj=opencc.OpenCC('jp2t')
BASE='/home/anr2/game/kawa/build/汉化补丁 GPT3.5'
font=TTFont(BASE+'/ＭＳ ゴシック.otf',fontNumber=0); cmap=font.getBestCmap()
def disp(cp):
    g=cmap.get(cp)
    if g and g.startswith('uni') and len(g)>=7:
        try:return chr(int(g[3:7],16))
        except:return chr(cp)
    return chr(cp)
mes=open(BASE+'/mes.ARC','rb').read()
n=struct.unpack('<I',mes[:4])[0];off=4;ents=[]
for i in range(n):
    rec=mes[off:off+40];off+=40
    nm=rec[:32].split(b'\x00')[0].decode('ascii','replace')
    o,s=struct.unpack('<II',rec[32:40]);ents.append((nm,o,s))
def is_text(disp_s):
    if len(disp_s)<2:return False
    cjk=sum(1 for c in disp_s if 0x3000<=ord(c)<=0x9fff or 0xff00<=ord(c)<=0xffef)
    return cjk>=max(2,len(disp_s)*0.6)
total=0; out=[]
# only event/story files (skip pure data like ALLPIC/DEFINE which are mostly opcodes)
for nm,o,s in ents:
    blob=mes[o:o+s]
    runs=re.findall(rb'(?:[\x81-\xfe][\x40-\xfe]){2,}',blob)
    lines=[]
    for r in runs:
        sj=r.decode('cp932','replace')
        d=''.join(disp(ord(c)) for c in sj)
        if is_text(d):
            t=ccj.convert(cc.convert(d)).rstrip('　 ')   # strip trailing fullwidth padding
            if t: lines.append(t)
    if lines:
        out.append(f"\n===== {nm} =====")
        out+=lines; total+=len(lines)
hdr=f"河原崎家の一族 XP — 對話/文字紀錄（繁體中文）\n由 mes.ARC 抽出，共 {len(ents)} 個 .MES 檔、{total} 段文字。\n字型 glyph 還原 + OpenCC s2tw 繁化。可能含少量系統字串。\n"
open('/home/anr2/game/kawa/對話紀錄_繁中.txt','w').write(hdr+'\n'.join(out))
print(f"wrote 對話紀錄_繁中.txt: {total} text segments, {len(out)} lines")
