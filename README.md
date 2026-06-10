# kawa_pkg

《河原崎家の一族 XP》(elf, 1993) **繁體中文版**打包紀錄 — Linux **AppImage** 與 **Windows zip**。

> ⚠️ **不含遊戲檔。** 本 repo 只有食譜、腳本與 Claude Code skill；
> 遊戲本體、漢化 patch、字型、成品（AppImage/zip）都不在此（見 `.gitignore`）。

## 內容

- **`SKILL.md`** — Claude Code skill：完整食譜與所有踩過的坑（最重要的檔案）。
- **`scripts/build_font.py`** — 把漢化字型重建成繁體黑體的核心腳本
  （讀 cmap 的 glyph 名稱還原顯示字 → OpenCC `s2tw` → 用 Noto Sans CJK TC Bold 重建）。
- **`scripts/AppRun`** — AppImage 啟動器（首次建 wine prefix、重試啟動、自動按掉光碟視窗、自動全螢幕）。
- **`scripts/answer-cd.sh`、`scripts/kawa-stop.sh`** — 開發/除錯用：wine 下啟動並自動回答光碟視窗、清乾淨並還原螢幕。
- **`windows/啟動遊戲.bat`、`windows/說明.txt`** — Windows 版啟動器與說明（設安裝機碼後開 AI.exe）。

## 一句話原理

不是中文程式，而是**日文引擎 (Shift-JIS/CP932) + 自訂字型 hook**；
漢化把中文存成 Shift-JIS 碼位，字型 cmap 的 glyph 名稱 `uniXXXX` 就藏著它顯示的簡體字，
據此用 OpenCC 轉繁、用 Noto TC 重建字型即可（`mes.ARC` 完全不動）。細節見 `SKILL.md`。

## 安裝成 skill

```bash
git clone https://github.com/wicanr2/kawa_pkg.git ~/.claude/skills/kawarazaki-zhtw
```

由 Claude Code 自動產生與整理。
