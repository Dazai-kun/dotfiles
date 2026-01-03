#!/bin/bash

source "$CONFIG_DIR/colors.sh"
source "$CONFIG_DIR/icon_map.sh"

# Get the focused workspace
FOCUSED_WORKSPACE=$(aerospace list-workspaces --focused)

# Get all workspaces
ALL_WORKSPACES=$(aerospace list-workspaces --all)

# Initialize the sketchybar command
BATCH_CMD="sketchybar"

# 1. Pre-calculate icons.
RAW_WINDOWS_DATA=$(aerospace list-windows --all --format %{workspace}%{app-name} --json | jq -r '.[] | "\(.workspace)|\(."app-name")"' | sort -u)

# Function to get icons for a specific workspace
get_icons_for_workspace() {
  local ws="$1"
  local icons=""
  while IFS='|' read -r w app; do
    if [ "$w" = "$ws" ] && [ -n "$app" ]; then
      __icon_map "$app"
      icons+=" $icon_result"
    fi
  done <<< "$RAW_WINDOWS_DATA"
  echo "$icons"
}

# 2. Build the batch command
for sid in $ALL_WORKSPACES; do
  icon_strip=$(get_icons_for_workspace "$sid")
  
  if [ "$sid" = "$FOCUSED_WORKSPACE" ]; then
    # Minimalist: Just change the color to ACCENT, no background
    BATCH_CMD+=" --set space.$sid \
      background.drawing=off \
      icon.color=$ACCENT \
      label.color=$ACCENT \
      icon.font.style=Bold \
      label=\"$icon_strip\" \
      label.font=\"sketchybar-app-font:Regular:12.0\" \
      label.y_offset=-1 \
      drawing=on"
  else
    if [ -n "$icon_strip" ]; then
      # Minimalist: Normal color (FOREGROUND)
      BATCH_CMD+=" --set space.$sid \
        background.drawing=off \
        icon.color=$FOREGROUND \
        label.color=$FOREGROUND \
        icon.font.style=Bold \
        label=\"$icon_strip\" \
        label.font=\"sketchybar-app-font:Regular:12.0\" \
        label.y_offset=-1 \
        drawing=on"
    else
      BATCH_CMD+=" --set space.$sid drawing=off"
    fi
  fi
done

# Execute the batch command
eval "$BATCH_CMD"