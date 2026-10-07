Name: Joshua Fabusuyi | Course: Python
STUDENT GRADE MANAGER
=====================

A console program for managing a class: add students, record scores,
see averages and letter grades, and view a ranked class report.

HOW TO RUN
----------
1. Install Python 3 (no extra packgit --versionages needed).
2. Open a terminal in the folder containing grade_manager.py.
3. Run:   python grade_manager.py      (or python3 grade_manager.py)

MENU OPTIONS
------------
1. Add student            5. Record scores for a student
2. View all students      6. Delete student
3. View one student       7. Class report (highest, lowest, class average)
4. Update student         8. Search students by part of a name
0. Exit                   9. Export class report to CSV

GRADING SCALE
-------------
A: 90-100   B: 80-89   C: 70-79   D: 60-69   F: below 60
(Edit GRADE_BOUNDARIES at the top of the code to change this.)

FILES
-----
students.json     Created automatically. All data is saved here after every
                  change and loaded when the program starts.
class_report.csv  Created when you choose option 9.

NOTES
-----
- Scores must be numbers from 0 to 100; invalid input is re-asked.
- If students.json is missing or empty, the program starts with an empty
  class. If it is corrupted, it is renamed to students.json.bak.
- Student names are not case-sensitive ("ada" and "Ada" are the same student).
