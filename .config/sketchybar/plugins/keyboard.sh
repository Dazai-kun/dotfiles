#!/bin/bash

# Get the current keyboard layout
# We try 'KeyboardLayout Name' first (standard layouts)
# If empty, we try 'InputModeName' (IMEs like Vietnamese, Chinese, etc.)
LAYOUT=$(defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources | grep -w 'KeyboardLayout Name' | sed -E 's/^.+ = "?([^"]+)"?;$/\1/')

if [ -z "$LAYOUT" ]; then
  LAYOUT=$(defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources | grep -w 'InputModeName' | sed -E 's/^.+ = "?([^"]+)"?;$/\1/')
fi

# Mapping for nicer labels
case "$LAYOUT" in
  "ABC") LABEL="ENG" ;;
  "U.S.") LABEL="ENG" ;;
  "Vietnamese") LABEL="VN" ;;
  "OpenKey") LABEL="VN" ;; # Guessing OpenKey's identifier
  *) LABEL="${LAYOUT:0:3}" ;; # Fallback: first 3 chars
esac

sketchybar --set "$NAME" label="$LABEL" icon="􀇳"
