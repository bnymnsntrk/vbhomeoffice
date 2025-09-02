import tkinter as tk
import calendar
import datetime
import json
import os
import math

DATA_FILE = "monthly.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

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

def calculate_stats():
    month_days = calendar.monthrange(year, month)[1]
    workdays = [d for d in range(1, month_days+1) if datetime.date(year, month, d).weekday() < 5]

    izin_days = [d for d in workdays if month_data.get(str(d)) == "I"]
    effective_workdays = len(workdays) - len(izin_days)

    ofis_days = sum(1 for d in workdays if month_data.get(str(d)) == "O")
    required_min = math.ceil(effective_workdays * 0.5)

    return len(workdays), effective_workdays, ofis_days, required_min

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
    status = "Karşılandı" if ofis_days >= required_min else "Karşılanmadı"
    status_color = "green" if ofis_days >= required_min else "red"

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
                is_weekend = col >= 5

                color = "white"
                if is_weekend:
                    color = "black"
                elif status == "O":
                    color = "lightgreen"
                elif status == "E":
                    color = "yellow"
                elif status == "I":
                    color = "lightblue"

                btn = tk.Button(frame, text=str(day), width=6, height=3, relief="solid",
                                bg=color, command=lambda d=day: toggle_status(d))
                btn.grid(row=row, column=col)

    # Legend
    legends = [("Ofis", "lightgreen"), ("Ev", "yellow"), ("İzin", "lightblue"), ("Hafta sonu", "black")]
    for text, color in legends:
        tk.Label(legend_frame, text="  ", bg=color, width=2).pack(side="left", padx=2)
        tk.Label(legend_frame, text=text, bg="#e0ded3").pack(side="left", padx=5)


root = tk.Tk()
root.title("Ofis Takip")
root.configure(bg="#e0ded3")

today = datetime.date.today()
year, month = today.year, today.month

data = load_data()
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
