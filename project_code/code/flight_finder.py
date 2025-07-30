
from tkinter import Toplevel, Label, Entry, Button, messagebox, StringVar, Text
from tkinter.ttk import Combobox
import mysql.connector
import os
from datetime import datetime, timedelta

# Read DB config
def read_db_config(filename='db_config.txt'):
    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, filename)
    config = {}
    with open(full_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    config['port'] = int(config.get('port', 3306))
    return config

# Connect to DB
def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

# Fetch spaceports for dropdown
def fetch_spaceports():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT spaceport_id, name FROM spaceport")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return {f"{name} (ID:{sid})": sid for sid, name in result}
    except:
        return {}

# Search paths recursively
def search_paths(current_port, destination_port, day, time, max_stops, max_time, path=[], total_time=0.0):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    itineraries = []
    visited = set(f['flight_number'] for f in path)

    # Get flights from current port on the same day
    cursor.execute("""
        SELECT f.*, s.type_name, r.origin_spaceport_id, r.destination_spaceport_id
        FROM flight f
        JOIN flight_schedule fs ON f.flight_number = fs.flight_number
        JOIN route r ON f.route_id = r.route_id
        JOIN spacecraft_type s ON f.craft_type_id = s.craft_type_id
        WHERE fs.day_of_week = %s
          AND r.origin_spaceport_id = %s
          AND TIME(f.departure_time) >= %s
    """, (day, current_port, time))

    for flight in cursor.fetchall():
        if flight['flight_number'] in visited:
            continue

        new_total_time = total_time + float(flight['flight_time'])

        if path:
            new_total_time += 1  # transfer time

        if new_total_time > float(max_time):
            continue

        new_path = path + [flight]
        if flight['destination_spaceport_id'] == destination_port:
            itineraries.append(new_path)
        elif max_stops > 0:
            # next leg must depart at least 1 hour later, and within 6 hours
            new_time = (datetime.strptime(str(flight['departure_time']), "%H:%M:%S") +
                        timedelta(hours=float(flight['flight_time']) + 1)).time()
            if new_time <= datetime.strptime("23:59:59", "%H:%M:%S").time():
                itineraries.extend(
                    search_paths(flight['destination_spaceport_id'], destination_port, day, new_time,
                                 max_stops - 1, max_time, new_path, new_total_time)
                )

    cursor.close()
    conn.close()
    return itineraries

# Show the planner window
def show_window():
    win = Toplevel()
    win.title("Flight Finder (Path Planning)")
    win.geometry("700x550")
    win.resizable(False, False)

    ports = fetch_spaceports()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    Label(win, text="Origin Spaceport:").pack()
    origin_var = StringVar()
    origin_box = Combobox(win, textvariable=origin_var, values=list(ports.keys()), width=60, state="readonly")
    origin_box.pack()

    Label(win, text="Destination Spaceport:").pack()
    dest_var = StringVar()
    dest_box = Combobox(win, textvariable=dest_var, values=list(ports.keys()), width=60, state="readonly")
    dest_box.pack()

    Label(win, text="Day of Week:").pack()
    day_var = StringVar()
    day_box = Combobox(win, textvariable=day_var, values=days, width=30, state="readonly")
    day_box.pack()

    Label(win, text="Earliest Departure Time (HH:MM:SS):").pack()
    entry_time = Entry(win, width=30)
    entry_time.pack()

    Label(win, text="Max Stops (0 for direct only):").pack()
    entry_stops = Entry(win, width=30)
    entry_stops.pack()

    Label(win, text="Max Total Travel Time (hours):").pack()
    entry_max_time = Entry(win, width=30)
    entry_max_time.pack()

    result_area = Text(win, width=85, height=18)
    result_area.pack(pady=10)

    def on_search():
        result_area.delete("1.0", "end")
        o = origin_var.get()
        d = dest_var.get()
        if not o or not d or o == d:
            messagebox.showerror("Input Error", "Please select different origin and destination.")
            return
        try:
            earliest = entry_time.get().strip()
            max_stops = int(entry_stops.get().strip())
            max_time = float(entry_max_time.get().strip())
            routes = search_paths(ports[o], ports[d], day_var.get(), earliest, max_stops, max_time)
            if not routes:
                result_area.insert("end", "No available routes found.\n")
            else:
                for idx, route in enumerate(routes, 1):
                    result_area.insert("end", f"Itinerary {idx} (Total Legs: {len(route)}):\n")
                    for f in route:
                        result_area.insert("end", f"  Flight {f['flight_number']} from {f['origin_spaceport_id']} to {f['destination_spaceport_id']} | "
                                                  f"Dep: {f['departure_time']} | Duration: {f['flight_time']} hrs | Spacecraft: {f['type_name']}\n")
                    result_area.insert("end", "\n")
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    Button(win, text="Find Route", command=on_search).pack(pady=5)
