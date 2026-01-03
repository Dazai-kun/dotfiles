#!/bin/bash

source "$CONFIG_DIR/colors.sh"

# METHOD 1: Check System Input Source
# reliable if OpenKey is used as an Input Source
SYSTEM_LAYOUT=$(defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources | grep -w 'KeyboardLayout Name' | sed -E 's/^.+ = "?([^"]+)"?;$/\1/')

if [ -z "$SYSTEM_LAYOUT" ]; then
  SYSTEM_LAYOUT=$(defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources | grep -w 'InputModeName' | sed -E 's/^.+ = "?([^"]+)"?;$/\1/')
fi

# METHOD 2: Check OpenKey Internal State
# 1 = Vietnamese, 0 = English
# We use 'defaults read' on the domain 'com.tuyenmai.openkey' (not the file path) to try and get the cached value
OPENKEY_METHOD=$(defaults read com.tuyenmai.openkey InputMethod 2>/dev/null)

LABEL="ENG" # Default

# Logic
if [[ "$SYSTEM_LAYOUT" == *"Vietnamese"* ]] || [[ "$SYSTEM_LAYOUT" == *"OpenKey"* ]]; then
  LABEL="VN"
elif [ "$OPENKEY_METHOD" = "1" ]; then
  # OpenKey is in Vietnamese mode
  LABEL="VN"
elif [ "$OPENKEY_METHOD" = "0" ]; then
  # OpenKey is in English mode
  LABEL="ENG"
else
  # Fallback to system layout first 3 chars
  LABEL="${SYSTEM_LAYOUT:0:3}"
fi

# Set the icon and label
if [ "$LABEL" = "VN" ]; then
  sketchybar --set "$NAME" label="VN" icon="􀇳" label.color="$ACCENT" icon.color="$ACCENT"
else
  sketchybar --set "$NAME" label="ENG" icon="􀇳" label.color="$FOREGROUND" icon.color="$FOREGROUND"
fi