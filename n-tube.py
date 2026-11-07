from pathlib import Path
from urllib.parse import urlparse

import deno
import yt_dlp
import imageio_ffmpeg
from yt_dlp.utils import DownloadError

folder = Path.home() / 'Downloads'

ydl_opts = {
    'nocheckcertificate': True,
    'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
    # without JavaScript runtime some YouTube formats are missing
    'js_runtimes': {'deno': {'path': deno.find_deno_bin()}},
    'paths': {'home': str(folder)},
    # too long file name = error
    'outtmpl': '%(title).150B [%(id)s].%(ext)s',
    # 'cookiesfrombrowser': ('firefox',),
}
# without 'nocheckcertificate': True script will return an error

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