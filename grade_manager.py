"""Student Grade Manager

A menu-driven console program for a teacher to manage a class:
add students, record scores, calculate averages and letter grades,
view a class report, and save everything to a JSON file.

Uses only the Python 3 standard library.
"""

import csv
import json
import os

DATA_FILE = "students.json"      # where all student data is saved
CSV_FILE = "class_report.csv"    # where the exported report goes

# Grade boundaries: (minimum average, letter). Change these to suit your school.
GRADE_BOUNDARIES = [(90, "A"), (80, "B"), (70, "C"), (60, "D"),(50, "E")]
FAIL_GRADE = "F"


# --------------------------------------------------------------------------
# Student class
# --------------------------------------------------------------------------
class Student:
    """A student with a name and a dictionary of subject -> score."""

    def __init__(self, name, scores=None):
        self.name = name
        self.scores = scores if scores is not None else {}

    def average(self):
        """Return the average score, or None if there are no scores yet."""
        if not self.scores:
            return None
        return sum(self.scores.values()) / len(self.scores)

    def grade(self):
        """Return the letter grade (A-F), or 'N/A' if there are no scores."""
        avg = self.average()
        if avg is None:
            return "N/A"
        for minimum, letter in GRADE_BOUNDARIES:
            if avg >= minimum:
                return letter
        return FAIL_GRADE

    def to_dict(self):
        """Convert to a plain dict so it can be saved as JSON."""
        return {"name": self.name, "scores": self.scores}

    @classmethod
    def from_dict(cls, data):
        """Build a Student from a dict. Raises ValueError if data is invalid."""
        if not isinstance(data, dict):
            raise ValueError("student entry is not a dictionary")
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValueError("student has no name")
        raw_scores = data.get("scores", {})
        if not isinstance(raw_scores, dict):
            raise ValueError("scores must be a dictionary")
        scores = {}
        for subject, score in raw_scores.items():
            score = float(score)  # raises ValueError/TypeError if bad
            if not 0 <= score <= 100:
                raise ValueError("score out of range")
            scores[str(subject)] = score
        return cls(name, scores)


# --------------------------------------------------------------------------
# Input helpers (all of them re-ask until the input is valid)
# --------------------------------------------------------------------------
def ask_text(prompt, allow_blank=False):
    """Ask for text. Re-asks if blank (unless allow_blank is True)."""
    while True:
        value = input(prompt).strip()
        if value or allow_blank:
            return value
        print("  Input cannot be empty. Please try again.")


def ask_score(prompt):
    """Ask for a score between 0 and 100. Re-asks until valid."""
    while True:
        raw = input(prompt).strip()
        try:
            score = float(raw)
        except ValueError:
            print("  Please enter a number (for example 72 or 85.5).")
            continue
        if 0 <= score <= 100:  # also rejects nan and inf
            return round(score, 2)
        print("  Score must be between 0 and 100.")


def ask_yes_no(prompt):
    """Ask a yes/no question. Returns True for yes."""
    while True:
        answer = input(prompt + " (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please type y or n.")


def ask_menu_choice(prompt, valid_choices):
    """Ask for one of the valid menu choices (a collection of strings)."""
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print("  Invalid choice. Please pick one of: " + ", ".join(valid_choices))


def pause():
    """Wait for Enter so the result stays on screen before the menu returns."""
    input("\nPress Enter to return to the menu...")


# --------------------------------------------------------------------------
# Saving and loading
# --------------------------------------------------------------------------
def make_key(name):
    """Students are stored under their lowercase name so lookups ignore case."""
    return name.strip().lower()


def load_data(filename=DATA_FILE):
    """Load students from a JSON file. Never crashes: returns {} on problems."""
    students = {}
    if not os.path.exists(filename):
        return students  # first run: nothing saved yet

    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read().strip()
        if not content:
            return students  # empty file
        data = json.loads(content)
        if not isinstance(data, list):
            raise ValueError("save file has the wrong structure")
        for entry in data:
            student = Student.from_dict(entry)
            students[make_key(student.name)] = student
    except (OSError, ValueError, TypeError) as error:
        # json.JSONDecodeError is a subclass of ValueError
        print(f"Warning: could not fully read '{filename}' ({error}).")
        backup = filename + ".bak"
        try:
            os.replace(filename, backup)
            print(f"The old file was kept as '{backup}'. Starting fresh.")
        except OSError:
            print("Starting with an empty class.")
        return {}
    return students


def save_data(students, filename=DATA_FILE):
    """Save all students to a JSON file. Returns True on success."""
    temp_name = filename + ".tmp"
    try:
        data = [student.to_dict() for student in students.values()]
        with open(temp_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        os.replace(temp_name, filename)  # safe swap so a crash can't corrupt it
        return True
    except OSError as error:
        print(f"Error: could not save data ({error}).")
        return False


# --------------------------------------------------------------------------
# Lookup helpers
# --------------------------------------------------------------------------
def find_matches(students, text):
    """Return all students whose name contains the text (case-insensitive)."""
    text = text.strip().lower()
    return [s for s in students.values() if text in s.name.lower()]


def pick_student(students, prompt="Student name: "):
    """Ask for a name and return the Student, or None (with a friendly message)."""
    if not students:
        print("There are no students yet. Add one first.")
        return None
    name = ask_text(prompt)
    student = students.get(make_key(name))
    if student:
        return student

    print(f"Sorry, no student named '{name}' was found.")
    similar = find_matches(students, name)
    if similar:
        print("Did you mean: " + ", ".join(s.name for s in similar) + "?")
    return None


def format_average(student):
    """Return the average as text, or '-' when there are no scores."""
    avg = student.average()
    return "-" if avg is None else f"{avg:.2f}"


def ranked_students(students):
    """Return students with scores, sorted by average (highest first)."""
    scored = [s for s in students.values() if s.scores]
    return sorted(scored, key=lambda s: s.average(), reverse=True)


# --------------------------------------------------------------------------
# Menu option functions
# --------------------------------------------------------------------------
def record_scores(student):
    """Keep asking for subject/score pairs until the teacher presses Enter."""
    print("Enter subjects and scores. Leave the subject blank to finish.")
    while True:
        subject = ask_text("  Subject: ", allow_blank=True)
        if not subject:
            break
        score = ask_score(f"  Score for {subject} (0-100): ")
        student.scores[subject] = score


def add_student(students):
    """Add a new student, optionally with scores."""
    name = ask_text("New student's name: ")
    if make_key(name) in students:
        print(f"'{name}' already exists. Use 'Update student' to change them.")
        return False
    student = Student(name)
    if ask_yes_no("Record scores now?"):
        record_scores(student)
    students[make_key(name)] = student
    print(f"Added {name}.")
    return True


def view_students(students):
    """Show a table of all students (sorted by name)."""
    if not students:
        print("No students to show yet.")
        return
    print(f"\n{'Name':<25}{'Subjects':>9}{'Average':>10}{'Grade':>7}")
    print("-" * 51)
    for student in sorted(students.values(), key=lambda s: s.name.lower()):
        print(f"{student.name:<25}{len(student.scores):>9}"
              f"{format_average(student):>10}{student.grade():>7}")


def view_one_student(students):
    """Show every score for one student."""
    student = pick_student(students)
    if not student:
        return
    print(f"\n{student.name}")
    print("-" * 30)
    if not student.scores:
        print("  (no scores recorded yet)")
    for subject, score in student.scores.items():
        print(f"  {subject:<20}{score:>6.2f}")
    print("-" * 30)
    print(f"  Average: {format_average(student)}   Grade: {student.grade()}")


def rename_student(students, student):
    """Rename a student, making sure the new name isn't already taken."""
    new_name = ask_text("New name: ")
    new_key = make_key(new_name)
    if new_key != make_key(student.name) and new_key in students:
        print(f"'{new_name}' already exists. Name not changed.")
        return False
    del students[make_key(student.name)]
    student.name = new_name
    students[new_key] = student
    print(f"Renamed to {new_name}.")
    return True


def update_student(students):
    """Rename a student, change/add a score, or remove a subject."""
    student = pick_student(students)
    if not student:
        return False
    print(f"\nUpdating {student.name}:")
    print("  1. Rename student")
    print("  2. Change or add a score")
    print("  3. Remove a subject")
    print("  0. Cancel")
    choice = ask_menu_choice("Choose: ", ("1", "2", "3", "0"))

    if choice == "1":
        return rename_student(students, student)
    if choice == "2":
        record_scores(student)
        return True
    if choice == "3":
        if not student.scores:
            print("This student has no subjects to remove.")
            return False
        subject = ask_text("Subject to remove: ")
        # match subject names ignoring case
        for existing in list(student.scores):
            if existing.lower() == subject.lower():
                del student.scores[existing]
                print(f"Removed {existing}.")
                return True
        print(f"'{subject}' was not found for {student.name}.")
    return False


def delete_student(students):
    """Delete a student after confirmation."""
    student = pick_student(students)
    if not student:
        return False
    if ask_yes_no(f"Really delete {student.name}?"):
        del students[make_key(student.name)]
        print(f"Deleted {student.name}.")
        return True
    print("Cancelled. Nothing was deleted.")
    return False


def record_scores_menu(students):
    """Menu option: record scores for an existing student."""
    student = pick_student(students)
    if not student:
        return False
    record_scores(student)
    return True


def class_report(students):
    """Show highest, lowest and class average, sorted by average."""
    ranked = ranked_students(students)
    if not ranked:
        print("No scores recorded yet, so there is nothing to report.")
        return
    class_average = sum(s.average() for s in ranked) / len(ranked)

    print("\n=========== CLASS REPORT ===========")
    print(f"{'Rank':<6}{'Name':<22}{'Average':>9}{'Grade':>7}")
    print("-" * 44)
    for rank, student in enumerate(ranked, start=1):
        print(f"{rank:<6}{student.name:<22}{student.average():>9.2f}{student.grade():>7}")
    print("-" * 44)
    print(f"Highest:       {ranked[0].name} ({ranked[0].average():.2f})")
    print(f"Lowest:        {ranked[-1].name} ({ranked[-1].average():.2f})")
    print(f"Class average: {class_average:.2f}")

    unscored = [s.name for s in students.values() if not s.scores]
    if unscored:
        print("No scores yet: " + ", ".join(unscored))


def search_students(students):
    """Search students by part of their name."""
    if not students:
        print("There are no students yet.")
        return
    text = ask_text("Search for: ")
    matches = find_matches(students, text)
    if not matches:
        print(f"No students match '{text}'.")
        return
    print(f"\nFound {len(matches)} match(es):")
    for student in sorted(matches, key=lambda s: s.name.lower()):
        print(f"  {student.name:<25} Average: {format_average(student):>6}  "
              f"Grade: {student.grade()}")


def export_csv(students, filename=CSV_FILE):
    """Export the class report (sorted by average) to a CSV file."""
    ranked = ranked_students(students)
    if not ranked:
        print("No scores recorded yet, so there is nothing to export.")
        return
    subjects = sorted({subject for s in ranked for subject in s.scores})
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Rank", "Name"] + subjects + ["Average", "Grade"])
            for rank, student in enumerate(ranked, start=1):
                row = [rank, student.name]
                row += [student.scores.get(subject, "") for subject in subjects]
                row += [f"{student.average():.2f}", student.grade()]
                writer.writerow(row)
        print(f"Report exported to '{filename}'.")
    except OSError as error:
        print(f"Error: could not write the CSV file ({error}).")


# --------------------------------------------------------------------------
# Main menu
# --------------------------------------------------------------------------
MENU = """
========= STUDENT GRADE MANAGER =========
  1. Add student
  2. View all students
  3. View one student's scores
  4. Update student
  5. Record scores for a student
  6. Delete student
  7. Class report
  8. Search students by name
  9. Export class report to CSV
  0. Exit
"""


def main():
    """Run the menu loop until the user chooses Exit."""
    students = load_data()
    print(f"Loaded {len(students)} student(s) from '{DATA_FILE}'.")

    # Options that change data return True when something changed.
    changing_actions = {
        "1": add_student,
        "4": update_student,
        "5": record_scores_menu,
        "6": delete_student,
    }
    viewing_actions = {
        "2": view_students,
        "3": view_one_student,
        "7": class_report,
        "8": search_students,
        "9": export_csv,
    }

    try:
        while True:
            print(MENU)
            choice = ask_menu_choice("Choose an option (0-9): ", tuple("0123456789"))
            if choice == "0":
                break
            if choice in changing_actions:
                if changing_actions[choice](students):
                    save_data(students)  # auto-save after every change
            else:
                viewing_actions[choice](students)
            pause()  # keep the result visible until the user is ready
    except (KeyboardInterrupt, EOFError):
        print("\nInput closed. Saving and exiting...")

    save_data(students)
    print("Data saved. Goodbye!")


if __name__ == "__main__":
    main()
