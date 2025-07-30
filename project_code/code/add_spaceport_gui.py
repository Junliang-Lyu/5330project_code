
from tkinter import Toplevel, Label, Entry, Button, messagebox, StringVar
from tkinter.ttk import Combobox
import mysql.connector
import os

# Read DB config from file
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

# Establish connection
def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

# Fetch existing planets
def fetch_planets():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT planet_id, name FROM planet")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except:
        return []

# Fetch existing space stations
def fetch_stations():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT station_id, name FROM spacestation")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except:
        return []

# Insert a new spaceport
def insert_spaceport(name, capacity, fee, planet_id, station_id):
    if not name or not capacity or not fee:
        messagebox.showerror("Input Error", "Name, capacity and fee are required.")
        return
    if planet_id and station_id:
        messagebox.showerror("Input Error", "A spaceport can only belong to a planet or a station, not both.")
        return
    if not planet_id and not station_id:
        messagebox.showerror("Input Error", "Select either a planet or a station.")
        return
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO spaceport (name, capacity_limit, fee_per_seat, planet_id, station_id) VALUES (%s, %s, %s, %s, %s)",
            (name, int(capacity), int(fee), planet_id, station_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"Spaceport '{name}' added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Insertion failed: {e}")

# GUI window to add spaceport
def show_window():
    win = Toplevel()
    win.title("Add Spaceport")
    win.geometry("400x360")
    win.resizable(False, False)

    planets = fetch_planets()
    stations = fetch_stations()
    planet_map = {f"{name} (ID:{pid})": pid for pid, name in planets}
    station_map = {f"{name} (ID:{sid})": sid for sid, name in stations}

    Label(win, text="Spaceport Name:").pack(pady=3)
    entry_name = Entry(win, width=35)
    entry_name.pack()

    Label(win, text="Capacity Limit (Integer):").pack(pady=3)
    entry_capacity = Entry(win, width=35)
    entry_capacity.pack()

    Label(win, text="Fee per Seat (Integer):").pack(pady=3)
    entry_fee = Entry(win, width=35)
    entry_fee.pack()

    Label(win, text="Select Planet (optional):").pack(pady=3)
    planet_var = StringVar()
    planet_box = Combobox(win, textvariable=planet_var, values=list(planet_map.keys()), width=32, state="readonly")
    planet_box.pack()

    Label(win, text="Select SpaceStation (optional):").pack(pady=3)
    station_var = StringVar()
    station_box = Combobox(win, textvariable=station_var, values=list(station_map.keys()), width=32, state="readonly")
    station_box.pack()

    def on_submit():
        name = entry_name.get().strip()
        capacity = entry_capacity.get().strip()
        fee = entry_fee.get().strip()
        planet_id = planet_map.get(planet_var.get())
        station_id = station_map.get(station_var.get())
        insert_spaceport(name, capacity, fee, planet_id, station_id)
        entry_name.delete(0, 'end')
        entry_capacity.delete(0, 'end')
        entry_fee.delete(0, 'end')

    Button(win, text="Add Spaceport", command=on_submit).pack(pady=10)
