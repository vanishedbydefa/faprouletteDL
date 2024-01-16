import sqlite3
import os

def get_all_ids_from_db(db_path:str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM img_data;")
    rows = cursor.fetchall()
    conn.close()
    ids = [i[0] for i in rows]
    return ids


def get_max_id_from_db(db_path:str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM img_data")
    highest_id_downloaded = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(seq) FROM sqlite_sequence")
    highest_id_general = cursor.fetchone()[0]
    conn.close()

    if highest_id_downloaded == None and highest_id_general == None:
        return None
    elif highest_id_downloaded == None or highest_id_general == None:
        print("ERROR: It seems like one table in the database is missing.")
        print("This should not occure from normal usage of 'faproulette-downloader'.")
        print("The program itself will not fix this issue. Think about deleting your DB and start downloading from zero again")
        print("You can also download an existing DB from github and use the downloader in speed mode.")
    elif highest_id_downloaded < highest_id_general:
        print(f"highest ID: {highest_id_general}")
        return highest_id_general
    else:
        print(f"highest ID: {highest_id_downloaded}")
        return highest_id_downloaded


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
