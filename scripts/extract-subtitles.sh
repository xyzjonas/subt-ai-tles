#!/usr/bin/env bash
# Extract embedded text subtitles from video files into <name>.<lang>.srt
# Usage: extract-subtitles.sh <directory>
# Requires: ffmpeg, ffprobe
set -euo pipefail

dir="${1:-.}"

for tool in ffmpeg ffprobe; do
  command -v "$tool" >/dev/null || { echo "missing dependency: $tool" >&2; exit 1; }
done

# Text-based codecs that can be converted to SRT (bitmap ones like PGS/VobSub cannot)
text_codecs="subrip srt ass ssa mov_text webvtt text"

# ISO 639-2 (3-letter, as used by mkv) -> ISO 639-1 (2-letter)
iso2() {
  case "$1" in
    eng) echo en;; ger|deu) echo de;; fre|fra) echo fr;; spa) echo es;;
    ita) echo it;; por) echo pt;; dut|nld) echo nl;; rus) echo ru;;
    jpn) echo ja;; chi|zho) echo zh;; kor) echo ko;; ara) echo ar;;
    swe) echo sv;; nor) echo no;; dan) echo da;; fin) echo fi;;
    pol) echo pl;; cze|ces) echo cs;; tur) echo tr;; gre|ell) echo el;;
    heb) echo he;; hun) echo hu;; ukr) echo uk;; rum|ron) echo ro;;
    hin) echo hi;; tha) echo th;; vie) echo vi;; ind) echo id;;
    *) echo "$1";;
  esac
}

find "$dir" -type f \( -iname '*.mkv' -o -iname '*.mp4' -o -iname '*.m4v' -o -iname '*.webm' -o -iname '*.avi' -o -iname '*.mov' \) -print0 |
while IFS= read -r -d '' file; do
  base="${file%.*}"
  echo "==> $file"

  # one line per subtitle stream: <stream index>,<codec>,<language>
  # (stream index is the absolute index; language tag may be absent)
  streams=$(ffprobe -v error -select_streams s \
    -show_entries stream=index,codec_name:stream_tags=language \
    -of csv=p=0 "$file" 2>/dev/null || true)

  if [[ -z "$streams" ]]; then
    echo "    no subtitle streams"
    continue
  fi

  while IFS=, read -r index codec lang; do
    [[ -z "$index" ]] && continue

    if [[ " $text_codecs " != *" $codec "* ]]; then
      echo "    stream $index ($codec): bitmap/unsupported, skipping"
      continue
    fi

    if [[ -z "$lang" || "$lang" == "und" ]]; then
      lang="und"
      echo "    stream $index: no language tag, using 'und'"
    else
      lang=$(iso2 "$lang")
    fi

    out="$base.$lang.srt"
    # never overwrite; this also means only the first track per language is kept
    if [[ -e "$out" ]]; then
      echo "    $out exists, skipping"
      continue
    fi

    if ffmpeg -v error -nostdin -n -i "$file" -map "0:$index" -c:s srt "$out"; then
      echo "    stream $index -> $out"
    else
      echo "    stream $index: extraction failed" >&2
      rm -f "$out"
    fi
  done <<< "$streams"
done
