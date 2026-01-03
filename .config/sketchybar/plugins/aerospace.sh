#!/bin/bash

source "$CONFIG_DIR/colors.sh"

# Add a small staggered delay based on the workspace name to prevent race conditions
# in sketchybar's background rendering when multiple spaces update at once.
# This fixes the "glitched border" issue.
sleep "0.$(echo "$1" | cksum | cut -c1-2)"

if [ -z "$FOCUSED_WORKSPACE" ]; then
  FOCUSED_WORKSPACE=$(aerospace list-workspaces --focused)
fi

# Get apps for this workspace and create icon strip
apps=$(aerospace list-windows --workspace "$1" | awk -F '|' '{gsub(/^ *| *$/, "", $2); if (!seen[$2]++) print $2}' | sort)

icon_strip=""
if [ "${apps}" != "" ]; then
  while read -r app; do
    icon_strip+=" $("$CONFIG_DIR"/plugins/icons.sh "$app")"
  done <<<"${apps}"
fi

if [ "$1" = "$FOCUSED_WORKSPACE" ]; then
  sketchybar --set "$NAME" \
    background.color="${ACCENT}" \
    icon.color="${BACKGROUND}" \
    icon.font.style="Bold" \
    icon="$(echo "$1" | cut -d'_' -f1)" \
    label="$icon_strip" \
    label.color="${BACKGROUND}" \
    label.font="sketchybar-app-font:Regular:12.0" \
    label.y_offset=-1 \
    drawing=on
else
  if [ "${apps}" != "" ]; then
    sketchybar --set "$NAME" \
      background.color="${TRANSPARENT}" \
      icon.color="${ACCENT}" \
      icon.font.style="Bold" \
      icon="$(echo "$1" | cut -d'_' -f1)" \
      label="$icon_strip" \
      label.color="${ACCENT}" \
      label.font="sketchybar-app-font:Regular:12.0" \
      label.y_offset=-1 \
      drawing=on
  else
    sketchybar --set "$NAME" drawing=off
  fi
fi
