from pathlib import Path
from urllib.parse import urlparse

import deno
import yt_dlp
import imageio_ffmpeg
from yt_dlp.utils import DownloadError

folder = Path.home() / 'Downloads'

ydl_opts = {
    'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
    # always .mp4 in the highest resolution, H.264/AAC preferred at the same resolution
    # (plays everywhere), above 1080p YouTube has only VP9/AV1 - remuxed to .mp4, not re-encoded
    'format_sort': ['res', 'vcodec:h264', 'acodec:aac'],
    'merge_output_format': 'mp4',
    'postprocessors': [{'key': 'FFmpegVideoRemuxer', 'preferedformat': 'mp4'}],
    # without JavaScript runtime some YouTube formats are missing
    'js_runtimes': {'deno': {'path': deno.find_deno_bin()}},
    # solver scripts from GitHub when yt-dlp-ejs doesn't match yt-dlp version
    'remote_components': ['ejs:github'],
    'paths': {'home': str(folder)},
    # too long file name = error
    'outtmpl': '%(title).150B [%(id)s].%(ext)s',
    # 'cookiesfrombrowser': ('firefox',),
}

def is_valid_url(url):
    parts = urlparse(url)
    return parts.scheme in ('http', 'https') and '.' in parts.netloc

def dwl_vid(video_url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def ask_next():
    while True:
        answer = input("Enter 1 if you want to download more videos\nEnter 0 if you are done: ").strip()
        if answer in ('0', '1'):
            return answer == '1'

print(f"Videos are saved to: {folder}")
channel = True
while channel:
    link_of_the_video = input("Copy & paste the URL of the video you want to download: ")
    zxt = link_of_the_video.strip()
    if not is_valid_url(zxt):
        print("This is not a valid link, it has to start with http:// or https://")
        continue

    try:
        dwl_vid(zxt)
    except DownloadError:
        print("Wrong link or the video is not available.")
    channel = ask_next()