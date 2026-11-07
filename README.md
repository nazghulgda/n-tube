# n-tube - video downloader

Video downloader for YouTube, Facebook, X and many other sites supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

There are two versions:
- `n-tube.py` - console version
- `n-tube-gui.py` - window version (GUI), works on Windows, Linux and macOS

`ffmpeg` is installed together with requirements (`imageio-ffmpeg` package), there is no need to install it globally.  
Too long video titles are trimmed in file name (150 bytes), otherwise saving the file fails.

### Console version
Install requirements: `pip install -r requirements-console.txt`  
It installs also JavaScript runtime (`deno`), without it some YouTube formats are missing. GUI version doesn't have it.  
Run script by `python n-tube.py` command, paste link to video,
wait for download to be finished and input 1 to download next video or
input 0 to end the script.  
Videos are saved in your `Downloads` folder.

### GUI version
Install requirements: `pip install -r requirements.txt` and run by `python n-tube-gui.py`, paste link to video and click `Download`.
When video is downloaded and merged a popup will show up, after clicking OK you can paste next link.  
Videos are saved in your `Downloads` folder, it can be changed with `Browse...` button.

### Building standalone app
App contains everything (python, ffmpeg), so it can be copied to another computer and run without installing anything.

| System  | Setup               | Build               | Result                    |
|---------|---------------------|---------------------|---------------------------|
| Windows | `setup.bat`         | `build.bat`         | `dist\n-tube.exe`         |
| Linux   | `./setup_lin.sh`    | `./build_lin.sh`    | `dist/n-tube`, `dist/n-tube.png`, `dist/install_lin.sh` |
| macOS   | `./setup_macos.sh`  | `./build_macos.sh`  | `dist/n-tube.app`, `dist/n-tube-macos.zip` |

Icons are in `assets` folder.  
`setup_lin.sh` installs `python3-venv` and `python3-tk` with `sudo` if they are missing.

On Linux run `dist/install_lin.sh` to add app with icon to the menu (copy `n-tube`, `n-tube.png`
and `install_lin.sh` together to another computer). `install_lin.sh --uninstall` removes it.  
It removes also old version of the app (`yt-downloader`).

ATT:
- app has to be built on the system it is made for, it is not possible to build Linux or macOS version on Windows
- close the app before running build again, otherwise build will fail
- macOS build is not tested yet
- on macOS app is not signed, so first time it has to be opened by right click -> Open
- yt-dlp has to be updated from time to time (`pip install -U yt-dlp`) and app built again, because sites change things

That's all for now ;)
