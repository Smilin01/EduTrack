import sqlite3

# Connect to your SQLite database
# If database.db is in the same directory, you can use the relative path
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Identify duplicates (this step is optional, just to see if duplicates exist)
cursor.execute('''
SELECT roll_number, name, COUNT(*) as count 
FROM students 
GROUP BY roll_number, name 
HAVING count > 1;
''')
duplicates = cursor.fetchall()
if duplicates:
    print("Duplicates found:")
    for duplicate in duplicates:
        print(duplicate)
else:
    print("No duplicates found.")

# Remove duplicates, keeping only one entry for each roll_number and name combination
cursor.execute('''
DELETE FROM students 
WHERE rowid NOT IN (
    SELECT MIN(rowid) 
    FROM students 
    GROUP BY roll_number, name
);
''')

# Commit the changes to the database
conn.commit()

# Verify that duplicates have been removed
cursor.execute('''
SELECT roll_number, name, COUNT(*) as count 
FROM students 
GROUP BY roll_number, name 
HAVING count > 1;
''')
remaining_duplicates = cursor.fetchall()
if not remaining_duplicates:
    print("Duplicates successfully removed!")
else:
    print("Some duplicates still exist:", remaining_duplicates)

# Close the connection
conn.close()
