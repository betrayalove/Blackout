# 🌙 Blackout

[Русская версия](#русская-версия)

## Description
Blackout is a utility for dimming selected monitors with customizable hotkeys. Perfect for presentations, focus work, or creating a comfortable environment.

## Features
- Dim any selected monitors
- Customizable hotkeys (toggle, exit)
- System tray integration and menu
- Autostart via .bat script
- All settings saved in Windows registry

## Requirements
- Windows 10/11
- Python 3.7+

## Quick Start (for users)
1. Download the ready-to-use archive from [Releases](https://github.com/betrayalove/Blackout/releases) and extract it to a separate folder.
2. Run `add_to_autostart.bat` from the folder with Blackout.exe **as administrator** to add to autostart.
3. To remove from autostart, use `remove_from_autostart.bat`.
4. To run manually, just open Blackout.exe.

## Build from Source (for developers)
1. Install Python 3.7+ and pip.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```
3. Build the exe:
   ```
   python build.py
   ```
   The ready exe and .bat scripts will appear in the `dist/` folder.

## Usage
- After launch, the app will appear in the system tray. Right-click the icon for settings.
- All settings (monitors, hotkeys) are available via the tray menu.
- Settings are saved in the registry: `HKEY_CURRENT_USER\Software\Blackout`

## FAQ
- **Autostart not working:** Run the .bat file as administrator and make sure exe and .bat are in the same folder.
- **Hotkey not working:** Make sure it does not conflict with system shortcuts.
- **Monitors not detected:** Check that your monitor drivers are installed correctly.

## License
MIT License. See the [LICENSE](LICENSE) file.

**Author: Kirill** 

---

# Русская версия

## Описание
Blackout — это утилита для затемнения выбранных мониторов с помощью настраиваемых горячих клавиш. Идеально подходит для презентаций, работы в фокусе или создания комфортной среды.

## Возможности
- Затемнение любых выбранных мониторов
- Настраиваемые горячие клавиши (включение/выключение, выход)
- Системный трей и удобное меню
- Автозапуск через .bat-файл
- Все настройки сохраняются в реестре Windows

## Требования
- Windows 10/11
- Python 3.7+

## Быстрый старт (для пользователей)
1. Скачайте готовый архив из [Releases](https://github.com/betrayalove/Blackout/releases) и распакуйте в отдельную папку.
2. Запустите `add_to_autostart.bat` из папки с Blackout.exe **от имени администратора** для добавления в автозапуск.
3. Для удаления из автозапуска используйте `remove_from_autostart.bat`.
4. Для ручного запуска — просто откройте Blackout.exe.

## Сборка из исходников (для разработчиков)
1. Установите Python 3.7+ и pip.
2. Установите зависимости:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```
3. Соберите exe:
   ```
   python build.py
   ```
   Готовый файл и .bat-скрипты появятся в папке `dist/`.

## Использование
- После запуска программа появится в трее. Кликните правой кнопкой по иконке для доступа к настройкам.
- Все настройки (мониторы, горячие клавиши) доступны через меню.
- Настройки сохраняются в реестре: `HKEY_CURRENT_USER\Software\Blackout`

## FAQ
- **Не работает автозапуск:** Запустите .bat-файл от имени администратора и убедитесь, что exe и .bat лежат в одной папке.
- **Не работает горячая клавиша:** Проверьте, что она не конфликтует с системными сочетаниями.
- **Не видит мониторы:** Убедитесь, что драйверы мониторов установлены корректно.
