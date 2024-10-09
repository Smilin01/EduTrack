CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT NOT NULL,
    dob TEXT NOT NULL,
    name TEXT,
    standard TEXT,
    term TEXT,
    tamil INTEGER,
    english INTEGER,
    math INTEGER,
    science INTEGER,
    social INTEGER
);

INSERT INTO students (roll_number, dob, name, standard, term, tamil, english, math, science, social)
VALUES ('24CS088', '28/09/2005', 'Gowtham M', '10th', '2', 88, 78, 67, 78, 77),
       ('24CS078', '18/09/2004', 'Murugan M', '11th', '2', 89, 78, 57, 68, 88);

CREATE TABLE IF NOT EXISTS quiz_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    score INTEGER,
    quiz_date TEXT,
    FOREIGN KEY (student_id) REFERENCES students (id)
);
