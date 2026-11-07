# n-tube - video downloader

Video downloader for YouTube, Facebook, X and many other sites supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

There are two versions:
- `pull-yt-video.py` - console version
- `pull-yt-video-gui.py` - window version (GUI), works on Windows, Linux and macOS

`ffmpeg` is installed together with requirements (`imageio-ffmpeg` package), there is no need to install it globally.  
Too long video titles are trimmed in file name (150 bytes), otherwise saving the file fails.

### Console version
Install requirements: `pip install -r requirements.txt`  
Run script by `python pull-yt-video.py` command, paste link to video,
wait for download to be finished and input 1 to download next video or
input 0 to end the script.  
Videos are saved in the current folder.

### GUI version
Install requirements (as above) and run by `python pull-yt-video-gui.py`, paste link to video and click `Download`.
When video is downloaded and merged a popup will show up, after clicking OK you can paste next link.  
Videos are saved in your `Downloads` folder, it can be changed with `Browse...` button.

### Building standalone app
App contains everything (python, ffmpeg), so it can be copied to another computer and run without installing anything.

| System  | Setup               | Build               | Result                    |
|---------|---------------------|---------------------|---------------------------|
| Windows | `setup.bat`         | `build.bat`         | `dist\yt-downloader.exe`  |
| Linux   | `./setup_lin.sh`    | `./build_lin.sh`    | `dist/yt-downloader`, `dist/yt-downloader.png`, `dist/install_lin.sh` |
| macOS   | `./setup_macos.sh`  | `./build_macos.sh`  | `dist/yt-downloader.app`, `dist/yt-downloader-macos.zip` |

Icons are in `assets` folder.  
`setup_lin.sh` installs `python3-venv` and `python3-tk` with `sudo` if they are missing.

On Linux run `dist/install_lin.sh` to add app with icon to the menu (copy `yt-downloader`, `yt-downloader.png`
and `install_lin.sh` together to another computer). `install_lin.sh --uninstall` removes it.

ATT:
- app has to be built on the system it is made for, it is not possible to build Linux or macOS version on Windows
- close the app before running build again, otherwise build will fail
- macOS build is not tested yet
- on macOS app is not signed, so first time it has to be opened by right click -> Open
- yt-dlp has to be updated from time to time (`pip install -U yt-dlp`) and app built again, because sites change things

That's all for now ;)
