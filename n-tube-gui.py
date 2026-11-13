import glob
import hashlib
import importlib.abc
import importlib.machinery
import io
import json
import os
import platform
import queue
import re
import shutil
import ssl
import sys
import threading
import urllib.request
import zipfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse

import certifi
import imageio_ffmpeg

# no console in windowed exe - stdout/stderr are None
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')


def data_dir():
    if sys.platform == 'win32':
        base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    elif sys.platform == 'darwin':
        base = Path.home() / 'Library' / 'Application Support'
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
    return base / 'n-tube'


# yt-dlp self-update, only in built app - newer yt-dlp from PyPI is extracted here
# and used instead of the bundled one from the next start
UPDATE_DIR = data_dir() / 'yt-dlp'


def version_key(version):
    return tuple(int(x) for x in version.split('.'))


def version_folders(parent):
    if not parent.is_dir():
        return []
    folders = [f for f in parent.iterdir() if f.is_dir() and re.fullmatch(r'\d+(\.\d+)*', f.name)]
    return sorted(folders, key=lambda f: version_key(f.name))


def installed_updates():
    return version_folders(UPDATE_DIR)


# yt_dlp_ejs - challenge solver scripts run by deno, its version has to match yt-dlp
UPDATED_PACKAGES = ('yt_dlp', 'yt_dlp_ejs')


class UpdatedYtDlpFinder(importlib.abc.MetaPathFinder):
    # has to be before PyInstaller importer, otherwise bundled yt_dlp is imported
    def __init__(self, folder):
        self.folder = str(folder)

    def find_spec(self, name, path=None, target=None):
        # None = not in the update folder, bundled package is used
        if name in UPDATED_PACKAGES:
            return importlib.machinery.PathFinder.find_spec(name, [self.folder])
        # submodules only of packages loaded from the update folder
        if path and all(str(p).startswith(self.folder) for p in path):
            return importlib.machinery.PathFinder.find_spec(name, path)
        return None


def unload_yt_dlp():
    # yt-dlp patches requests, urllib3 and websockets at import, without unloading them
    # the second yt-dlp patches already patched objects and requests fail
    for name in list(sys.modules):
        if name.partition('.')[0] in (*UPDATED_PACKAGES, 'requests', 'urllib3', 'websockets'):
            del sys.modules[name]


def load_yt_dlp():
    import yt_dlp
    if not getattr(sys, 'frozen', False):
        return yt_dlp
    bundled = version_key(yt_dlp.version.__version__)
    updates = installed_updates()
    for folder in updates:
        if version_key(folder.name) <= bundled:
            shutil.rmtree(folder, ignore_errors=True)
    updates = [f for f in updates if version_key(f.name) > bundled]
    if not updates:
        return yt_dlp
    newest = updates[-1]
    finder = UpdatedYtDlpFinder(newest)
    unload_yt_dlp()
    sys.meta_path.insert(0, finder)
    try:
        import yt_dlp
    except Exception:
        # update doesn't work with this build, back to the bundled version
        sys.meta_path.remove(finder)
        unload_yt_dlp()
        shutil.rmtree(newest, ignore_errors=True)
        import yt_dlp
        return yt_dlp
    for folder in updates[:-1]:
        shutil.rmtree(folder, ignore_errors=True)
    return yt_dlp


def ssl_context():
    # certifi - system certificates are not always found by the built app
    return ssl.create_default_context(cafile=certifi.where())


def pypi_info(package, context, version=None):
    url = f'https://pypi.org/pypi/{package}/{version}/json' if version else f'https://pypi.org/pypi/{package}/json'
    with urllib.request.urlopen(url, timeout=15, context=context) as r:
        return json.load(r)


def download_wheel(info, context, platform_parts=()):
    # platform_parts - parts of the file name, e.g. ('manylinux', 'x86_64')
    wheel = next((u for u in info['urls'] if u['packagetype'] == 'bdist_wheel'
                  and all(p in u['filename'] for p in platform_parts)), None)
    if wheel is None:
        raise ValueError(f'no {info["info"]["name"]} package for this system')
    with urllib.request.urlopen(wheel['url'], timeout=120, context=context) as r:
        data = r.read()
    if hashlib.sha256(data).hexdigest() != wheel['digests']['sha256']:
        raise ValueError('wrong checksum of the downloaded file')
    return zipfile.ZipFile(io.BytesIO(data))


def required_version(info, package):
    # e.g. 'yt-dlp-ejs==0.8.0; extra == "default"'
    for req in info['info'].get('requires_dist') or []:
        m = re.match(rf'{re.escape(package)}==([\d.]+);.*extra == "default"', req)
        if m:
            return m.group(1)
    return None


def update_yt_dlp(current, events):
    try:
        context = ssl_context()
        info = pypi_info('yt-dlp', context)
        latest = info['info']['version']
        if version_key(latest) <= version_key(current) or (UPDATE_DIR / latest).is_dir():
            return
        tmp = UPDATE_DIR / f'.tmp-{latest}'
        shutil.rmtree(tmp, ignore_errors=True)
        with download_wheel(info, context) as z:
            z.extractall(tmp)
        ejs = required_version(info, 'yt-dlp-ejs')
        if ejs:
            with download_wheel(pypi_info('yt-dlp-ejs', context, ejs), context) as z:
                z.extractall(tmp)
        tmp.rename(UPDATE_DIR / latest)
        events.put(('log', f'yt-dlp {latest} downloaded, it will be used after restart of the app.'))
    except Exception as e:
        events.put(('log', f'yt-dlp update failed: {e}'))


# JavaScript runtime for YouTube challenges, without it some formats are missing.
# Too big to be bundled (~40 MB compressed), so it's downloaded from PyPI (deno package)
# at the first start and updated like yt-dlp. Used right after download, no restart needed.
DENO_DIR = data_dir() / 'deno'
DENO_EXE = 'deno.exe' if sys.platform == 'win32' else 'deno'


def deno_wheel_parts():
    machine = platform.machine().lower()
    if sys.platform == 'win32':
        return ('win_amd64',) if machine in ('amd64', 'x86_64') else None
    if sys.platform == 'darwin':
        return ('macosx', 'arm64' if machine == 'arm64' else 'x86_64')
    if sys.platform.startswith('linux') and machine in ('x86_64', 'aarch64'):
        return ('manylinux', machine)
    return None


def installed_deno():
    """Returns (path, version), version None = deno from pip, not updated by the app."""
    if not getattr(sys, 'frozen', False):
        # script version with requirements-console.txt
        try:
            import deno
            return deno.find_deno_bin(), None
        except Exception:
            pass
    for tmp in DENO_DIR.glob('.tmp-*'):
        shutil.rmtree(tmp, ignore_errors=True)
    folders = [f for f in version_folders(DENO_DIR) if (f / DENO_EXE).is_file()]
    if not folders:
        return None, None
    for folder in folders[:-1]:
        shutil.rmtree(folder, ignore_errors=True)
    return str(folders[-1] / DENO_EXE), folders[-1].name


def update_deno(current, events):
    try:
        parts = deno_wheel_parts()
        if parts is None:
            events.put(('log', 'deno is not available for this system, some YouTube formats may be missing.'))
            return
        context = ssl_context()
        info = pypi_info('deno', context)
        latest = info['info']['version']
        if current and version_key(latest) <= version_key(current):
            return
        if not current:
            events.put(('log', 'Downloading deno (JavaScript runtime needed by YouTube, about 40 MB)...'))
        tmp = DENO_DIR / f'.tmp-{latest}'
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        with download_wheel(info, context, parts) as z:
            member = next(n for n in z.namelist() if n.endswith('/scripts/' + DENO_EXE))
            (tmp / DENO_EXE).write_bytes(z.read(member))
        (tmp / DENO_EXE).chmod(0o755)
        tmp.rename(DENO_DIR / latest)
        events.put(('deno', str(DENO_DIR / latest / DENO_EXE)))
        events.put(('log', f'deno {latest} downloaded.'))
    except Exception as e:
        events.put(('log', f'deno download failed: {e}'))


yt_dlp = load_yt_dlp()
DownloadCancelled = yt_dlp.utils.DownloadCancelled
DownloadError = yt_dlp.utils.DownloadError

# exe unpacks files to sys._MEIPASS
ASSETS = Path(getattr(sys, '_MEIPASS', Path(__file__).parent)) / 'assets'


def set_icon(root):
    if sys.platform == 'win32':
        # without it taskbar shows python icon
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('n-tube')
        except Exception:
            pass
        root.iconbitmap(default=str(ASSETS / 'n-tube.ico'))
    else:
        root.icons = [tk.PhotoImage(file=str(ASSETS / 'png' / f'n-tube-{size}.png'))
                      for size in (256, 128, 64, 48, 32, 16)]
        root.iconphoto(True, *root.icons)


def is_valid_url(url):
    parts = urlparse(url)
    return parts.scheme in ('http', 'https') and '.' in parts.netloc


class GuiLogger:
    def __init__(self, events):
        self.events = events

    def debug(self, msg):
        if not msg.startswith('[debug] '):
            self.events.put(('log', msg))

    def info(self, msg):
        self.events.put(('log', msg))

    def warning(self, msg):
        self.events.put(('log', f'WARNING: {msg}'))

    def error(self, msg):
        self.events.put(('log', msg))


class App:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.thread = None
        self.cancel = False
        # files being downloaded, to remove .part files when window is closed
        self.downloading_files = set()

        root.title('n-tube - video downloader')
        root.minsize(560, 360)

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)

        ttk.Label(frame, text='Video URL:').grid(row=0, column=0, sticky='w')
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(frame, textvariable=self.url_var)
        self.url_entry.grid(row=0, column=1, sticky='ew', padx=5)
        self.url_entry.bind('<Return>', lambda e: self.start_download())
        self.download_btn = ttk.Button(frame, text='Download', command=self.start_download)
        self.download_btn.grid(row=0, column=2)

        ttk.Label(frame, text='Save to:').grid(row=1, column=0, sticky='w', pady=(8, 0))
        self.folder_var = tk.StringVar(value=str(Path.home() / 'Downloads'))
        self.folder_entry = ttk.Entry(frame, textvariable=self.folder_var)
        self.folder_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=(8, 0))
        self.browse_btn = ttk.Button(frame, text='Browse...', command=self.choose_folder)
        self.browse_btn.grid(row=1, column=2, pady=(8, 0))

        self.progress = ttk.Progressbar(frame, maximum=100)
        self.progress.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(12, 0))
        self.status_var = tk.StringVar(value='Paste a link and click Download.')
        ttk.Label(frame, textvariable=self.status_var).grid(row=3, column=0, columnspan=3, sticky='w', pady=(4, 8))

        self.log = tk.Text(frame, height=10, state='disabled', wrap='word')
        self.log.grid(row=4, column=0, columnspan=3, sticky='nsew')

        self.url_entry.focus()
        root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.events.put(('log', f'yt-dlp {yt_dlp.version.__version__}'))
        if getattr(sys, 'frozen', False):
            threading.Thread(target=update_yt_dlp, args=(yt_dlp.version.__version__, self.events), daemon=True).start()
        self.deno, deno_version = installed_deno()
        if self.deno:
            self.events.put(('log', f'deno {deno_version or "from pip"}'))
        if not (self.deno and deno_version is None):
            threading.Thread(target=update_deno, args=(deno_version, self.events), daemon=True).start()
        self.root.after(100, self.process_events)

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)

    def start_download(self):
        # Enter works also when button is disabled
        if self.download_btn.instate(['disabled']):
            return
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning('No URL', 'Paste the URL of the video you want to download.')
            return
        if not is_valid_url(url):
            messagebox.showwarning('Wrong URL', 'This is not a valid link, it has to start with http:// or https://')
            return
        self.download_btn.config(state='disabled')
        self.folder_entry.config(state='disabled')
        self.browse_btn.config(state='disabled')
        self.cancel = False
        self.downloading_files = set()
        self.progress['value'] = 0
        self.status_var.set('Starting...')
        self.thread = threading.Thread(target=self.dwl_vid, args=(url, self.folder_var.get(), self.deno), daemon=True)
        self.thread.start()

    def dwl_vid(self, video_url, folder, deno):
        saved_files = []
        ydl_opts = {
            'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
            # always .mp4 in the highest resolution, H.264/AAC preferred at the same resolution
            # (plays everywhere), above 1080p YouTube has only VP9/AV1 - remuxed to .mp4, not re-encoded
            'format_sort': ['res', 'vcodec:h264', 'acodec:aac'],
            'merge_output_format': 'mp4',
            'postprocessors': [{'key': 'FFmpegVideoRemuxer', 'preferedformat': 'mp4'}],
            'paths': {'home': folder},
            # too long file name = error
            'outtmpl': '%(title).150B [%(id)s].%(ext)s',
            'quiet': True,
            'noprogress': True,
            'logger': GuiLogger(self.events),
            'progress_hooks': [self.progress_hook],
            'postprocessor_hooks': [self.postprocessor_hook],
            # final file path, after merging
            'post_hooks': [saved_files.append],
            # solver scripts from GitHub when yt-dlp-ejs doesn't match yt-dlp version
            'remote_components': ['ejs:github'],
            # 'cookiesfrombrowser': ('firefox',),
        }
        if deno:
            ydl_opts['js_runtimes'] = {'deno': {'path': deno}}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            self.events.put(('done', saved_files))
        except DownloadError as e:
            self.events.put(('error', f'Wrong link or the video is not available.\n\n{e}'))
        except Exception as e:
            self.events.put(('error', str(e)))

    def progress_hook(self, d):
        if self.cancel:
            raise DownloadCancelled()
        if d['status'] == 'downloading':
            self.downloading_files.add(d['filename'])
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            percent = d['downloaded_bytes'] / total * 100 if total else 0
            self.events.put(('progress', percent))
        elif d['status'] == 'finished':
            self.events.put(('progress', 100))

    def postprocessor_hook(self, d):
        if d['status'] == 'started' and d['postprocessor'] == 'Merger':
            self.events.put(('status', 'Merging video and audio...'))

    def on_close(self):
        if not (self.thread and self.thread.is_alive()):
            self.root.destroy()
            return
        # download is stopped in progress_hook, .part files can be removed after that (Windows can't remove open file)
        self.cancel = True
        self.status_var.set('Cancelling...')
        self.wait_and_close(50)

    def wait_and_close(self, tries):
        # merging (ffmpeg) can't be stopped, max 5 s of waiting
        if self.thread.is_alive() and tries > 0:
            self.root.after(100, self.wait_and_close, tries - 1)
            return
        for f in self.downloading_files:
            for part in glob.glob(glob.escape(f) + '.part*') + glob.glob(glob.escape(f) + '.ytdl'):
                try:
                    os.remove(part)
                except OSError:
                    pass
        self.root.destroy()

    def process_events(self):
        # tkinter works only from main thread
        while not self.events.empty() and not self.cancel:
            kind, value = self.events.get()
            if kind == 'log':
                self.log.config(state='normal')
                self.log.insert('end', value + '\n')
                self.log.see('end')
                self.log.config(state='disabled')
            elif kind == 'progress':
                self.progress['value'] = value
                self.status_var.set(f'Downloading... {value:.1f}%')
            elif kind == 'status':
                self.status_var.set(value)
            elif kind == 'deno':
                self.deno = value
            elif kind == 'done':
                self.status_var.set('Finished.')
                files = '\n'.join(Path(f).name for f in value)
                messagebox.showinfo(
                    'Download finished',
                    f'The video has been downloaded and merged:\n\n{files}\n\n'
                    f'Saved to: {self.folder_var.get()}',
                )
                self.reset()
            elif kind == 'error':
                self.status_var.set('Download failed.')
                messagebox.showerror('Error', value)
                self.reset()
        self.root.after(100, self.process_events)

    def reset(self):
        self.url_var.set('')
        self.progress['value'] = 0
        self.status_var.set('Paste a link and click Download.')
        self.download_btn.config(state='normal')
        self.folder_entry.config(state='normal')
        self.browse_btn.config(state='normal')
        self.url_entry.focus()


if __name__ == '__main__':
    # className has to match StartupWMClass in install_lin.sh
    root = tk.Tk(className='n-tube')
    set_icon(root)
    App(root)
    root.mainloop()
