
from tkinter import Toplevel, Label, Entry, Button, messagebox, StringVar
from tkinter.ttk import Combobox
import mysql.connector
import os

# Read database config from db_config.txt
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

# Establish MySQL connection
def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

# Fetch all planets for dropdown options
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

# Insert a new space station into the database
def insert_station(name, location_type, planet_id, orbiting_id):
    if not name or not location_type or not planet_id:
        messagebox.showerror("Input Error", "Name, location type and owner planet are required.")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        orbiting = int(orbiting_id) if orbiting_id else None
        cursor.execute(
            "INSERT INTO spacestation (name, location_type, planet_id, orbiting_planet_id) VALUES (%s, %s, %s, %s)",
            (name, location_type, int(planet_id), orbiting)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"SpaceStation '{name}' added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Insertion failed: {e}")

# GUI window to add a space station
def show_window():
    win = Toplevel()
    win.title("Add SpaceStation")
    win.geometry("400x330")
    win.resizable(False, False)

    planets = fetch_planets()
    planet_map = {f"{name} (ID:{pid})": pid for pid, name in planets}
    options = list(planet_map.keys())

    Label(win, text="Station Name:").pack(pady=3)
    entry_name = Entry(win, width=35)
    entry_name.pack()

    Label(win, text="Location Type (orbit / space):").pack(pady=3)
    entry_type = Entry(win, width=35)
    entry_type.pack()

    Label(win, text="Owner Planet:").pack(pady=3)
    planet_var = StringVar()
    planet_box = Combobox(win, textvariable=planet_var, values=options, state="readonly", width=32)
    planet_box.pack()

    Label(win, text="Orbiting Planet (optional):").pack(pady=3)
    orbit_var = StringVar()
    orbit_box = Combobox(win, textvariable=orbit_var, values=options, state="readonly", width=32)
    orbit_box.pack()

    # On submit, validate and insert
    def on_submit():
        name = entry_name.get().strip()
        location_type = entry_type.get().strip()
        selected_owner = planet_var.get()
        selected_orbit = orbit_var.get()
        planet_id = planet_map.get(selected_owner)
        orbiting_id = planet_map.get(selected_orbit) if selected_orbit else None
        insert_station(name, location_type, planet_id, orbiting_id)
        entry_name.delete(0, 'end')
        entry_type.delete(0, 'end')

    Button(win, text="Add SpaceStation", command=on_submit).pack(pady=10)
