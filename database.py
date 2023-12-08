import sqlite3
import os


def get_max_id_from_db(db_path:str):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute the SQL query
    cursor.execute("SELECT MAX(id) FROM img_data")

    # Fetch the result
    highest_id = cursor.fetchone()[0]

    # Close the connection
    conn.close()
    return highest_id


def check_db_entry_exists(db_path:str, id_value:int):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute a SELECT query to check if the entry exists
    cursor.execute('SELECT * FROM img_data WHERE id = ?', (id_value,))
    result = cursor.fetchone()  # Fetches the first row that matches the condition

    conn.close()

    # Check if the result is not None (entry exists) or None (entry does not exist)
    return result is not None

# Function to insert data into the database
def insert_or_update_entry(db_path:str, id_value:int , name:str, category:str, download_date, url:str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the entry exists
    cursor.execute('SELECT * FROM img_data WHERE id = ?', (id_value,))
    existing_entry = cursor.fetchone()

    if existing_entry:
        # If the entry exists, update it
        cursor.execute('''
            UPDATE img_data
            SET name=?, category=?, download_date=?, url=?
            WHERE id=?
        ''', (name, category, download_date, url, id_value))
    else:
        # If the entry does not exist, insert a new one
        cursor.execute('''
            INSERT INTO img_data (id, name, category, download_date, url)
            VALUES (?, ?, ?, ?, ?)
        ''', (id_value, name, category, download_date, url))

    conn.commit()
    conn.close()

# Function to create a new database if it doesn't exist
def create_new_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS img_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            download_date DATE,
            url TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
# Function to check if the database exists
def check_db_exists(db_path):
    if not os.path.exists(db_path):
        print("    - Database not found. Creating a new one...")
        create_new_db(db_path)
        print("    - Database created at", db_path)
    else:
        print("    - Database already exists at", db_path)
