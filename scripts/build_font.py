#!/usr/bin/env python3
# Rebuild the localization font: map each Shift-JIS codepoint to its Traditional-Chinese
# glyph drawn in Noto Sans CJK TC (黑體). Leaves mes.ARC untouched.
import sys
from fontTools.ttLib import TTFont, TTCollection, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.subset import Subsetter, Options
import opencc

BUND="/home/anr2/game/kawa/build/汉化补丁 GPT3.5/ＭＳ ゴシック.otf"
NOTO="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
OUT=sys.argv[1] if len(sys.argv)>1 else "/home/anr2/game/kawa/build/MSGothic-TC.otf"
cc=opencc.OpenCC('s2tw')

def isideo(o): return 0x4e00<=o<=0x9fff or 0x3400<=o<=0x4dbf or 0xf900<=o<=0xfaff
def conv(d):
    if isideo(ord(d)):
        t=cc.convert(d); return t[0] if t else d
    return d

# 1) bundled cmap -> displayed char D, target Traditional T
b=TTFont(BUND,fontNumber=0); bc=b.getBestCmap()
CtoD={}; CtoT={}
for C,g in bc.items():
    if g.startswith('uni') and len(g)>=7:
        try: D=chr(int(g[3:7],16))
        except: D=chr(C)
    else:
        D=chr(C)
    CtoD[C]=D; CtoT[C]=conv(D)
print(f"bundled codepoints: {len(CtoT)}")

# 2) subset Noto TC to needed target unicodes
noto=TTCollection(NOTO).fonts[3]   # Noto Sans CJK TC
target=set()
for C in CtoT:
    target.add(ord(CtoT[C])); target.add(ord(CtoD[C]))
opts=Options(); opts.glyph_names=True; opts.notdef_outline=True; opts.name_IDs=['*']; opts.name_legacy=True; opts.recalc_bounds=True; opts.drop_tables=[]
ss=Subsetter(options=opts); ss.populate(unicodes=target); ss.subset(noto)
ncmap=noto.getBestCmap()
print(f"noto subset glyphs, cmap entries: {len(ncmap)}")

# 3) new cmap C -> noto glyph for T (fallback D)
newmap={}; miss=0
for C,T in CtoT.items():
    gn=ncmap.get(ord(T)) or ncmap.get(ord(CtoD[C]))
    if gn: newmap[C]=gn
    else: miss+=1
print(f"mapped {len(newmap)} codepoints, {miss} unmapped")

# 4) replace cmap
cmap=newTable('cmap'); cmap.tableVersion=0
s4=CmapSubtable.getSubtableClass(4)(4); s4.platformID=3; s4.platEncID=1; s4.format=4; s4.language=0
s4.cmap={c:g for c,g in newmap.items() if c<=0xFFFF}
s12=CmapSubtable.getSubtableClass(12)(12); s12.platformID=3; s12.platEncID=10; s12.format=12; s12.language=0; s12.reserved=0; s12.length=0; s12.nGroups=0
s12.cmap=dict(newmap)
cmap.tables=[s4,s12]; noto['cmap']=cmap

# 5b) tighten vertical metrics so the (em-inset) Noto glyphs FILL the engine's
#     fixed text cell. The engine asks GDI for a POSITIVE cell height and scales the
#     font so (winAscent+winDescent) maps to it. Noto's default 1448 (1.45x em) left
#     CJK glyphs at only ~65% of the cell -> looked tiny. The original 漢化 font used
#     winAscent+winDescent == em (256) so its glyphs filled the cell. Measured the
#     real ink of the glyphs we actually draw: CJK ideographs span y[-90,853], common
#     fullwidth punctuation (、。「」（）：；) span y[-103,858]. So 860/110 fits every
#     real glyph and fills the cell -> ~1.49x bigger than before, no clipping of text
#     (only Latin accents / g j | descenders clip, and those never appear in the CN text).
ASC, DESC = 860, 110
os2=noto['OS/2']; hhea=noto['hhea']
os2.usWinAscent=ASC; os2.usWinDescent=DESC
os2.sTypoAscender=ASC; os2.sTypoDescender=-DESC; os2.sTypoLineGap=0
hhea.ascent=ASC; hhea.descent=-DESC; hhea.lineGap=0
os2.fsSelection &= ~(1<<7)        # clear USE_TYPO_METRICS -> GDI uses the win metrics above

# 5) rename family to MS Gothic / ＭＳ ゴシック so the hook keeps loading it
name=noto['name']
for pid,eid,lid in [(3,1,0x409),(3,1,0x411),(1,0,0)]:
    name.setName("MS Gothic" if lid!=0x411 else "ＭＳ ゴシック",1,pid,eid,lid)
    name.setName("MS Gothic" if lid!=0x411 else "ＭＳ ゴシック",4,pid,eid,lid)
    name.setName("Regular",2,pid,eid,lid)
    name.setName("MSGothicTC",6,pid,eid,lid)
noto.save(OUT)
print("saved",OUT)
