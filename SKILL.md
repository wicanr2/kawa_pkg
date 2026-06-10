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
5. **用 Bold**（`NotoSansCJK-Bold.ttc`）：640×480 放大時粗體比 Regular 清楚很多。

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

## 放大畫面

引擎固定 640×480。`gamescope` 在 Ubuntu 22.04 裝不起來（apt/snap 都沒有、要自己編）。
最後用**引擎自帶全螢幕**：選單「ウィンドウ」→「ウィンドウ最大化」
（DirectDraw 切 640×480 exclusive、面板放大填滿；遊戲結束 wine 自動還原解析度，比 xrandr scale 安全）。
AppRun 用 xdotool 自動：點選單列 x≈90 開「ウィンドウ」→ 點彈出選單第 2 項「最大化」。
（`xrandr --output X --scale 0.5 --filter nearest` 可做整桌面 2x 銳利縮放，但使用者不要。）
全螢幕的糊是先天：640×480 被拉大 ~3 倍；Bold 字型已盡量補救。

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

## 重新製作的順序

1. `unrar x <rar>`：取得 BIN/CUE、`汉化补丁 GPT3.5/`、`免CD补丁/`、`全CG存档/`。
2. `7z x <bin>`（MODE1/2048 = ISO）取遊戲檔，排除 `directx9b`/`ie60`/installer。
3. 套 no-CD（`AI.exe`/`AI.ini`，ROM=1）、套漢化（`mes.ARC`/`winmm.dll`/`d2d1.dll`/字型）。
4. `scripts/build_font.py` 重建 Bold 繁體字型。
5. 組 AppDir，`appimagetool` 打 AppImage；組 Windows 資料夾打 zip。
