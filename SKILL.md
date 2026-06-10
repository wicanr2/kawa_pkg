---
name: kawarazaki-zhtw
description: 把 elf《河原崎家の一族 XP》(1993) 從「簡體 AI 漢化」轉成繁體中文，並打包成 Linux AppImage 與 Windows zip 的完整工具鏈與陷阱。當使用者談到「河原崎家の一族」「河原崎一族」「Kawarazakike no Ichizoku」「KAWAXP-CD」「这家遊戲跑不起來/未安裝」「elf 日文遊戲漢化 wine」「Shift-JIS 漢化字型」「漢化字型 glyph 名稱 uniXXXX」「簡體轉繁體 OpenCC 重建字型」「日文 eroge wine AppImage 打包」等情境觸發。
---

# 河原崎家の一族 XP 繁中化 + 打包

把這個 1993 年 elf 文字冒險（XP 重製版，含「GPT3.5 簡體 AI 漢化」）：
1. 在 Linux 用 wine 跑起來，
2. 把簡體轉成**繁體中文**、字型換成清楚的**黑體**，
3. 打包成 **AppImage**（Linux）與 **Windows zip**（解壓即玩）。

成品（不放在本 repo，含遊戲檔）放在 `/home/anr2/game/kawa/`：
`河原崎家の一族XP-繁中.AppImage`、`河原崎家の一族XP_繁中_Windows.zip`。
原始 RAR（`Kawarazakike no Ichizoku XP [elf] [1993] (iso).rar`）也在那裡。

## ⚠️ 最關鍵、最反直覺的事

**這不是中文程式，而是「日文引擎 (Shift-JIS / CP932) ＋ 中文字型 hook」。**

- 引擎是日文的。必須以 `LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8` 執行（wine 內部對應 CP932），
  否則所有引擎對話框（含「放入光碟」「未安裝」）都是亂碼。
  host 沒有 `ja_JP.UTF-8` locale 也沒關係，wine 會自己對應（setlocale 警告可忽略）。
- 漢化把中文文字存成 **Shift-JIS 的碼位**（不是 GBK！），再靠一個**自訂字型**
  把這些碼位畫成中文字。字型偽裝成日文的「ＭＳ ゴシック」（`ＭＳ ゴシック.otf`）。
- **解開繁體轉換的鑰匙**：用 fontTools 看那字型的 cmap，每個碼位對應的 glyph **名稱**
  就是 `uniXXXX` —— 那 `XXXX` 正是它實際顯示的**簡體字**的 Unicode！
  例：碼位 U+69C7(槇) → glyph `uni5427`(吧)、U+9F9C(龜) → `uni5417`(吗)。

## 繁體 + 換字型（核心，見 `scripts/build_font.py`）

不動 `mes.ARC`（避免 offset 風險），只**重建字型**：

1. 讀漢化字型 cmap：每個碼位 C → glyph 名稱 → 取出它顯示的簡體字 D。
2. `OpenCC('s2tw')` 把 D 轉成繁體 T（台灣用字，逐字 1:1）。
3. 用 **Noto Sans CJK TC**（subfont index 3）的 glyph 重建：新字型 cmap 把 C 指向 T 的 glyph。
4. 字型名稱設回「MS Gothic / ＭＳ ゴシック」，存成 `windows/Fonts/msgothic.otf`
   （wine 下 hook 載入遊戲目錄字型會因全形檔名失敗 → fallback 到系統字型，所以放這）。
5. 字重用 **Regular**（`NotoSansCJK-Regular.ttc`，`build_font.py` 預設）。
   （曾改 Bold 想讓全螢幕放大時更清楚，但使用者偏好 Regular，最終用 Regular。）
6. **字身高度 metrics（讓字填滿字格＝看起來變大，關鍵！）**：引擎用**正的** `lfHeight`
   叫 GDI 畫字，GDI 把字型的 `usWinAscent+usWinDescent` 映射到那個字格高度。Noto 預設此值
   ＝**1.45×em（1448/1000）**，使中文字只填字格 ~65% → 看起來很小（這是「字太小」的真兇，
   **不是**字型家族問題）。原始漢化字型則設成剛好 `1×em`（256/256）讓字填滿格。
   修法：量出實際會畫到的字墨範圍（漢字 y[-90,853]、全形標點 `、。「」（）：；` y[-103,858]），
   把重建字型設 `usWinAscent=860 / usWinDescent=110`（同步 typo/hhea，並清掉 `fsSelection`
   的 USE_TYPO_METRICS bit7）→ 字幾乎填滿格、**比原本大約 1.49×**，且不裁切任何真會出現的字
   （只裁 Latin 重音/`g j |` 下緣，中文文本不會用到）。見 `build_font.py` 的 `ASC,DESC=860,110`。

需要：`pip install --user opencc`、`python3-fonttools`、host 有 Noto Sans CJK（`fonts-noto-cjk`）。
建一次字型約 2 分鐘、產出 ~12MB OTF。

## 讓遊戲跑起來（wine）的四個坑

1. **編碼**：`LANG=ja_JP.UTF-8`（見上）。
2. **免光碟安裝機碼**：no-CD `AI.exe` 會檢查
   `HKLM\Software\elf\KAWAXP-CD` 或 `HKCU\...` 的 `InstExec` 值；沒有就跳「ゲームが
   インストールされていません」。設成指向遊戲目錄的 `AI.exe`（`C:\Kawa\AI.exe`）即可，
   **不必跑 Install.exe**。
3. **放入光碟視窗**：啟動會跳「『DISC』のCDを…」Yes/No 視窗，要按**「いいえ(No)」**
   才會從硬碟跑（crack 把 No 改成「從硬碟執行」）。
4. **冷啟動不穩**：引擎是單一實例，殘留 wineserver 狀態會讓新啟動**靜默結束**(exit 0、空 log)。
   每次啟動前 `wineserver -k` + **重試最多 5 次**才穩。

DLL override：`WINEDLLOVERRIDES="winmm=n,b;d2d1=n,b;mscoree,mshtml="`（載入漢化 hook、關 gecko/mono）。
GUI 字型 substitute（讓對話框可讀）：把 MS Shell Dlg/Tahoma/System → `Noto Sans CJK TC`。

## 放大畫面（字太小）

引擎固定 640×480、字格大小固定。**換字型「家族」不會變大**（量過 OS 裡 Noto/WenQuanYi/
Droid/UMing… 同字級字框幾乎一樣，差 <2%）——但 **字型的 `winAscent/winDescent` metrics 會！**
見上面「繁體+換字型」第 6 點：把字型 metrics 收緊讓字填滿字格，已讓字 **~1.49× 變大且不放大螢幕**
（這是先做的、效果最好的一步）。要再更大才需要整桌面縮放：
`gamescope`（能做視窗 nearest 縮放）在 Ubuntu 22.04 裝不起來（apt/snap 都沒有、要自己編）。

**AppRun 預設＝不動螢幕**（使用者最後要求「不要放大螢幕」），遊戲就跑原生 640×480 視窗（小）。
放大是**選用**：設 `KAWA_SCALE` 才會用 `xrandr --output <OUT> --scale SxS --filter nearest`
（nearest = 銳利不糊）整桌面放大，結束/中斷 `--scale 1x1` 還原（trap EXIT/INT/TERM）。
- 例：`KAWA_SCALE=0.42`（≈2.4x，幾乎填滿、清晰）。
- **下限約 0.41**：framebuffer 高 = 1200×SCALE 必須 ≥ 視窗 500px，否則字幕框底部被切。
- 缺點：xrandr scale 會放大**整個桌面**（使用者不喜歡，故不設成預設）；要乾淨的單視窗縮放需 gamescope（裝不起來）。

**字體大小/銳利度**：字小是先天（引擎固定 cell，字型已填滿 cell；換字型/字級無法變大）。
若不放大螢幕又嫌「糊」，把字渲染成**無反鋸齒的銳利點陣**：first-run 設
`HKCU\Control Panel\Desktop` `FontSmoothing=0`（REG_SZ）、`FontSmoothingType=0`（DWORD），
GDI 就以 1-bit 渲染 → 原生 ~16px 的清晰像素字（接近原版 16×16 點陣字感）。AppRun 已內建。

引擎自帶全螢幕（會糊、~3x）：選單「ウィンドウ」→「ウィンドウ最大化」
（DirectDraw 切 640×480 exclusive、面板 bilinear 放大；wine 結束自動還原）。
xdotool 自動：點選單列 x≈90 開「ウィンドウ」→ 點彈出選單第 2 項「最大化」。
（使用者比較過：要清楚就 nearest 縮放，要更大就全螢幕但糊；最後選 nearest 縮放。）

## GUI 自動化小技巧（在被遮擋的桌面上）

- `import -window <id>`（ImageMagick）可**穿透遮擋**直接截某視窗內容。
- 按掉 wine 視窗的按鈕：`xdotool windowactivate --sync <id>` 確認 `getactivewindow` 後送鍵，
  或更可靠的 `xdotool mousemove --window <id> X Y; xdotool click --window <id> 1`（合成事件，
  即使被終端機遮擋也能點到）。

## 打包

- **AppImage**（`scripts/AppRun` + appimagetool）：用**系統 wine**（不內建 wine，太大太脆）。
  只放遊戲資料 + 字型 + AppRun；首次執行才在 `~/.local/share/kawarazaki-no-ichizoku/`
  建 prefix、複製遊戲、裝字型、設機碼。AppRun 內含：重試啟動、自動按 No、自動全螢幕、結束還原解析度。
  build：`ARCH=x86_64 ./appimagetool.AppImage AppDir <out>.AppImage`
- **Windows zip**：把打好漢化的遊戲資料夾 + `winmm.dll`/`d2d1.dll`（漢化 hook）+ Bold 繁體
  `ＭＳ ゴシック.otf` + `windows/啟動遊戲.bat`（設機碼後開 AI.exe）+ `說明.txt` + `vc_redist.x86.exe`
  （備援；漢化 DLL 需要 MSVCP140/VCRUNTIME140，多數 Windows 已內建）打包。
  Windows 上 hook 會正確載入遊戲目錄的全形檔名字型 → 直接顯示繁體 Bold。
  ⚠️ 只能在 Linux/wine 組裝驗證遊戲邏輯，**無法在真 Windows 測**，需使用者實測。

## UI 圖中文化（選單/按鈕）＋ .gcc 圖檔格式

UI 文字（指令選單/標題選單/存讀檔/CG 鑑賞等）是燒在 `gcc.ARC` 的圖片裡（不是字串），
elf 專有「G24n/G24m」格式。已逆向完成，見 `scripts/gcc_codec.py`：
- `gcc.ARC` = 跟 mes.ARC 同 TOC（count + 40-byte records）；裡面是 `.gcc` 圖。
- `.gcc`：12-byte header（sig G24n/G24m、OffsetX@4、OffsetY@6、W@8、H@10），
  色彩資料從 0x14(G24n)/0x20(G24m) 起，**LZSS**(4KB ring, init 0xFEE, LSB ctrl, bit=1=literal,
  off=((hi&0xF0)<<4)|lo, cnt=(hi&0xF)+3) 壓的 **BGR24、上下顛倒**。
- **G24m 有 alpha mask** 接在色彩後；header **0x0C = 色彩壓縮長度**。重編時：色彩用
  all-literal LZSS 重壓（W*H*3 % 8 == 0 故乾淨）+ **原樣接回 alpha bytes** + **更新 0x0C**。不必重編 alpha。
- 編輯法：解碼成 RGB → 找按鈕格（多狀態 sprite sheet：黑/青/紅 bg 或金色漸層）→ **逐列取樣 bg 色擦掉日文**
  （漸層安全）→ 用 Noto Sans CJK TC Bold 置中畫繁中（白字或自動對比色）→ 重編 → repack。
- 已做：menu(指令選單)、title_pt(標題)、r_menu(右鍵金色選單)、cg_pt(CG)、sl_save/sl_load。
  未做（量大/低頻）：setting(設定滑桿)、soundk_pt(~20 BGM 曲名)、edk_pt、backlog。
- 上方 Win32 menu bar（ゲームの終了/ウィンドウ…）字串找不到（packed/engine），未解。

## 抽全部對話成文字（`scripts/extract_dialogue.py`）

mes.ARC 每個 .MES 找 SJIS 雙位元組 run → 用字型 glyph 名稱 uniXXXX 還原**顯示字**（簡體）→
OpenCC `s2tw` 再 `jp2t`（清掉日文新字体如 満→滿、経→經、説→說）→ 依 .MES 分段輸出 `對話紀錄_繁中.txt`。

## 重新製作的順序

1. `unrar x <rar>`：取得 BIN/CUE、`汉化补丁 GPT3.5/`、`免CD补丁/`、`全CG存档/`。
2. `7z x <bin>`（MODE1/2048 = ISO）取遊戲檔，排除 `directx9b`/`ie60`/installer。
3. 套 no-CD（`AI.exe`/`AI.ini`，ROM=1）、套漢化（`mes.ARC`/`winmm.dll`/`d2d1.dll`/字型）。
4. `scripts/build_font.py` 重建 Bold 繁體字型。
5. 組 AppDir，`appimagetool` 打 AppImage；組 Windows 資料夾打 zip。
