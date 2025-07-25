import json
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import winsound
import winreg
import keyboard
import pystray
from PIL import Image, ImageDraw
from screeninfo import get_monitors

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    def disable_system_sounds():
        try:
            winsound.PlaySound(None, winsound.SND_ASYNC)
            winsound.PlaySound("", winsound.SND_ASYNC)
        except:
            pass
    disable_system_sounds()

    overlays = []
    active = False
    selected_monitors = set()
    registered_hotkeys = set()
    DEFAULT_CONFIG = {
        "hotkey": "ctrl+alt+b",
        "exit_hotkey": "esc",
        "selected_monitors": [],
        "system_hotkeys": [
            "shift+alt",
            "ctrl+alt+delete",
            "alt+tab",
            "alt+f4"
        ]
    }
    def save_to_registry(config):
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Blackout")
            winreg.SetValueEx(key, "hotkey", 0, winreg.REG_SZ, config["hotkey"])
            winreg.SetValueEx(key, "exit_hotkey", 0, winreg.REG_SZ, config["exit_hotkey"])
            winreg.SetValueEx(key, "selected_monitors", 0, winreg.REG_SZ, json.dumps(list(config["selected_monitors"])))
            winreg.SetValueEx(key, "system_hotkeys", 0, winreg.REG_SZ, json.dumps(config["system_hotkeys"]))
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error saving to registry: {e}")
            return False
    def load_from_registry():
        config = DEFAULT_CONFIG.copy()
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Blackout")
            config["hotkey"] = winreg.QueryValueEx(key, "hotkey")[0]
            config["exit_hotkey"] = winreg.QueryValueEx(key, "exit_hotkey")[0]
            selected_monitors_str = winreg.QueryValueEx(key, "selected_monitors")[0]
            config["selected_monitors"] = json.loads(selected_monitors_str)
            system_hotkeys_str = winreg.QueryValueEx(key, "system_hotkeys")[0]
            config["system_hotkeys"] = json.loads(system_hotkeys_str)
            winreg.CloseKey(key)
        except:
            pass
        return config
    config = load_from_registry()
    current_hotkey = config["hotkey"]
    exit_hotkey = config["exit_hotkey"]
    selected_monitors = set(config["selected_monitors"])
    system_hotkeys = set(config.get("system_hotkeys", [
        "shift+alt",
        "ctrl+alt+delete",
        "alt+tab",
        "alt+f4"
    ]))
    def save_config():
        config = {
            "hotkey": current_hotkey,
            "exit_hotkey": exit_hotkey,
            "selected_monitors": list(selected_monitors),
            "system_hotkeys": [
                "shift+alt",
                "ctrl+alt+delete",
                "alt+tab",
                "alt+f4"
            ]
        }
        return save_to_registry(config)
    def create_standard_window(title, width=600, height=500):
        window = tk.Toplevel(root)
        window.title(title)
        window.geometry(f"{width}x{height}")
        window.resizable(False, False)
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
        return window
    def create_image():
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
        else:
            icon_path = os.path.abspath('icon.ico')
        return Image.open(icon_path)
    def get_all_monitors():
        try:
            monitors = get_monitors()
            monitor_info = []
            for i, mon in enumerate(monitors):
                is_primary = getattr(mon, "is_primary", False)
                if not is_primary:
                    is_primary = (mon.x <= 0 < mon.x + mon.width and mon.y <= 0 < mon.y + mon.height)
                monitor_info.append({
                    'index': i,
                    'name': mon.name,
                    'width': mon.width,
                    'height': mon.height,
                    'x': mon.x,
                    'y': mon.y,
                    'is_primary': is_primary,
                    'description': f"Monitor {i+1}: {mon.width}x{mon.height} ({mon.name})"
                })
            return monitor_info
        except Exception as e:
            print(f"Error getting monitors: {e}")
            return [{
                'index': 0,
                'name': 'Monitor_0',
                'width': 1920,
                'height': 1080,
                'x': 0,
                'y': 0,
                'is_primary': True,
                'description': 'Monitor 1: 1920x1080 (Monitor_0)'
            }]
    def build_overlays():
        global overlays
        overlays.clear()
        monitors = get_all_monitors()
        for monitor in monitors:
            if monitor['name'] in selected_monitors:
                win = tk.Toplevel(root)
                win.overrideredirect(True)
                win.attributes("-topmost", True)
                win.configure(bg="black")
                win.geometry(f"{monitor['width']}x{monitor['height']}+{monitor['x']}+{monitor['y']}")
                win.withdraw()
                overlays.append(win)
    def cleanup_hotkeys():
        global registered_hotkeys
        for hotkey in registered_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
            except:
                pass
        registered_hotkeys.clear()
    def register_hotkey(hotkey, callback, suppress=False):
        try:
            try:
                keyboard.remove_hotkey(hotkey)
            except:
                pass
            keyboard.add_hotkey(hotkey, callback, suppress=suppress)
            registered_hotkeys.add(hotkey)
            return True
        except Exception as e:
            print(f"Error registering hotkey {hotkey}: {e}")
            return False
    def show():
        if not overlays:
            build_overlays()
        for w in overlays:
            w.deiconify()
        register_hotkey(exit_hotkey, hide, suppress=False)
    def hide():
        global active
        for w in overlays:
            w.withdraw()
        try:
            keyboard.remove_hotkey(exit_hotkey)
            registered_hotkeys.discard(exit_hotkey)
        except:
            pass
        active = False
    def toggle(_=None):
        global active
        if active:
            hide()
        else:
            show()
            active = True
    def setup_hotkeys():
        cleanup_hotkeys()
        if not register_hotkey(current_hotkey, toggle, suppress=False):
            register_hotkey("ctrl+alt+b", toggle, suppress=False)
    def show_monitor_selection():
        selection_window = create_standard_window("Monitor Selection for Dimming", 500, 400)
        disable_system_sounds()
        monitor_vars = {}
        tk.Label(selection_window, text="Select monitors to dim:", font=("Arial", 12, "bold")).pack(pady=10)
        monitors = get_all_monitors()
        for monitor in monitors:
            var = tk.BooleanVar(value=monitor['name'] in selected_monitors)
            monitor_vars[monitor['name']] = var
            display_text = monitor['description']
            if monitor['is_primary']:
                display_text += " (primary)"
            cb = tk.Checkbutton(selection_window, text=display_text, variable=var, font=("Arial", 10))
            cb.pack(anchor="w", padx=20, pady=2)
        button_frame = tk.Frame(selection_window)
        button_frame.pack(pady=20)
        def save_selection():
            global selected_monitors
            selected_monitors.clear()
            for monitor_name, var in monitor_vars.items():
                if var.get():
                    selected_monitors.add(monitor_name)
            save_config()
            if active:
                hide()
                build_overlays()
                show()
            else:
                build_overlays()
            selection_window.destroy()
        def cancel():
            selection_window.destroy()
        tk.Button(button_frame, text="Save", command=save_selection).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel).pack(side="left", padx=5)
    def show_hotkey_settings():
        settings_window = create_standard_window("Hotkey Settings", 450, 250)
        disable_system_sounds()
        tk.Label(settings_window, text="Hotkey Settings:", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(settings_window, text="Toggle hotkey:").pack(anchor="w", padx=20)
        hotkey_var = tk.StringVar(value=current_hotkey)
        hotkey_entry = tk.Entry(settings_window, textvariable=hotkey_var, width=30)
        hotkey_entry.pack(padx=20, pady=5)
        tk.Label(settings_window, text="Exit hotkey:").pack(anchor="w", padx=20)
        exit_hotkey_var = tk.StringVar(value=exit_hotkey)
        exit_hotkey_entry = tk.Entry(settings_window, textvariable=exit_hotkey_var, width=30)
        exit_hotkey_entry.pack(padx=20, pady=5)
        tk.Label(settings_window, text="Examples: ctrl+alt+b, f1, ctrl+shift+a", font=("Arial", 8)).pack(pady=5)
        button_frame = tk.Frame(settings_window)
        button_frame.pack(pady=20)
        def save_hotkeys():
            global current_hotkey, exit_hotkey
            new_hotkey = hotkey_var.get().strip()
            new_exit_hotkey = exit_hotkey_var.get().strip()
            if new_hotkey and new_exit_hotkey:
                current_hotkey = new_hotkey
                exit_hotkey = new_exit_hotkey
                save_config()
                setup_hotkeys()
                update_tray_menu()
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "Please enter both hotkeys!")
        def cancel():
            settings_window.destroy()
        tk.Button(button_frame, text="Save", command=save_hotkeys).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel).pack(side="left", padx=5)
    def on_quit(icon, item):
        hide()
        cleanup_hotkeys()
        icon.stop()
        root.quit()
    tray_icon = None
    def show_main_window():
        main_window = create_standard_window("Blackout - Monitor Management", 700, 600)
        disable_system_sounds()
        nav_header = tk.Frame(main_window, height=60)
        nav_header.pack(fill="x", side="top")
        nav_header.pack_propagate(False)
        title_label = tk.Label(nav_header, text="Blackout", font=("Arial", 16, "bold"))
        title_label.pack(side="left", padx=20, pady=15)
        nav_buttons_frame = tk.Frame(nav_header)
        nav_buttons_frame.pack(side="right", padx=20, pady=10)
        content_frame = tk.Frame(main_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        pages = {}
        current_page = tk.StringVar(value="monitors")
        def show_page(page_name):
            for page in pages.values():
                page.pack_forget()
            if page_name in pages:
                pages[page_name].pack(fill="both", expand=True)
                current_page.set(page_name)
        def create_monitors_page():
            monitors_page = tk.Frame(content_frame)
            tk.Label(monitors_page, text="Monitor Selection for Dimming", font=("Arial", 14, "bold")).pack(pady=10)
            monitor_vars = {}
            monitors = get_all_monitors()
            canvas = tk.Canvas(monitors_page, height=300)
            scrollbar = tk.Scrollbar(monitors_page, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            for monitor in monitors:
                var = tk.BooleanVar(value=monitor['name'] in selected_monitors)
                monitor_vars[monitor['name']] = var
                display_text = monitor['description']
                if monitor['is_primary']:
                    display_text += " (primary)"
                cb = tk.Checkbutton(scrollable_frame, text=display_text, variable=var, font=("Arial", 10))
                cb.pack(anchor="w", padx=20, pady=2)
            canvas.pack(side="left", fill="both", expand=True, padx=20)
            scrollbar.pack(side="right", fill="y")
            button_frame = tk.Frame(monitors_page)
            button_frame.pack(pady=20)
            def save_selection():
                global selected_monitors
                selected_monitors.clear()
                for monitor_name, var in monitor_vars.items():
                    if var.get():
                        selected_monitors.add(monitor_name)
                save_config()
                if active:
                    hide()
                    build_overlays()
                    show()
                else:
                    build_overlays()
                status_label.config(text="Settings saved!", fg="green")
                main_window.after(2000, lambda: status_label.config(text=""))
            def cancel():
                main_window.destroy()
            tk.Button(button_frame, text="Save", command=save_selection).pack(side="left", padx=5)
            tk.Button(button_frame, text="Cancel", command=cancel).pack(side="left", padx=5)
            status_label = tk.Label(monitors_page, text="")
            status_label.pack(pady=5)
            return monitors_page
        def create_hotkeys_page():
            hotkeys_page = tk.Frame(content_frame)
            tk.Label(hotkeys_page, text="Hotkey Settings", font=("Arial", 14, "bold")).pack(pady=10)
            tk.Label(hotkeys_page, text="Click on field and enter new key combination", font=("Arial", 10)).pack(pady=5)
            hotkeys_frame = tk.Frame(hotkeys_page)
            hotkeys_frame.pack(pady=20)
            hotkey_var = tk.StringVar(value=current_hotkey)
            def capture_hotkey(entry_widget, var, label_text):
                entry_widget.config(state="normal")
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, "Press keys...")
                entry_widget.config(state="readonly")
                entry_widget.focus()
                captured_keys = set()
                key_combination = ""
                def on_key_press(event):
                    nonlocal key_combination
                    key = event.keysym.lower()
                    key_mapping = {
                        'control_l': 'ctrl', 'control_r': 'ctrl',
                        'alt_l': 'alt', 'alt_r': 'alt',
                        'shift_l': 'shift', 'shift_r': 'shift'
                    }
                    if key in key_mapping:
                        key = key_mapping[key]
                    captured_keys.add(key)
                    modifiers = []
                    main_key = None
                    for k in captured_keys:
                        if k in ['ctrl', 'alt', 'shift']:
                            modifiers.append(k)
                        else:
                            main_key = k
                    if main_key:
                        if modifiers:
                            key_combination = "+".join(sorted(modifiers) + [main_key])
                        else:
                            key_combination = main_key
                        var.set(key_combination)
                        entry_widget.config(state="normal")
                        entry_widget.delete(0, tk.END)
                        entry_widget.insert(0, key_combination)
                        entry_widget.config(state="readonly")
                        entry_widget.unbind('<KeyPress>')
                        entry_widget.unbind('<KeyRelease>')
                        entry_widget.master.focus()
                def on_key_release(event):
                    key = event.keysym.lower()
                    key_mapping = {
                        'control_l': 'ctrl', 'control_r': 'ctrl',
                        'alt_l': 'alt', 'alt_r': 'alt',
                        'shift_l': 'shift', 'shift_r': 'shift'
                    }
                    if key in key_mapping:
                        key = key_mapping[key]
                    captured_keys.discard(key)
                entry_widget.bind('<KeyPress>', on_key_press)
                entry_widget.bind('<KeyRelease>', on_key_release)
            tk.Label(hotkeys_frame, text="Toggle hotkey:", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(10, 5))
            hotkey_entry = tk.Entry(hotkeys_frame, textvariable=hotkey_var, width=30, state="readonly")
            hotkey_entry.pack(padx=20, pady=(0, 10))
            tk.Button(hotkeys_frame, text="Change", command=lambda: capture_hotkey(hotkey_entry, hotkey_var, "toggle"), font=("Arial", 9)).pack(pady=(0, 20))
            button_frame = tk.Frame(hotkeys_page)
            button_frame.pack(pady=20)
            def save_hotkeys():
                global current_hotkey
                new_hotkey = hotkey_var.get().strip()
                if new_hotkey:
                    current_hotkey = new_hotkey
                    save_config()
                    setup_hotkeys()
                    update_tray_menu()
                    status_label.config(text="Hotkey saved!", fg="green")
                    main_window.after(2000, lambda: status_label.config(text=""))
                else:
                    status_label.config(text="Please enter a hotkey!", fg="red")
            def cancel():
                main_window.destroy()
            tk.Button(button_frame, text="Save", command=save_hotkeys).pack(side="left", padx=5)
            tk.Button(button_frame, text="Cancel", command=cancel).pack(side="left", padx=5)
            status_label = tk.Label(hotkeys_page, text="")
            status_label.pack(pady=5)
            return hotkeys_page
        def create_info_page():
            info_page = tk.Frame(content_frame)
            tk.Label(info_page, text="Monitor Information", font=("Arial", 14, "bold")).pack(pady=10)
            text_frame = tk.Frame(info_page)
            text_frame.pack(fill="both", expand=True, padx=20, pady=10)
            monitors = get_all_monitors()
            text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 10))
            scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            for monitor in monitors:
                if monitor['is_primary']:
                    status = " (primary)"
                elif monitor['name'] in selected_monitors:
                    status = " (selected for dimming)"
                else:
                    status = " (not selected)"
                info_line = f"{monitor['description']}{status}\n"
                text_widget.insert("end", info_line)
            text_widget.config(state="disabled")
            return info_page
        def create_quick_actions_page():
            actions_page = tk.Frame(content_frame)
            tk.Label(actions_page, text="Quick Actions", font=("Arial", 14, "bold")).pack(pady=10)
            actions_frame = tk.Frame(actions_page)
            actions_frame.pack(pady=20)
            tk.Button(actions_frame, text=f"Enable Dimming ({current_hotkey})", command=toggle, font=("Arial", 12), width=25, height=2).pack(pady=10)
            tk.Button(actions_frame, text="Disable Dimming", command=hide, font=("Arial", 12), width=25, height=2).pack(pady=10)
            status_label = tk.Label(actions_page, text="")
            status_label.pack(pady=5)
            return actions_page
        pages["monitors"] = create_monitors_page()
        pages["hotkeys"] = create_hotkeys_page()
        pages["info"] = create_info_page()
        pages["actions"] = create_quick_actions_page()
        nav_buttons = [
            ("Monitors", "monitors"),
            ("Hotkeys", "hotkeys"),
            ("Information", "info"),
            ("Actions", "actions")
        ]
        for text, page_name in nav_buttons:
            btn = tk.Button(nav_buttons_frame, text=text, command=lambda p=page_name: show_page(p))
            btn.pack(side="left", padx=5)
        show_page("monitors")
    def setup_tray_icon():
        global tray_icon
        menu = pystray.Menu(
            pystray.MenuItem("Main Window", lambda _: show_main_window()),
            pystray.MenuItem(f"Toggle Dimming ({current_hotkey})", lambda _: toggle()),
            pystray.MenuItem("Monitor Selection", lambda _: show_monitor_selection()),
            pystray.MenuItem("Hotkey Settings", lambda _: show_hotkey_settings()),
            pystray.MenuItem("Monitor Information", lambda _: show_monitor_info()),
            pystray.MenuItem("Exit", on_quit)
        )
        tray_icon = pystray.Icon("BlackoutApp", create_image(), "Blackout app", menu=menu)
        tray_icon.run()
    def update_tray_menu():
        global tray_icon
        if tray_icon:
            menu = pystray.Menu(
                pystray.MenuItem("Main Window", lambda _: show_main_window()),
                pystray.MenuItem(f"Toggle Dimming ({current_hotkey})", lambda _: toggle()),
                pystray.MenuItem("Monitor Selection", lambda _: show_monitor_selection()),
                pystray.MenuItem("Hotkey Settings", lambda _: show_hotkey_settings()),
                pystray.MenuItem("Monitor Information", lambda _: show_monitor_info()),
                pystray.MenuItem("Exit", on_quit)
            )
            tray_icon.menu = menu
    def show_monitor_info():
        info_window = create_standard_window("Monitor Information", 500, 400)
        disable_system_sounds()
        tk.Label(info_window, text="Monitor Information:", font=("Arial", 12, "bold")).pack(pady=10)
        text_frame = tk.Frame(info_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        monitors = get_all_monitors()
        text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 10))
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        for monitor in monitors:
            if monitor['is_primary']:
                status = " (primary)"
            elif monitor['name'] in selected_monitors:
                status = " (selected for dimming)"
            else:
                status = " (not selected)"
            info_line = f"{monitor['description']}{status}\n"
            text_widget.insert("end", info_line)
        text_widget.config(state="disabled")
        button_frame = tk.Frame(info_window)
        button_frame.pack(pady=20)
        def close_info():
            info_window.destroy()
        tk.Button(button_frame, text="Close", command=close_info).pack()
    if not selected_monitors:
        monitors = get_all_monitors()
        for monitor in monitors:
            if not monitor['is_primary']:
                selected_monitors.add(monitor['name'])
        save_config()
    setup_hotkeys()
    threading.Thread(target=setup_tray_icon, daemon=True).start()
    root.mainloop()