import sqlite3

# Define the get_db_connection function here
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_number TEXT NOT NULL,
        dob TEXT NOT NULL, -- store DOB as text in YYYY-MM-DD format
        name TEXT,
        standard TEXT,
        term TEXT,
        tamil INTEGER,
        english INTEGER,
        math INTEGER,
        science INTEGER,
        social INTEGER
    )
    ''')

    # Insert initial student data with consistent date format
    cursor.execute('''
    INSERT INTO students (roll_number, dob, name, standard, term, tamil, english, math, science, social) 
    VALUES ('24CS088', '2005-09-28', 'Gowtham M', '10th', '2', 88, 78, 67, 78, 77),
           ('24CS078', '2004-09-18', 'Murugan M', '11th', '2', 89, 78, 57, 68, 88)
    ''')

    conn.commit()
    conn.close()

# Function to create the quiz_scores table
def create_quiz_scores_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            score INTEGER,
            quiz_date TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    conn.commit()
    conn.close()

# Call these functions to initialize the database and create the quiz_scores table
initialize_database()
create_quiz_scores_table()

if __name__ == '__main__':
    initialize_database()
