import tkinter as tk
from tkinter import colorchooser
import calendar
import datetime
import json
import os
import math

# Eğer holidays yüklüyse tatilleri kullan; yüklü değilse sadece hafta sonlarını tatil sayar
try:
    import holidays
    TR_HOLIDAYS = holidays.Turkey()
    HAS_HOLIDAYS = True
except Exception:
    TR_HOLIDAYS = None
    HAS_HOLIDAYS = False

DATA_FILE = "monthly.json"

# Default renk atamaları (Ofis, Ev, İzin)
DEFAULT_COLORS = {
    "O": "#66bb6a",   # Ofis (yeşil)
    "E": "#ffd54f",   # Ev (sarı)
    "I": "#8ecae6"    # İzin (mavi)
}

# Kodlar:
# "O" = Ofis
# "E" = Ev
# "I" = İzin
# ""  = boş (henüz işaretlenmemiş)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    # başlangıç yapı
    return {"__colors__": DEFAULT_COLORS.copy()}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_holiday(dt: datetime.date):
    if not HAS_HOLIDAYS:
        return False
    return dt in TR_HOLIDAYS

def get_color_for(status_code):
    colors = data.get("__colors__", {})
    return colors.get(status_code, DEFAULT_COLORS.get(status_code, "#ffffff"))

def choose_color_for(status_code):
    """Open color chooser and set chosen color for status_code (O/E/I)."""
    initial = get_color_for(status_code)
    # colorchooser returns ( (r,g,b), "#rrggbb") or (None, None) if cancelled
    picked = colorchooser.askcolor(color=initial, title=f"Renk seç - {status_code}")
    if picked is None:
        return
    hex_color = picked[1]
    if not hex_color:
        return
    colors = data.setdefault("__colors__", DEFAULT_COLORS.copy())
    colors[status_code] = hex_color
    data["__colors__"] = colors
    save_data()
    draw_calendar()

def calculate_stats():
    month_days = calendar.monthrange(year, month)[1]
    workdays = []
    for d in range(1, month_days + 1):
        dt = datetime.date(year, month, d)
        if dt.weekday() < 5 and not is_holiday(dt):
            workdays.append(d)

    izin_days = [d for d in workdays if month_data.get(str(d)) == "I"]
    effective_workdays = len(workdays) - len(izin_days)

    ofis_days = sum(1 for d in workdays if month_data.get(str(d)) == "O")
    required_min = math.ceil(effective_workdays * 0.5)

    return len(workdays), effective_workdays, ofis_days, required_min

def toggle_status(day):
    current = month_data.get(str(day), "")
    if current == "":
        month_data[str(day)] = "O"   # Ofis
    elif current == "O":
        month_data[str(day)] = "E"   # Ev
    elif current == "E":
        month_data[str(day)] = "I"   # İzin
    else:
        month_data[str(day)] = ""    # Boş
    save_data()
    draw_calendar()

def change_month(delta):
    global year, month, month_data
    month += delta
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    month_data = data.setdefault(f"{year}-{month}", {})
    draw_calendar()

def draw_calendar():
    # temizle önceki
    for widget in frame.winfo_children():
        widget.destroy()
    for widget in header_frame.winfo_children():
        widget.destroy()
    for widget in legend_frame.winfo_children():
        widget.destroy()

    # Başlık
    lbl = tk.Label(header_frame, text=f"{calendar.month_name[month]} {year}",
                   font=("Arial", 14, "bold"), bg="#e0ded3")
    lbl.pack(side="left", padx=20)

    tk.Button(header_frame, text="◀ Önceki Ay", command=lambda: change_month(-1)).pack(side="left", padx=10)
    tk.Button(header_frame, text="Sonraki Ay ▶", command=lambda: change_month(1)).pack(side="right", padx=10)

    # İstatistik
    workdays, effective, ofis_days, required_min = calculate_stats()
    condition_ok = (ofis_days >= required_min)
    status = "Karşılandı" if condition_ok else "Karşılanmadı"
    status_color = "green" if condition_ok else "red"

    stats_label.config(
        text=f"İş günü: {workdays} | İzin sonrası: {effective} | "
             f"Ofis günleri: {ofis_days} | Min %50: {required_min} | Durum: {status}",
        fg=status_color
    )

    # Gün isimleri
    days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    for i, d in enumerate(days):
        tk.Label(frame, text=d, font=("Arial", 10, "bold"), width=6, height=2, bg="#ddd").grid(row=0, column=i)

    # Takvim
    month_cal = calendar.Calendar().monthdayscalendar(year, month)
    for row, week in enumerate(month_cal, start=1):
        for col, day in enumerate(week):
            if day == 0:
                tk.Label(frame, text="", width=6, height=3, relief="solid", bg="#f0f0f0").grid(row=row, column=col)
            else:
                status = month_data.get(str(day), "")
                dt = datetime.date(year, month, day)
                is_weekend = col >= 5
                holiday_flag = is_holiday(dt)

                if is_weekend or holiday_flag:
                    color = "black"
                    fg = "white"
                    # hafta sonu/tatil tıklanmasın
                    tk.Label(frame, text=str(day), width=6, height=3, relief="solid", bg=color, fg=fg).grid(row=row, column=col)
                else:
                    # durum rengi data içindeki ayarlanmış renge göre
                    if status == "O":
                        color = get_color_for("O")
                    elif status == "E":
                        color = get_color_for("E")
                    elif status == "I":
                        color = get_color_for("I")
                    else:
                        color = "white"
                    fg = "white" if color.lower() in ("black", "#000000") else "black"

                    btn = tk.Button(frame, text=str(day), width=6, height=3, relief="solid",
                                    bg=color, fg=fg, command=lambda d=day: toggle_status(d))
                    btn.grid(row=row, column=col)

    # Legend (tıklayınca colorpicker aç)
    def make_legend_button(label_text, status_code):
        f = tk.Frame(legend_frame, bg="#e0ded3")
        f.pack(side="left", padx=8)
        color = get_color_for(status_code)
        # small color preview button
        color_btn = tk.Button(f, width=3, height=1, bg=color,
                              command=lambda sc=status_code: choose_color_for(sc))
        color_btn.pack(side="left")
        tk.Label(f, text=label_text, bg="#e0ded3").pack(side="left", padx=6)

    make_legend_button("Ofis", "O")
    make_legend_button("Ev", "E")
    make_legend_button("İzin", "I")

    # sabit hafta sonu/ tatil legend
    f2 = tk.Frame(legend_frame, bg="#e0ded3")
    f2.pack(side="left", padx=8)
    tk.Label(f2, width=3, height=1, bg="black").pack(side="left")
    tk.Label(f2, text="Hafta sonu / Resmi tatil", bg="#e0ded3").pack(side="left", padx=6)

# --- UI Başlangıç ---
root = tk.Tk()
root.title("Ofis Takip")
root.configure(bg="#e0ded3")

today = datetime.date.today()
year, month = today.year, today.month

data = load_data()
# ensure colors exist
data.setdefault("__colors__", DEFAULT_COLORS.copy())
month_data = data.setdefault(f"{year}-{month}", {})

header_frame = tk.Frame(root, bg="#e0ded3")
header_frame.pack(pady=5)

frame = tk.Frame(root, bg="#e0ded3")
frame.pack()

legend_frame = tk.Frame(root, bg="#e0ded3")
legend_frame.pack(pady=5)

# Sabit stats label
stats_label = tk.Label(root, text="", bg="#e0ded3", font=("Arial", 10))
stats_label.pack(pady=5)

draw_calendar()
root.mainloop()
