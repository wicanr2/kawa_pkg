#!/bin/bash
# Launch the game and dismiss the CD prompt by choosing いいえ (No), trying several
# input methods until the game window appears. Captures the game window on success.
export WINEPREFIX="/home/anr2/game/kawa/build/prefix" DISPLAY=:1
export LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8
export WINEDLLOVERRIDES="winmm=n,b;d2d1=n,b;mscoree,mshtml=" WINEDEBUG=fixme-all,err-all

pkill -9 -f "Kawa/AI.exe" 2>/dev/null; wineserver -k 2>/dev/null; sleep 1
# remove the CD-ROM override (back to no CD -> normal prompt flow)
rm -f "$WINEPREFIX/dosdevices/d:" "$WINEPREFIX/dosdevices/d::"

cd "$WINEPREFIX/drive_c/Kawa" || exit 1
nohup wine AI.exe >/tmp/kawa-run.log 2>&1 &

find_dialog(){ xdotool search --class "ai.exe" 2>/dev/null | while read w; do [ "$(xdotool getwindowname "$w" 2>/dev/null)" = "AI" ] && echo "$w"; done | head -1; }
find_game(){ for w in $(xdotool search --class "ai.exe" 2>/dev/null); do eval "$(xdotool getwindowgeometry --shell "$w" 2>/dev/null)"; n=$(xdotool getwindowname "$w" 2>/dev/null); [ "$n" != "Default IME" ] && [ "${WIDTH:-0}" -ge 600 ] && { echo "$w"; return; }; done; }

method=0
for t in $(seq 1 30); do
  sleep 0.7
  g=$(find_game); [ -n "$g" ] && { echo "GAME=$g (method=$method t=$t)"; break; }
  d=$(find_dialog); [ -z "$d" ] && continue
  eval "$(xdotool getwindowgeometry --shell "$d" 2>/dev/null)"
  nx=$(( ${X:-0} + WIDTH*73/100 )); ny=$(( ${Y:-0} + HEIGHT*82/100 ))
  rx=$(( WIDTH*73/100 )); ry=$(( HEIGHT*82/100 ))
  case $((t % 4)) in
    0) method="activate+altN"; xdotool windowactivate --sync "$d" 2>/dev/null; [ "$(xdotool getactivewindow 2>/dev/null)" = "$d" ] && xdotool key --clearmodifiers alt+n ;;
    1) method="synthclick"; xdotool mousemove --window "$d" "$rx" "$ry" 2>/dev/null; xdotool click --window "$d" 1 2>/dev/null ;;
    2) method="focus+nav"; xdotool windowfocus "$d" 2>/dev/null; xdotool key --window "$d" --clearmodifiers Right; xdotool key --window "$d" --clearmodifiers Return ;;
    3) method="realclick"; xdotool windowactivate "$d" 2>/dev/null; xdotool mousemove "$nx" "$ny" click 1 2>/dev/null ;;
  esac
done
g=$(find_game)
if [ -n "$g" ]; then
  sleep 2
  import -window "$g" /tmp/game_shot.png 2>/dev/null
  convert /tmp/game_shot.png -scale 175% /tmp/game_shot_big.png 2>/dev/null
  echo "CAPTURED via $method"
else
  echo "FAILED (alive=$(pgrep -f 'Kawa/AI.exe' >/dev/null && echo Y || echo N))"
fi
