#!/usr/bin/env python3
"""elf .gcc image codec (G24n/G24m) + gcc.ARC (un)pack — for UI localization.
Format: 12-byte header [sig 'G24n'/'G24m' | OffsetX i16@4 | OffsetY i16@6 | W u16@8 | H u16@10],
color data starts at 0x14 (G24n) or 0x20 (G24m); LZSS-compressed BGR24, vertically flipped.
G24m also has an alpha mask after the color; header[0x0C] = color compressed length (MUST be
updated if you re-encode the color). Re-encode color as all-literal LZSS and append the original
alpha bytes untouched (works because W*H*3 % 8 == 0 for these images). LZSS = classic 4KB ring,
init pos 0xFEE, LSB-first ctrl, bit=1 literal; offset=((hi&0xF0)<<4)|lo, count=(hi&0xF)+3."""
import struct
def lzss_decompress(data, out_len):
    out=bytearray(); fr=bytearray(0x1000); fp=0xFEE; p=0; n=len(data)
    while len(out)<out_len and p<n:
        c=data[p]; p+=1
        for _ in range(8):
            if len(out)>=out_len: break
            if c&1: b=data[p]; p+=1; out.append(b); fr[fp]=b; fp=(fp+1)&0xFFF
            else:
                lo=data[p]; hi=data[p+1]; p+=2; o=((hi&0xF0)<<4)|lo; k=(hi&0xF)+3
                for i in range(k): b=fr[(o+i)&0xFFF]; out.append(b); fr[fp]=b; fp=(fp+1)&0xFFF
            c>>=1
    return bytes(out[:out_len]), p   # also returns input bytes consumed
def lzss_literals(data):             # all-literal stream (no compression, always valid)
    o=bytearray(); i=0
    while i<len(data): ch=data[i:i+8]; i+=8; o.append((1<<len(ch))-1); o+=ch
    return bytes(o)
def parse_arc(arc):                  # -> [(name, offset, size)]
    n=struct.unpack('<I',arc[:4])[0]; off=4; ents=[]
    for _ in range(n):
        r=arc[off:off+40]; off+=40
        nm=r[:32].split(b'\x00')[0].decode('ascii','replace')
        o,s=struct.unpack('<II',r[32:40]); ents.append((nm,o,s))
    return ents
def repack_arc(arc, replacements):   # replacements: {name: new_bytes} -> new arc bytes
    n=struct.unpack('<I',arc[:4])[0]; ents=parse_arc(arc)
    out=bytearray(struct.pack('<I',n)); cur=4+40*n; toc=bytearray(); datas=[]
    for nm,o,s in ents:
        d=replacements.get(nm, arc[o:o+s]); datas.append(d)
        z=nm.encode('ascii'); z+=b'\x00'*(32-len(z)); toc+=z+struct.pack('<II',cur,len(d)); cur+=len(d)
    out+=toc
    for d in datas: out+=d
    return bytes(out)
