#!/usr/bin/env bash
# Find our path via npm because BASH_SOURCE won't work under npm scripts… ಠ_ಠ
DIR="$(npm ls --global --parseable imagemagick-macos-font-setup)"
TYPE_GEN_SCRIPT="$DIR/vendor/imagemagick_type_gen"
echo "<----- Ensuring $HOME/.config/ImageMagick exists"
mkdir -p "$HOME/.config/ImageMagick"
echo "<----- Writing font definition to $HOME/.config/ImageMagick/type.xml"
find "$PWD/lib/fonts" -type f -name '*.ttf' | "$TYPE_GEN_SCRIPT" -f - > "$HOME/.config/ImageMagick/type.xml"
