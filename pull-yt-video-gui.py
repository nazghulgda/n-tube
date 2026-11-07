import os
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import yt_dlp
import imageio_ffmpeg

# no console in windowed exe - stdout/stderr are None
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

# exe unpacks files to sys._MEIPASS
ASSETS = Path(getattr(sys, '_MEIPASS', Path(__file__).parent)) / 'assets'


def set_icon(root):
    if sys.platform == 'win32':
        # without it taskbar shows python icon
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('yt-downloader')
        except Exception:
            pass
        root.iconbitmap(default=str(ASSETS / 'n-tube.ico'))
    else:
        root.icons = [tk.PhotoImage(file=str(ASSETS / 'png' / f'n-tube-{size}.png'))
                      for size in (256, 128, 64, 48, 32, 16)]
        root.iconphoto(True, *root.icons)


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
        ttk.Entry(frame, textvariable=self.folder_var).grid(row=1, column=1, sticky='ew', padx=5, pady=(8, 0))
        ttk.Button(frame, text='Browse...', command=self.choose_folder).grid(row=1, column=2, pady=(8, 0))

        self.progress = ttk.Progressbar(frame, maximum=100)
        self.progress.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(12, 0))
        self.status_var = tk.StringVar(value='Paste a link and click Download.')
        ttk.Label(frame, textvariable=self.status_var).grid(row=3, column=0, columnspan=3, sticky='w', pady=(4, 8))

        self.log = tk.Text(frame, height=10, state='disabled', wrap='word')
        self.log.grid(row=4, column=0, columnspan=3, sticky='nsew')

        self.url_entry.focus()
        self.root.after(100, self.process_events)

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning('No URL', 'Paste the URL of the video you want to download.')
            return
        self.download_btn.config(state='disabled')
        self.progress['value'] = 0
        self.status_var.set('Starting...')
        threading.Thread(target=self.dwl_vid, args=(url, self.folder_var.get()), daemon=True).start()

    def dwl_vid(self, video_url, folder):
        saved_files = []
        ydl_opts = {
            'nocheckcertificate': True,
            'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
            'paths': {'home': folder},
            # too long file name = error
            'outtmpl': '%(title).150B [%(id)s].%(ext)s',
            'quiet': True,
            'noprogress': True,
            'logger': GuiLogger(self.events),
            'progress_hooks': [self.progress_hook],
            # final file path, after merging
            'post_hooks': [saved_files.append],
            # 'cookiesfrombrowser': ('firefox',),
        }
        # without 'nocheckcertificate': True script will return an error
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            self.events.put(('done', saved_files))
        except Exception as e:
            self.events.put(('error', str(e)))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            percent = d['downloaded_bytes'] / total * 100 if total else 0
            self.events.put(('progress', percent))
        elif d['status'] == 'finished':
            self.events.put(('progress', 100))

    def process_events(self):
        # tkinter works only from main thread
        while not self.events.empty():
            kind, value = self.events.get()
            if kind == 'log':
                self.log.config(state='normal')
                self.log.insert('end', value + '\n')
                self.log.see('end')
                self.log.config(state='disabled')
            elif kind == 'progress':
                self.progress['value'] = value
                self.status_var.set(f'Downloading... {value:.1f}%')
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
        self.url_entry.focus()


if __name__ == '__main__':
    # className has to match StartupWMClass in install_lin.sh
    root = tk.Tk(className='yt-downloader')
    set_icon(root)
    App(root)
    root.mainloop()
