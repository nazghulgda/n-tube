import yt_dlp
import imageio_ffmpeg

ydl_opts = {
    'nocheckcertificate': True,
    'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
    # 'paths': {'home': 'downloads'},
    # too long file name = error
    'outtmpl': '%(title).150B [%(id)s].%(ext)s',
    # 'cookiesfrombrowser': ('firefox',),
}
# without 'nocheckcertificate': True script will return an error

def dwl_vid(video_url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

channel = 1
while channel == 1:
    link_of_the_video = input("Copy & paste the URL of the video you want to download: ")
    zxt = link_of_the_video.strip()

    dwl_vid(zxt)
    channel = int(input("Enter 1 if you want to download more videos\nEnter 0 if you are done: "))