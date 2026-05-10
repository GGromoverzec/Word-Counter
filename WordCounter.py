import customtkinter as ctk
import speech_recognition as sr
import threading
import json
from tkinter import messagebox

ctk.set_appearance_mode("dark")

DATA_FILE = "settings.json"

# ---------- ПЕРЕКЛАД ----------
lang_pack = {
    "ua": {
        "tabs": ["Головне", "Налаштування", "Фрази", "Лог"],
        "start": "СТАРТ",
        "stop": "СТОП",
        "reset": "СКИНУТИ",
        "overlay": "Оверлей режим",
        "ui_lang": "Мова інтерфейсу",
        "speech_lang": "Мова розпізнавання",
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
        "overlay": "Оверлей режим",
        "ui_lang": "Язык интерфейса",
        "speech_lang": "Язык распознавания",
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
        "overlay": "Overlay mode",
        "ui_lang": "UI Language",
        "speech_lang": "Speech Language",
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
            return json.load(f)
    except:
        return {
            "count": 0,
            "phrases": ["плюс одна смерть"],
            "overlay_text": "Смерті",
            "mic_index": None,
            "language": "ru-RU",
            "ui_lang": "ua"
        }

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ---------- ГОЛОС ----------
recognizer = sr.Recognizer()
running = False

# лог буде створений пізніше
log_box = None

def listen():
    global running
    while running:
        try:
            set_status("listening")

            with sr.Microphone(device_index=data["mic_index"]) as source:
                audio = recognizer.listen(source)

            set_status("processing")

            text = recognizer.recognize_google(audio, language=data["language"]).lower()

            if log_box:
                log_box.insert("end", text + "\n")
                log_box.see("end")

            for phrase in data["phrases"]:
                if phrase in text:
                    data["count"] += 1
                    update_ui()
                    save_data()

        except:
            pass

    set_status("idle")

# ---------- UI ----------
app = ctk.CTk()
app.title("WordCounter")
app.geometry("600x500")

count_label = ctk.CTkLabel(app, font=("Arial", 50))
count_label.pack(side="top", pady=20)

status_label = ctk.CTkLabel(app)
status_label.pack()

def set_status(state):
    status_label.configure(text=get_text(state))

# ---------- TABVIEW ----------
def build_tabs():
    global tabview, main_tab, settings_tab, phrases_tab, log_tab, log_box

    try:
        tabview.destroy()
    except:
        pass

    tabview = ctk.CTkTabview(app)
    tabview.pack(fill="both", expand=True)

    tabs = get_text("tabs")

    main_tab = tabview.add(tabs[0])
    settings_tab = tabview.add(tabs[1])
    phrases_tab = tabview.add(tabs[2])
    log_tab = tabview.add(tabs[3])

    build_ui()

    # створюємо лог ОДИН раз
    log_box = ctk.CTkTextbox(log_tab)
    log_box.pack(fill="both", expand=True, padx=10, pady=10)

def build_ui():
    for tab in [main_tab, settings_tab, phrases_tab]:
        for w in tab.winfo_children():
            w.destroy()

    # MAIN
    ctk.CTkButton(main_tab, text=get_text("start"), command=start).pack(pady=5)
    ctk.CTkButton(main_tab, text=get_text("stop"), command=stop).pack(pady=5)
    ctk.CTkButton(main_tab, text=get_text("reset"), command=reset_counter).pack(pady=5)

    # SETTINGS
    ctk.CTkLabel(settings_tab, text=get_text("ui_lang")).pack()
    ctk.CTkOptionMenu(settings_tab, values=["ua","ru","en"], command=set_ui_lang).pack(pady=5)

    ctk.CTkLabel(settings_tab, text=get_text("speech_lang")).pack()
    ctk.CTkOptionMenu(settings_tab, values=["ru-RU","en-US","uk-UA"], command=set_speech_lang).pack(pady=5)

    ctk.CTkButton(settings_tab, text=get_text("overlay"), command=toggle_overlay_mode).pack(pady=10)

    # PHRASES
    ctk.CTkLabel(phrases_tab, text=get_text("counter_text_label")).pack()

    global entry
    entry = ctk.CTkEntry(phrases_tab)
    entry.insert(0, data["overlay_text"])
    entry.pack(pady=5)

    ctk.CTkButton(phrases_tab, text=get_text("save_text_btn"), command=save_overlay).pack()

    ctk.CTkLabel(phrases_tab, text=get_text("phrases_label")).pack()

    global phrases_box
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
    count_label.configure(text=f"{data['overlay_text']}: {data['count']}")

def start():
    global running
    running = True
    threading.Thread(target=listen, daemon=True).start()

def stop():
    global running
    running = False

def reset_counter():
    if messagebox.askyesno(get_text("reset_title"), get_text("reset_text")):
        data["count"] = 0
        update_ui()
        save_data()

def set_ui_lang(choice):
    data["ui_lang"] = choice
    save_data()
    build_tabs()
    set_status("idle")

def set_speech_lang(choice):
    data["language"] = choice
    save_data()

def save_overlay():
    data["overlay_text"] = entry.get()
    update_ui()
    save_data()

def save_phrases():
    data["phrases"] = phrases_box.get("1.0","end").strip().split("\n")
    save_data()

# ---------- СТАРТ ----------
build_tabs()
update_ui()
set_status("idle")

app.mainloop()