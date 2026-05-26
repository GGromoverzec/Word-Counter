import customtkinter as ctk
import speech_recognition as sr
import threading
import ctypes
import json
import os
import shutil
import subprocess
import sys
import uuid
from ctypes import wintypes
from tkinter import messagebox

ctk.set_appearance_mode("dark")

APP_NAME = "WordCounter"
APP_VERSION = "1.4.2"
LOCAL_APPDATA = os.environ.get(
    "LOCALAPPDATA",
    os.path.join(os.path.expanduser("~"), "AppData", "Local")
)
APP_DIR = os.path.join(LOCAL_APPDATA, APP_NAME)
DATA_FILE = os.path.join(APP_DIR, "settings.json")
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
SHORTCUT_FILE = os.path.join(DESKTOP_DIR, f"{APP_NAME}.lnk")


def get_current_app_path():
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.executable)

    return os.path.abspath(__file__)


def get_installed_app_path():
    return os.path.join(APP_DIR, os.path.basename(get_current_app_path()))


def same_path(first_path, second_path):
    return os.path.normcase(os.path.abspath(first_path)) == os.path.normcase(os.path.abspath(second_path))


def get_gui_python_path():
    if getattr(sys, "frozen", False):
        return get_installed_app_path()

    pythonw_path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")

    if os.path.exists(pythonw_path):
        return pythonw_path

    return sys.executable


def ps_quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def get_hidden_subprocess_options():
    options = {}

    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

        options["startupinfo"] = startupinfo
        options["creationflags"] = subprocess.CREATE_NO_WINDOW

    return options


def create_desktop_shortcut():
    if not os.path.isdir(DESKTOP_DIR):
        return

    installed_path = get_installed_app_path()

    if getattr(sys, "frozen", False):
        target_path = installed_path
        arguments = ""
        icon_path = installed_path
    else:
        target_path = get_gui_python_path()
        arguments = f'"{installed_path}"'
        icon_path = target_path

    command = "\n".join([
        "$shell = New-Object -ComObject WScript.Shell",
        f"$shortcut = $shell.CreateShortcut({ps_quote(SHORTCUT_FILE)})",
        f"$shortcut.TargetPath = {ps_quote(target_path)}",
        f"$shortcut.Arguments = {ps_quote(arguments)}",
        f"$shortcut.WorkingDirectory = {ps_quote(APP_DIR)}",
        f"$shortcut.IconLocation = {ps_quote(icon_path + ',0')}",
        "$shortcut.Save()"
    ])

    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **get_hidden_subprocess_options()
        )
    except Exception:
        pass


def migrate_legacy_settings():
    legacy_data_file = os.path.join(os.path.dirname(get_current_app_path()), "settings.json")

    if same_path(legacy_data_file, DATA_FILE):
        return

    if os.path.exists(DATA_FILE) or not os.path.exists(legacy_data_file):
        return

    try:
        shutil.copy2(legacy_data_file, DATA_FILE)
    except Exception:
        pass


def install_if_needed():
    os.makedirs(APP_DIR, exist_ok=True)
    migrate_legacy_settings()

    current_path = get_current_app_path()
    installed_path = get_installed_app_path()

    if same_path(current_path, installed_path):
        if not os.path.exists(SHORTCUT_FILE):
            create_desktop_shortcut()
        return

    try:
        shutil.copy2(current_path, installed_path)
        create_desktop_shortcut()

        if getattr(sys, "frozen", False):
            subprocess.Popen([installed_path], cwd=APP_DIR, **get_hidden_subprocess_options())
        else:
            subprocess.Popen([get_gui_python_path(), installed_path], cwd=APP_DIR, **get_hidden_subprocess_options())

        sys.exit(0)
    except Exception:
        pass


install_if_needed()

# ---------- ПЕРЕКЛАД ----------
lang_pack = {
    "ua": {
        "tabs": ["Головне", "Налаштування", "Фрази", "Лог"],
        "start": "СТАРТ",
        "stop": "СТОП",
        "reset": "СКИНУТИ",
        "set_count_label": "Встановити рахунок",
        "set_count_btn": "ВСТАНОВИТИ",
        "count_error_title": "Помилка",
        "count_error_text": "Введіть ціле число 0 або більше.",
        "overlay": "Оверлей режим",
        "ui_lang": "Мова інтерфейсу",
        "speech_lang": "Мова розпізнавання",
        "microphone": "Мікрофон",
        "default_microphone": "Системний мікрофон",
        "no_microphones": "Мікрофони не знайдені",
        "counter_text_label": "Текст лічильника",
        "phrases_label": "Фрази",
        "save_text_btn": "Зберегти текст",
        "save_phrases_btn": "Зберегти фрази",
        "listening": "● СЛУХАЄ",
        "idle": "● НЕ СЛУХАЄ",
        "processing": "● ОБРОБКА",
        "reset_title": "Підтвердження",
        "reset_text": "Скинути лічильник?"
    },
    "ru": {
        "tabs": ["Главное", "Настройки", "Фразы", "Лог"],
        "start": "СТАРТ",
        "stop": "СТОП",
        "reset": "СБРОС",
        "set_count_label": "Установить счет",
        "set_count_btn": "УСТАНОВИТЬ",
        "count_error_title": "Ошибка",
        "count_error_text": "Введите целое число 0 или больше.",
        "overlay": "Оверлей режим",
        "ui_lang": "Язык интерфейса",
        "speech_lang": "Язык распознавания",
        "microphone": "Микрофон",
        "default_microphone": "Системный микрофон",
        "no_microphones": "Микрофоны не найдены",
        "counter_text_label": "Текст счетчика",
        "phrases_label": "Фразы",
        "save_text_btn": "Сохранить текст",
        "save_phrases_btn": "Сохранить фразы",
        "listening": "● СЛУШАЮ",
        "idle": "● НЕ СЛУШАЮ",
        "processing": "● ОБРАБОТКА",
        "reset_title": "Подтверждение",
        "reset_text": "Сбросить счетчик?"
    },
    "en": {
        "tabs": ["Main", "Settings", "Phrases", "Log"],
        "start": "START",
        "stop": "STOP",
        "reset": "RESET",
        "set_count_label": "Set counter",
        "set_count_btn": "SET",
        "count_error_title": "Error",
        "count_error_text": "Enter a whole number 0 or higher.",
        "overlay": "Overlay mode",
        "ui_lang": "UI Language",
        "speech_lang": "Speech Language",
        "microphone": "Microphone",
        "default_microphone": "System microphone",
        "no_microphones": "No microphones found",
        "counter_text_label": "Counter text",
        "phrases_label": "Phrases",
        "save_text_btn": "Save text",
        "save_phrases_btn": "Save phrases",
        "listening": "● LISTENING",
        "idle": "● IDLE",
        "processing": "● PROCESSING",
        "reset_title": "Confirm",
        "reset_text": "Reset counter?"
    }
}


def get_text(key):
    return lang_pack[data["ui_lang"]][key]


# ---------- ДАНІ ----------
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except Exception:
        loaded = {}

    defaults = {
        "count": 0,
        "phrases": ["плюс одна смерть"],
        "overlay_text": "Смерті",
        "mic_index": None,
        "mic_name": None,
        "language": "ru-RU",
        "ui_lang": "ua"
    }
    defaults.update(loaded)
    return defaults


def save_data():
    with state_lock:
        snapshot = data.copy()

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)


data = load_data()

# ---------- ГОЛОС ----------
recognizer = sr.Recognizer()
running = False
listen_thread = None
state_lock = threading.Lock()
main_thread = threading.current_thread()
mic_choices = {}

# Лог буде створений пізніше.
log_box = None


def on_ui_thread(callback):
    if threading.current_thread() is main_thread:
        callback()
    else:
        app.after(0, callback)


def write_log(text):
    def update_log():
        if log_box:
            log_box.insert("end", text + "\n")
            log_box.see("end")

    on_ui_thread(update_log)


def normalize_audio_name(name):
    return " ".join(str(name).lower().split())


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __init__(self, value):
        guid = uuid.UUID(value)
        self.Data1 = guid.time_low
        self.Data2 = guid.time_mid
        self.Data3 = guid.time_hi_version
        self.Data4[:] = guid.bytes[8:]


class PROPERTYKEY(ctypes.Structure):
    _fields_ = [
        ("fmtid", GUID),
        ("pid", wintypes.DWORD),
    ]


class PROPVARIANT_VALUE(ctypes.Union):
    _fields_ = [
        ("pwszVal", wintypes.LPWSTR),
        ("raw", ctypes.c_ulonglong),
    ]


class PROPVARIANT(ctypes.Structure):
    _anonymous_ = ("value",)
    _fields_ = [
        ("vt", wintypes.USHORT),
        ("wReserved1", wintypes.USHORT),
        ("wReserved2", wintypes.USHORT),
        ("wReserved3", wintypes.USHORT),
        ("value", PROPVARIANT_VALUE),
    ]


def com_method(pointer, index, result_type, *argument_types):
    vtable = ctypes.cast(pointer, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return ctypes.WINFUNCTYPE(result_type, ctypes.c_void_p, *argument_types)(vtable[index])


def release_com_object(pointer):
    if pointer:
        com_method(pointer, 2, wintypes.ULONG)(pointer)


def get_windows_enabled_capture_names():
    try:
        ole32 = ctypes.OleDLL("ole32")
        ole32.CoInitialize(None)

        clsid_mm_device_enumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
        iid_mm_device_enumerator = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
        pkey_device_friendly_name = PROPERTYKEY(
            GUID("{A45C254E-DF1C-4EFD-8020-67D146A850E0}"),
            14
        )

        enumerator = ctypes.c_void_p()
        result = ole32.CoCreateInstance(
            ctypes.byref(clsid_mm_device_enumerator),
            None,
            23,
            ctypes.byref(iid_mm_device_enumerator),
            ctypes.byref(enumerator)
        )

        if result != 0:
            return None

        collection = ctypes.c_void_p()
        enum_audio_endpoints = com_method(
            enumerator,
            3,
            ctypes.HRESULT,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.POINTER(ctypes.c_void_p)
        )
        result = enum_audio_endpoints(enumerator, 1, 1, ctypes.byref(collection))

        if result != 0:
            release_com_object(enumerator)
            return None

        get_count = com_method(collection, 3, ctypes.HRESULT, ctypes.POINTER(wintypes.UINT))
        item = com_method(collection, 4, ctypes.HRESULT, wintypes.UINT, ctypes.POINTER(ctypes.c_void_p))

        count = wintypes.UINT()
        result = get_count(collection, ctypes.byref(count))

        if result != 0:
            release_com_object(collection)
            release_com_object(enumerator)
            return None

        devices = {}

        for index in range(count.value):
            device = ctypes.c_void_p()

            if item(collection, index, ctypes.byref(device)) != 0:
                continue

            property_store = ctypes.c_void_p()
            open_property_store = com_method(
                device,
                4,
                ctypes.HRESULT,
                wintypes.DWORD,
                ctypes.POINTER(ctypes.c_void_p)
            )

            if open_property_store(device, 0, ctypes.byref(property_store)) == 0:
                propvariant = PROPVARIANT()
                get_value = com_method(
                    property_store,
                    5,
                    ctypes.HRESULT,
                    ctypes.POINTER(PROPERTYKEY),
                    ctypes.POINTER(PROPVARIANT)
                )

                if get_value(
                    property_store,
                    ctypes.byref(pkey_device_friendly_name),
                    ctypes.byref(propvariant)
                ) == 0 and propvariant.vt == 31 and propvariant.pwszVal:
                    name = str(propvariant.pwszVal).strip()

                    if name:
                        devices[normalize_audio_name(name)] = name

                ctypes.OleDLL("ole32").PropVariantClear(ctypes.byref(propvariant))
                release_com_object(property_store)

            release_com_object(device)

        release_com_object(collection)
        release_com_object(enumerator)

        return devices
    except Exception as error:
        write_log(f"Windows microphone list error: {error}")
        return None


def get_allowed_microphone_label(name, allowed_names):
    if allowed_names is None:
        return name

    normalized_name = normalize_audio_name(name)

    for allowed_name, display_name in allowed_names.items():
        if (
            normalized_name == allowed_name
            or normalized_name in allowed_name
            or allowed_name in normalized_name
        ):
            return display_name

    return None


def get_microphone_options():
    choices = {
        get_text("default_microphone"): {
            "index": None,
            "name": None
        }
    }
    seen_names = set()
    allowed_names = get_windows_enabled_capture_names()

    try:
        audio = sr.Microphone.get_pyaudio().PyAudio()

        try:
            for index in range(audio.get_device_count()):
                device = audio.get_device_info_by_index(index)

                if int(device.get("maxInputChannels", 0)) <= 0:
                    continue

                name = str(device.get("name", "")).strip()
                display_name = get_allowed_microphone_label(name, allowed_names)

                if not display_name:
                    continue

                normalized_name = normalize_audio_name(display_name)

                if normalized_name in seen_names:
                    continue

                seen_names.add(normalized_name)
                choices[display_name] = {
                    "index": index,
                    "name": display_name
                }
        finally:
            audio.terminate()
    except Exception as error:
        write_log(f"Microphone list error: {error}")

    if len(choices) == 1:
        choices[get_text("no_microphones")] = {
            "index": None,
            "name": None
        }

    return choices


def get_current_microphone_label():
    mic_name = data.get("mic_name")
    mic_index = data.get("mic_index")

    if mic_name:
        for label, microphone in mic_choices.items():
            if microphone.get("name") == mic_name:
                return label

    for label, microphone in mic_choices.items():
        if microphone.get("index") == mic_index:
            return label

    return next(iter(mic_choices), get_text("default_microphone"))


def get_selected_microphone_index(mic_name, mic_index):
    if mic_name:
        for microphone in mic_choices.values():
            if microphone.get("name") == mic_name:
                return microphone.get("index")

        return None

    for microphone in mic_choices.values():
        if microphone.get("index") == mic_index:
            return mic_index

    return None


def is_running():
    with state_lock:
        return running


def listen():
    while is_running():
        try:
            set_status("listening")

            with state_lock:
                selected_mic_name = data.get("mic_name")
                selected_mic_index = data.get("mic_index")
                language = data["language"]
                phrases = [phrase.lower() for phrase in data["phrases"] if phrase.strip()]

            mic_index = get_selected_microphone_index(selected_mic_name, selected_mic_index)

            with sr.Microphone(device_index=mic_index) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=6)

            set_status("processing")

            text = recognizer.recognize_google(audio, language=language).lower()
            write_log(text)

            for phrase in phrases:
                if phrase in text:
                    with state_lock:
                        data["count"] += 1
                    update_ui()
                    update_count_entry()
                    save_data()

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError as error:
            write_log(f"Recognition error: {error}")
        except OSError as error:
            write_log(f"Microphone error: {error}")
            stop()
        except Exception as error:
            write_log(f"Error: {error}")

    set_status("idle")


# ---------- UI ----------
app = ctk.CTk()
app.title(f"WordCounter {APP_VERSION}")
app.geometry("600x500")

count_label = ctk.CTkLabel(app, font=("Arial", 50))
count_label.pack(side="top", pady=20)

status_label = ctk.CTkLabel(app)
status_label.pack()


def set_status(state):
    on_ui_thread(lambda: status_label.configure(text=get_text(state)))


# ---------- TABVIEW ----------
def build_tabs():
    global tabview, main_tab, settings_tab, phrases_tab, log_tab, log_box

    try:
        tabview.destroy()
    except Exception:
        pass

    tabview = ctk.CTkTabview(app)
    tabview.pack(fill="both", expand=True)

    tabs = get_text("tabs")

    main_tab = tabview.add(tabs[0])
    settings_tab = tabview.add(tabs[1])
    phrases_tab = tabview.add(tabs[2])
    log_tab = tabview.add(tabs[3])

    build_ui()

    log_box = ctk.CTkTextbox(log_tab)
    log_box.pack(fill="both", expand=True, padx=10, pady=10)


def build_ui():
    global entry, phrases_box, mic_choices, count_entry

    for tab in [main_tab, settings_tab, phrases_tab]:
        for widget in tab.winfo_children():
            widget.destroy()

    # MAIN
    ctk.CTkButton(main_tab, text=get_text("start"), command=start).pack(pady=5)
    ctk.CTkButton(main_tab, text=get_text("stop"), command=stop).pack(pady=5)
    ctk.CTkButton(main_tab, text=get_text("reset"), command=reset_counter).pack(pady=5)
    ctk.CTkLabel(main_tab, text=get_text("set_count_label")).pack(pady=(15, 2))

    count_entry = ctk.CTkEntry(main_tab, width=140)
    count_entry.insert(0, str(data["count"]))
    count_entry.pack(pady=5)

    ctk.CTkButton(main_tab, text=get_text("set_count_btn"), command=set_counter).pack(pady=5)

    # SETTINGS
    ctk.CTkLabel(settings_tab, text=get_text("ui_lang")).pack()
    ui_menu = ctk.CTkOptionMenu(settings_tab, values=["ua", "ru", "en"], command=set_ui_lang)
    ui_menu.pack(pady=5)
    ui_menu.set(data["ui_lang"])

    ctk.CTkLabel(settings_tab, text=get_text("speech_lang")).pack()
    lang_menu = ctk.CTkOptionMenu(
        settings_tab,
        values=["ru-RU", "en-US", "uk-UA"],
        command=set_speech_lang
    )
    lang_menu.pack(pady=5)
    lang_menu.set(data["language"])

    ctk.CTkLabel(settings_tab, text=get_text("microphone")).pack()
    mic_choices = get_microphone_options()
    mic_menu = ctk.CTkOptionMenu(
        settings_tab,
        values=list(mic_choices.keys())
    )
    mic_menu.pack(pady=5)
    mic_menu.set(get_current_microphone_label())
    mic_menu.configure(command=set_microphone)

    ctk.CTkButton(settings_tab, text=get_text("overlay"), command=toggle_overlay_mode).pack(pady=10)

    # PHRASES
    ctk.CTkLabel(phrases_tab, text=get_text("counter_text_label")).pack()

    entry = ctk.CTkEntry(phrases_tab)
    entry.insert(0, data["overlay_text"])
    entry.pack(pady=5)

    ctk.CTkButton(phrases_tab, text=get_text("save_text_btn"), command=save_overlay).pack()

    ctk.CTkLabel(phrases_tab, text=get_text("phrases_label")).pack()

    phrases_box = ctk.CTkTextbox(phrases_tab, height=120)
    phrases_box.pack(pady=5)
    phrases_box.insert("end", "\n".join(data["phrases"]))

    ctk.CTkButton(phrases_tab, text=get_text("save_phrases_btn"), command=save_phrases).pack()


# ---------- OVERLAY ----------
overlay_mode = False


def toggle_overlay_mode():
    global overlay_mode
    overlay_mode = not overlay_mode

    if overlay_mode:
        app.attributes("-topmost", True)
        app.configure(fg_color="#00FF00")
        tabview.pack_forget()
        status_label.pack_forget()
    else:
        app.attributes("-topmost", False)
        app.configure(fg_color="#1f1f1f")
        status_label.pack()
        tabview.pack(fill="both", expand=True)


app.bind("<Double-Button-1>", lambda e: toggle_overlay_mode() if overlay_mode else None)


# ---------- ФУНКЦІЇ ----------
def update_ui():
    on_ui_thread(lambda: count_label.configure(text=f"{data['overlay_text']}: {data['count']}"))


def start():
    global running, listen_thread

    with state_lock:
        if running:
            return
        running = True

    listen_thread = threading.Thread(target=listen, daemon=True)
    listen_thread.start()


def stop():
    global running

    with state_lock:
        running = False


def reset_counter():
    if messagebox.askyesno(get_text("reset_title"), get_text("reset_text")):
        with state_lock:
            data["count"] = 0
        update_ui()
        update_count_entry()
        save_data()


def update_count_entry():
    def update_entry():
        if "count_entry" in globals() and count_entry.winfo_exists():
            count_entry.delete(0, "end")
            count_entry.insert(0, str(data["count"]))

    on_ui_thread(update_entry)


def set_counter():
    try:
        new_count = int(count_entry.get().strip())

        if new_count < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(get_text("count_error_title"), get_text("count_error_text"))
        return

    with state_lock:
        data["count"] = new_count

    update_ui()
    update_count_entry()
    save_data()


def set_ui_lang(choice):
    with state_lock:
        data["ui_lang"] = choice

    save_data()
    build_tabs()
    set_status("idle")


def set_speech_lang(choice):
    with state_lock:
        data["language"] = choice

    save_data()


def set_microphone(choice):
    microphone = mic_choices.get(choice, {"index": None, "name": None})

    with state_lock:
        data["mic_index"] = microphone.get("index")
        data["mic_name"] = microphone.get("name")

    save_data()


def save_overlay():
    with state_lock:
        data["overlay_text"] = entry.get()

    update_ui()
    save_data()


def save_phrases():
    phrases = phrases_box.get("1.0", "end").strip().split("\n")

    with state_lock:
        data["phrases"] = phrases

    save_data()


# ---------- СТАРТ ----------
build_tabs()
update_ui()
set_status("idle")

app.mainloop()
