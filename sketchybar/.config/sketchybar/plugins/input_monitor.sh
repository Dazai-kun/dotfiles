#!/bin/bash

source "$CONFIG_DIR/colors.sh"

LAST_LABEL=""

while true; do
  # METHOD 1: Check System Input Source
  SYSTEM_LAYOUT=$(defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources | grep -w 'KeyboardLayout Name' | sed -E 's/^.+ = "?([^"]+)"?;$/\1/')

  if [ -z "$SYSTEM_LAYOUT" ]; then
    SYSTEM_LAYOUT=$(defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources | grep -w 'InputModeName' | sed -E 's/^.+ = "?([^"]+)"?;$/\1/')
  fi

  # METHOD 2: Check OpenKey Internal State
  OPENKEY_METHOD=$(defaults read com.tuyenmai.openkey InputMethod 2>/dev/null)

  LABEL="ENG"

  # Logic
  if [[ "$SYSTEM_LAYOUT" == *"Vietnamese"* ]] || [[ "$SYSTEM_LAYOUT" == *"OpenKey"* ]]; then
    LABEL="VN"
  elif [ "$OPENKEY_METHOD" = "1" ]; then
    LABEL="VN"
  elif [ "$OPENKEY_METHOD" = "0" ]; then
    LABEL="ENG"
  else
    LABEL="${SYSTEM_LAYOUT:0:3}"
  fi

  # Only update if changed
  if [ "$LABEL" != "$LAST_LABEL" ]; then
    if [ "$LABEL" = "VN" ]; then
      sketchybar --set input label="VN" icon="􀇳" label.color="$ACCENT" icon.color="$ACCENT"
    else
      sketchybar --set input label="ENG" icon="􀇳" label.color="$FOREGROUND" icon.color="$FOREGROUND"
    fi
    LAST_LABEL="$LABEL"
  fi

  sleep 0.5
done
