Folder Overview

File / Folder Name              Description
--------------------           --------------------------------------------------
main.py                        Main entry point. Run this to launch the GUI.
db_config.txt                  Database config file (edit to match your MySQL settings)
reset_database.py              Clears all tables and resets auto-increment (use with caution)
test_data(generate_by_gpt).txt Sample test data insert statements
add_*.py                       GUI modules for adding data (planet, flight, etc.)
query_*.py                     Query modules
flight_finder.py               Flight path planner with time/stop constraints
new_flight_creator.py          Extra credit: smart flight creation assistant
__pycache__/                   Python cache (can be ignored)

How to Use

Make sure you’ve created a database named `intergalactic_travel` and run the schema SQL file to set up the tables.

Edit `db_config.txt` with your database info:

host=localhost  
port=3306  
user=your_mysql_username  
password=your_mysql_password  
database=intergalactic_travel

Run the program:

