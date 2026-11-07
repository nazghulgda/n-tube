# n-tube - video downloader

Video downloader for YouTube, Facebook, X and many other sites supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

There are two versions:
- `n-tube.py` - console version
- `n-tube-gui.py` - window version (GUI), works on Windows, Linux and macOS

Python 3 is needed to run scripts (GUI version needs also `tkinter`, on Linux it's a separate package, e.g. `python3-tk`).  
`ffmpeg` is installed together with requirements (`imageio-ffmpeg` package), there is no need to install it globally.  
Too long video titles are trimmed in file name (150 bytes), otherwise saving the file fails.

### Requirements files
- `requirements.txt` - packages for GUI version, used also by setup scripts for building the app
- `requirements-console.txt` - everything from `requirements.txt` plus JavaScript runtime `deno` (about 100 MB),
  without it some YouTube formats are missing (usually the best quality ones)

The app built by setup and build scripts doesn't contain `deno`.

`yt-dlp` and `deno` have no version in requirements, so the newest version is always installed - YouTube and other sites
change things often and only the newest yt-dlp works with them. Other packages have fixed versions.

### Console version
Install requirements: `pip install -U -r requirements-console.txt`  
Run the same command from time to time to update yt-dlp and deno.  
Run script by `python n-tube.py` command, paste link to video,
wait for download to be finished and input 1 to download next video or
input 0 to end the script. Any other answer repeats the question.  
Videos are saved in your `Downloads` folder.  
Link has to start with `http://` or `https://`, otherwise script asks for it again. If the video can't be downloaded
(wrong link, video not available) script shows a message and asks if you want to download next video.

### GUI version
Install requirements: `pip install -U -r requirements.txt` (run it also to update yt-dlp) and run by `python n-tube-gui.py`, paste link to video
and click `Download` (or press Enter).
Progress bar shows download progress, messages from yt-dlp are shown in the window below.
When video is downloaded and merged a popup will show up, after clicking OK you can paste next link.  
Videos are saved in your `Downloads` folder, it can be changed with `Browse...` button (not during download).  
Wrong link or video that can't be downloaded shows a message, after clicking OK you can paste next link.  
If the window is closed during download, download is stopped and `.part` files are removed.

### yt-dlp self-update (built app only)
At start the app checks on PyPI if there is newer yt-dlp than the one it uses. If yes, it is downloaded in the background
(checksum is verified) and used from the next start of the app - no need to build the app again.
The used yt-dlp version is shown in the first line of the log.

Updates are saved in:
- Windows - `%LOCALAPPDATA%\n-tube\yt-dlp`
- Linux - `~/.local/share/n-tube/yt-dlp`
- macOS - `~/Library/Application Support/n-tube/yt-dlp`

Only the newest one is kept. If downloaded yt-dlp can't be loaded, the app removes it and uses the bundled one.
If the app is built again with newer yt-dlp, older updates are removed. Deleting the folder is safe, it's downloaded again.  
ATT: the app contains only Python modules used by yt-dlp at build time. If newer yt-dlp needs something more,
build the app again.  
Script version (`python n-tube-gui.py`) doesn't update itself, it uses yt-dlp installed by pip.

### Cookies
Some videos (age restricted, private, needing login) can be downloaded only with cookies from the browser.
Uncomment `'cookiesfrombrowser': ('firefox',),` line in the script (in GUI version in `dwl_vid`) and be logged in
to the site in Firefox. Other browsers can be used too, e.g. `('chrome',)`.

### Building standalone app
App contains everything (python, ffmpeg), so it can be copied to another computer and run without installing anything.

| System  | Setup               | Build               | Result                    |
|---------|---------------------|---------------------|---------------------------|
| Windows | `setup.bat`         | `build.bat`         | `dist\n-tube.exe`         |
| Linux   | `./setup_lin.sh`    | `./build_lin.sh`    | `dist/n-tube`, `dist/n-tube.png`, `dist/install_lin.sh` |
| macOS   | `./setup_macos.sh`  | `./build_macos.sh`  | `dist/n-tube.app`, `dist/n-tube-macos.zip` |

Setup creates virtual environment `.venv` and installs (or updates) `requirements.txt` and PyInstaller into it.  
Build updates yt-dlp to the newest version before building, so the app always contains the newest yt-dlp.  
`setup_lin.sh` installs `python3-venv` and `python3-tk` with `sudo` if they are missing.  
`setup_macos.sh` needs Python from python.org or Homebrew (it installs `python-tk` for Homebrew Python if needed).

Icons are in `assets` folder. Only icons used by the app are included in the build (Windows - `n-tube.ico`,
Linux and macOS - png 16-256 px, macOS `.icns` is made from png files during build).

On Linux run `dist/install_lin.sh` to add app with icon to the menu (copy `n-tube`, `n-tube.png`
and `install_lin.sh` together to another computer). App is installed for the current user only (`~/.local`),
`sudo` is not needed. `install_lin.sh --uninstall` removes it (together with downloaded yt-dlp updates).  
It removes also old version of the app (`yt-downloader`).  
If the menu still shows the old name after install, log out and log in again (on KDE `kbuildsycoca6` is enough).

ATT:
- app has to be built on the system it is made for, it is not possible to build Linux or macOS version on Windows
- close the app before running build again, otherwise build will fail
- macOS build is not tested yet
- on macOS app is not signed, so first time it has to be opened by right click -> Open
- on Windows Explorer can show old icon of the exe because of its icon cache, renaming or moving the file helps
- the app needs internet access to PyPI (pypi.org) for yt-dlp self-update, without it the app works with the version it has

That's all for now ;)
