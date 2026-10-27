import json
import tkinter as tk
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import ttk, messagebox

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday"]
SAVE_FILE = Path("schedule.json") #creates a json file to save the schedule data

schedule = {}                                    # "YYYY-MM-DD" -> {day: [[time, task]]}
state = {"start": None, "day": None, "time": None}
cell_times = {}                                  # (row_id, day) -> time
cell_tasks = {}      # (row_id, day) -> "14:00  full task text"

# ---------------------------------------------------------------- data model
def week_start(d):
    """The Sunday on or before date d."""
    return d - timedelta(days=(d.weekday() + 1) % 7)


def current_week():
    """The displayed week's dict, created on demand."""
    key = state["start"].isoformat()
    if key not in schedule:
        schedule[key] = {day: [] for day in DAYS}
    return schedule[key]


def add_task(day, time, task):
    current_week()[day].append([time, task])


def remove_task(day, time):
    tasks = current_week()[day]
    for i in range(len(tasks)):
        if tasks[i][0] == time:
            del tasks[i]
            return True
    return False


def normalize_time(raw):
    """Accept 9:00, 0900, 2pm, 14 -> '14:00'. None if unparseable."""
    cleaned = raw.upper().replace(" ", "")
    for fmt in ("%H:%M", "%H%M", "%I:%M%p", "%I%p", "%H"):
        try:
            return datetime.strptime(cleaned, fmt).strftime("%H:%M")
        except ValueError:
            continue
    return None


# ------------------------------------------------------------- save and load
def save():
    keep = {k: v for k, v in schedule.items() if any(v[d] for d in DAYS)}
    try:
        SAVE_FILE.write_text(json.dumps(keep, indent=2))
    except OSError as err:
        messagebox.showerror("Save failed", str(err))


def load():
    if not SAVE_FILE.exists():
        return
    try:
        data = json.loads(SAVE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        messagebox.showwarning("Load failed", "Could not read schedule.json.")
        return
    for key, days in data.items():
        schedule[key] = {d: [list(p) for p in days.get(d, [])] for d in DAYS}


# ------------------------------------------------------------------- display
def refresh_display():
    start = state["start"]
    end = start + timedelta(days=6)
    is_now = start == week_start(date.today())
    week_label.config(text=f"{start:%b %d} - {end:%b %d, %Y}"
                           + ("   (this week)" if is_now else ""))

    for i, day in enumerate(DAYS):
        d = start + timedelta(days=i)
        marker = " *" if d == date.today() else ""
        tree.heading(day, text=f"{day[:3]} {d.month}/{d.day}{marker}")

        tree.delete(*tree.get_children())
    cell_times.clear()
    cell_tasks.clear()                                  # <-- add

    week = current_week()
    ordered = {day: sorted(week[day]) for day in DAYS}
    rows = max([len(t) for t in ordered.values()] + [1])

    for i in range(rows):
        values = []
        for day in DAYS:
            if i < len(ordered[day]):
                time, task = ordered[day][i]
                values.append(f"{time}  {task}")
            else:
                values.append("")
        row_id = tree.insert("", "end", values=values)
        for day in DAYS:
            if i < len(ordered[day]):
                time, task = ordered[day][i]
                cell_times[(row_id, day)] = time
                cell_tasks[(row_id, day)] = f"{time}  {task}"      # <-- add

def clear_selection():
    state["day"] = state["time"] = None
    status.config(text="Click a task to select it.")


def shift_week(delta):
    state["start"] += timedelta(weeks=delta)
    clear_selection()
    refresh_display()


def goto(d):
    state["start"] = week_start(d)
    clear_selection()
    refresh_display()


# ------------------------------------------------------------------ handlers
def on_cell_click(event):
    if tree.identify_region(event.x, event.y) != "cell":
        return
    row_id = tree.identify_row(event.y)
    col_id = tree.identify_column(event.x)
    if not row_id:
        return

    day = DAYS[int(col_id[1:]) - 1]
    time = cell_times.get((row_id, day))

    if time is None:
        clear_selection()
        status.config(text=f"Empty cell in {day}.")
        return

    state["day"], state["time"] = day, time
    status.config(text=f"Selected: {tree.set(row_id, day).strip()}  ({day})")


def on_add(event=None):
    raw_time = time_entry.get().strip()
    task = task_entry.get().strip()
    if not raw_time or not task:
        messagebox.showwarning("Missing info", "Enter both a time and a task.")
        return

    time = normalize_time(raw_time)
    if time is None:
        messagebox.showwarning("Bad time", f"Could not read '{raw_time}'.\n"
                                           "Try something like 14:00 or 2pm.")
        return

    add_task(day_var.get(), time, task)
    time_entry.delete(0, "end")
    task_entry.delete(0, "end")
    task_entry.focus_set()
    refresh_display()
    status.config(text=f"Added {time} {task} to {day_var.get()}.")


def on_remove():
    if not state["day"]:
        messagebox.showinfo("Nothing selected", "Click a task cell first.")
        return
    time, day = state["time"], state["day"]
    remove_task(day, time)
    clear_selection()
    refresh_display()
    status.config(text=f"Removed the {time} task on {day}.")


def on_close():
    save()
    root.destroy()


# -------------------------------------------------------------------- window
root = tk.Tk()
root.title("Schedule Planner")
root.geometry("1000x520")
root.minsize(760, 360)
root.protocol("WM_DELETE_WINDOW", on_close)

state["start"] = week_start(date.today())

# navigation bar
nav = ttk.Frame(root, padding=(10, 8))
nav.pack(fill="x")
ttk.Button(nav, text="< Prev", width=9,
           command=lambda: shift_week(-1)).pack(side="left")
ttk.Button(nav, text="Next >", width=9,
           command=lambda: shift_week(1)).pack(side="left", padx=4)
ttk.Button(nav, text="This Week",
           command=lambda: goto(date.today())).pack(side="left", padx=(12, 0))
week_label = ttk.Label(nav, text="", font=("TkDefaultFont", 11, "bold"))
week_label.pack(side="left", padx=20)

# input form
form = ttk.Frame(root, padding=(10, 4))
form.pack(fill="x")

ttk.Label(form, text="Day:").grid(row=0, column=0)
day_var = tk.StringVar(value=DAYS[(date.today().weekday() + 1) % 7])
ttk.Combobox(form, textvariable=day_var, values=DAYS, state="readonly",
             width=12).grid(row=0, column=1, padx=(4, 12))

ttk.Label(form, text="Time:").grid(row=0, column=2)
time_entry = ttk.Entry(form, width=10)
time_entry.grid(row=0, column=3, padx=(4, 12))

ttk.Label(form, text="Task:").grid(row=0, column=4)
task_entry = ttk.Entry(form, width=30)
task_entry.grid(row=0, column=5, padx=4)

ttk.Button(form, text="Add Task",
           command=on_add).grid(row=0, column=6, padx=(12, 4))
ttk.Button(form, text="Remove Selected",
           command=on_remove).grid(row=0, column=7, padx=4)

time_entry.bind("<Return>", on_add)
task_entry.bind("<Return>", on_add)

# the week grid
tree_frame = ttk.Frame(root, padding=10)
tree_frame.pack(fill="both", expand=True)

tree = ttk.Treeview(tree_frame, columns=DAYS, show="headings",
                    height=15, selectmode="none")
tree.pack(side="left", fill="both", expand=True)

scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
scroll.pack(side="right", fill="y")
tree.configure(yscrollcommand=scroll.set)

for day in DAYS:
    tree.heading(day, text=day)
    tree.column(day, width=135, anchor="w", stretch=True)

ttk.Style().configure("Treeview", font=("Courier New", 10), rowheight=22)
tree.bind("<Button-1>", on_cell_click)

status = ttk.Label(root, text="Click a task to select it.", padding=(12, 6))
status.pack(fill="x")


#part of the view on hover feature
import tkinter.font as tkfont

cell_font = tkfont.Font(family="Courier New", size=10)

tip = tk.Toplevel(root)
tip.wm_overrideredirect(True)          # no title bar or border
tip.attributes("-topmost", True)
tip.withdraw()                         # start hidden

tip_label = tk.Label(tip, text="", justify="left", wraplength=320,
                     background="#ffffe0", relief="solid", borderwidth=1,
                     padx=6, pady=3, font=("TkDefaultFont", 9))
tip_label.pack()

hovered = {"cell": None}               # remembers the last cell we showed



def hide_tip(event=None):
    tip.withdraw()
    hovered["cell"] = None


def on_motion(event):
    if tree.identify_region(event.x, event.y) != "cell":
        hide_tip()
        return

    row_id = tree.identify_row(event.y)
    col_id = tree.identify_column(event.x)
    if not row_id or not col_id:
        hide_tip()
        return

    day = DAYS[int(col_id[1:]) - 1]
    text = cell_tasks.get((row_id, day))

    if not text:
        hide_tip()
        return

    # only bother if the text is actually too wide for the column
    if cell_font.measure(text) + 12 <= tree.column(day, "width"):
        hide_tip()
        return

    if hovered["cell"] != (row_id, day):               # new cell: update text
        hovered["cell"] = (row_id, day)
        tip_label.config(text=text)
        tip.deiconify()

    tip.wm_geometry(f"+{event.x_root + 14}+{event.y_root + 14}")


tree.bind("<Motion>", on_motion)
tree.bind("<Leave>", hide_tip)
tree.bind("<Button-1>", hide_tip, add="+")     # dismiss on click




# go
load()
refresh_display()
root.mainloop()