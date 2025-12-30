import tkinter as tk
from tkinter import simpledialog, messagebox
import json, os, uuid, random

# ---------------- CONFIG ----------------
APP_NAME = "TaskerPro"
DATA_FILE = "data.json"

COLORS = {
    "bg": "#0f0f14",
    "card": "#1b1b24",
    "text": "#ffffff",
    "muted": "#9a9a9a",
    "accent": "#9C27B0",
    "danger": "#ff5f5f"
}

# ---------------- DATA ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "tasks": [],
        "categories": {"General": COLORS["accent"]},
        "filter": "All"
    }

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ---------------- APP ----------------
root = tk.Tk()
root.title(APP_NAME)
root.geometry("540x640")
root.configure(bg=COLORS["bg"])
root.resizable(False, False)

# ---------------- ICON ----------------
if os.path.exists("assets/app.ico"):
    root.iconbitmap("assets/app.ico")

# ---------------- UI HELPERS ----------------
task_widgets = {}

def pill(parent, text, cmd):
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=COLORS["accent"], fg=COLORS["text"],
        relief=tk.FLAT, padx=14, pady=6,
        font=("Segoe UI", 10, "bold")
    )

    def on_enter(e):
        b.config(bg="#AB47BC")
    def on_leave(e):
        b.config(bg=COLORS["accent"])

    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    return b

# ---------------- HEADER ----------------
header = tk.Frame(root, bg=COLORS["bg"])
header.pack(pady=20)

title = tk.Label(
    header, text="Your Tasks",
    bg=COLORS["bg"], fg=COLORS["text"],
    font=("Segoe UI", 20, "bold")
)
title.pack()

counter = tk.Label(
    header, bg=COLORS["bg"],
    fg=COLORS["muted"],
    font=("Segoe UI", 10)
)
counter.pack()

# ---------------- FILTER ----------------
filter_frame = tk.Frame(root, bg=COLORS["bg"])
filter_frame.pack(pady=6)

def set_filter(cat):
    data["filter"] = cat
    save_data()
    refresh()

def rebuild_filters():
    for w in filter_frame.winfo_children():
        w.destroy()

    pill(filter_frame, "All", lambda: set_filter("All")).pack(side=tk.LEFT, padx=4)
    pill(filter_frame, "Done", lambda: set_filter("Done")).pack(side=tk.LEFT, padx=4)

    for cat in data["categories"]:
        pill(filter_frame, cat, lambda c=cat: set_filter(c)).pack(side=tk.LEFT, padx=4)

# ---------------- TASK LIST ----------------
list_frame = tk.Frame(root, bg=COLORS["bg"])
list_frame.pack(fill=tk.BOTH, expand=True)

def refresh():
    for w in list_frame.winfo_children():
        w.destroy()

    visible = 0
    task_widgets.clear()

    for task in data["tasks"]:
        if data["filter"] == "Done" and not task["done"]:
            continue
        if data["filter"] not in ("All", "Done") and task["category"] != data["filter"]:
            continue

        visible += 1
        draw_task(task)

    counter.config(text=f"{visible} task(s)")

def draw_task(task):
    card = tk.Frame(list_frame, bg=COLORS["card"])
    card.pack(fill=tk.X, padx=18, pady=6)

    var = tk.BooleanVar(value=task["done"])

    cb = tk.Checkbutton(
        card, variable=var, bg=COLORS["card"],
        activebackground=COLORS["card"],
        command=lambda t=task, v=var: toggle_done(t, v)
    )
    cb.pack(side=tk.LEFT, padx=8)

    lbl = tk.Label(
        card, text=task["title"],
        bg=COLORS["card"], fg=COLORS["text"],
        font=("Segoe UI", 11, "overstrike" if task["done"] else "normal")
    )
    lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

    tk.Button(
        card, text="✕", bg=COLORS["card"], fg=COLORS["danger"],
        relief=tk.FLAT, command=lambda t=task: delete_task(t)
    ).pack(side=tk.RIGHT, padx=6)

    task_widgets[task["id"]] = {"label": lbl}

def toggle_done(task, var):
    task["done"] = var.get()
    fade_text(task) if var.get() else reset_text(task)
    save_data()
    refresh()

def fade_text(task, step=0):
    lbl = task_widgets[task["id"]]["label"]
    colors = ["#ffffff", "#dddddd", "#aaaaaa", "#888888"]
    if step < len(colors):
        lbl.config(fg=colors[step])
        lbl.after(50, lambda: fade_text(task, step+1))
    else:
        lbl.config(font=("Segoe UI", 11, "overstrike"))

def reset_text(task):
    lbl = task_widgets[task["id"]]["label"]
    lbl.config(font=("Segoe UI", 11, "normal"), fg=COLORS["text"])

def delete_task(task):
    data["tasks"].remove(task)
    save_data()
    refresh()

# ---------------- ADD TASK ----------------
def add_task():
    title = simpledialog.askstring("New Task", "Task name:")
    if not title:
        return

    category = simpledialog.askstring(
        "Category",
        f"Category ({', '.join(data['categories'].keys())}):"
    ) or "General"

    if category not in data["categories"]:
        data["categories"][category] = COLORS["accent"]
        rebuild_filters()

    data["tasks"].append({
        "id": str(uuid.uuid4()),
        "title": title,
        "category": category,
        "done": False
    })
    save_data()
    refresh()

# ---------------- FOOTER ----------------
footer = tk.Frame(root, bg=COLORS["bg"])
footer.pack(pady=16)

pill(footer, "+ Add Task", add_task).pack()

rebuild_filters()
refresh()
root.mainloop()
