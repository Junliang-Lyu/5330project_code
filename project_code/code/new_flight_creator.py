
from tkinter import Toplevel, Label, Entry, Button, messagebox, StringVar, OptionMenu
import mysql.connector
import os

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

def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

def simple_input(title, prompt):
    from tkinter.simpledialog import askstring
    return askstring(title, prompt)

def show_window():
    win = Toplevel()
    win.title("New Flight Creator")
    win.geometry("400x600")
    conn = connect_db()
    cursor = conn.cursor()

    Label(win, text="Step 1: Select Origin and Destination").pack(pady=10)
    cursor.execute("SELECT spaceport_id, name FROM spaceport")
    ports = cursor.fetchall()
    port_map = {f"{name} (ID:{pid})": pid for pid, name in ports}
    origin_var = StringVar()
    dest_var = StringVar()
    OptionMenu(win, origin_var, *port_map.keys()).pack()
    OptionMenu(win, dest_var, *port_map.keys()).pack()

    def step1_continue():
        if not origin_var.get() or not dest_var.get():
            messagebox.showerror("Error", "Please select both origin and destination.")
            return
        oid = port_map[origin_var.get()]
        did = port_map[dest_var.get()]
        cursor.execute("SELECT route_id, distance FROM route WHERE origin_spaceport_id=%s AND destination_spaceport_id=%s", (oid, did))
        route = cursor.fetchone()
        if not route:
            distance = simple_input("New Route", "Enter distance between ports:")
            cursor.execute("INSERT INTO route (origin_spaceport_id, destination_spaceport_id, distance) VALUES (%s, %s, %s)", (oid, did, distance))
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            route_id = cursor.fetchone()[0]
        else:
            route_id = route[0]
            distance = route[1]
        step2(route_id, distance)

    Button(win, text="Next Step", command=step1_continue).pack(pady=10)

    def step2(route_id, distance):
        top = Toplevel(win)
        top.title("Step 2: Choose Spacecraft")
        cursor.execute("SELECT craft_type_id, type_name, `range` FROM spacecraft_type WHERE `range` >= %s", (distance,))
        options = cursor.fetchall()
        if not options:
            messagebox.showerror("Error", "No spacecraft can travel this distance.")
            top.destroy()
            return
        Label(top, text="Select a spacecraft:").pack(pady=5)
        craft_map = {f"{name} (ID:{cid}, Range: {r})": cid for cid, name, r in options}
        craft_var = StringVar()
        OptionMenu(top, craft_var, *craft_map.keys()).pack()
        def confirm_craft():
            if not craft_var.get():
                messagebox.showerror("Error", "Please select a spacecraft.")
                return
            craft_id = craft_map[craft_var.get()]
            top.destroy()
            step3(route_id, craft_id)
        Button(top, text="Next Step", command=confirm_craft).pack(pady=10)

    def step3(route_id, craft_id):
        top = Toplevel(win)
        top.title("Step 3: Create Flight")
        Label(top, text="Flight Number:").pack()
        num_entry = Entry(top)
        num_entry.pack()
        Label(top, text="Departure Time (HH:MM:SS):").pack()
        dep_entry = Entry(top)
        dep_entry.pack()
        Label(top, text="Flight Time (hrs):").pack()
        time_entry = Entry(top)
        time_entry.pack()
        def create_flight():
            try:
                cursor.execute(
                    "INSERT INTO flight (flight_number, route_id, craft_type_id, departure_time, flight_time) VALUES (%s, %s, %s, %s, %s)",
                    (num_entry.get(), route_id, craft_id, dep_entry.get(), float(time_entry.get()))
                )
                conn.commit()
                messagebox.showinfo("Success", "Flight created successfully.")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        Button(top, text="Create Flight", command=create_flight).pack(pady=10)

if __name__ == "__main__":
    from tkinter import Tk
    root = Tk()
    root.withdraw()
    show_window()
    root.mainloop()
