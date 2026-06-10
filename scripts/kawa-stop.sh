#!/bin/bash
export DISPLAY=:1
pkill -9 -f 'XP-繁中' 2>/dev/null
pkill -9 -f 'mount_河原' 2>/dev/null
pkill -9 -f 'AI.exe' 2>/dev/null
pkill -9 wineserver 2>/dev/null
pkill -9 winedevice 2>/dev/null
sleep 2
xrandr --output eDP-1 --scale 1x1 2>/dev/null
xrandr --output eDP-1 --mode 1920x1200 2>/dev/null
sleep 1
echo "res: $(xrandr 2>/dev/null | grep 'eDP-1 connected' | awk '{print $4}')"
echo "ai.exe: $(ps -C AI.exe -o pid= 2>/dev/null | wc -l)  appimage: $(pgrep -f 'XP-繁中' >/dev/null && echo Y || echo N)"
