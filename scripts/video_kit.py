#!/usr/bin/env python3
"""Turn an owned screen recording into a 1080p video with FFmpeg.
This is a local post-production helper; it does not capture, publish, or clone videos.
"""
import argparse, pathlib, shutil, subprocess, sys
p=argparse.ArgumentParser(description='Local screen-recording export; FFmpeg required')
p.add_argument('--input',required=True)
p.add_argument('--output',required=True)
p.add_argument('--mode',choices=['long','short'],default='long')
a=p.parse_args()
if not shutil.which('ffmpeg'):sys.exit('FFmpeg not found. Install it first: https://ffmpeg.org/download.html')
src=pathlib.Path(a.input).resolve(); dst=pathlib.Path(a.output).resolve()
if not src.is_file() or src.suffix.lower() not in ('.mp4','.mov','.mkv','.webm'):sys.exit('Input must be your existing video file')
if src==dst:sys.exit('Input and output must be different files')
if dst.exists():sys.exit('Output already exists; choose another path')
dst.parent.mkdir(parents=True,exist_ok=True)
if a.mode=='long':
    # Pad—not crop—so the entire original screen remains visible.
    vf='scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x102e24,setsar=1'
else:
    # Never crop away the UI automatically. Explicitly review readability after export.
    vf='scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x102e24,setsar=1'
cmd=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-i',str(src),'-vf',vf,
     '-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-y',str(dst)]
print('Rendering',a.mode,'from owned footage; inspect visual and audio before upload')
try:subprocess.run(cmd,check=True)
except subprocess.CalledProcessError as e:sys.exit(f'FFmpeg failed: {e.returncode}')
print('Created:',dst)
