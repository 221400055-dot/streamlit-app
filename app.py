import streamlit as st
import copy

# ---------------- CSP CLASS ----------------
class ExamSchedulerCSP:
    def __init__(self, exams, slots, rooms, student_enrollments, room_capacities, teacher_assignments):
        self.variables = exams
        self.domains = {
            exam: [(slot, room) for slot in slots for room in rooms]
            for exam in exams
        }
        self.student_enrollments = student_enrollments
        self.room_capacities = room_capacities
        self.teacher_assignments = teacher_assignments
        self.exam_sizes = {exam: len(students) for exam, students in student_enrollments.items()}

    def is_consistent(self, exam, assignment, slot_room):
        chosen_slot, chosen_room = slot_room

        # 1️⃣ Room capacity constraint
        if self.exam_sizes[exam] > self.room_capacities[chosen_room]:
            return False

        # 2️⃣ Check conflicts with already assigned exams
        for other_exam, (other_slot, other_room) in assignment.items():
            if chosen_slot == other_slot:
                # Room conflict
                if chosen_room == other_room:
                    return False
                # Student conflict
                if self.student_enrollments[exam].intersection(self.student_enrollments[other_exam]):
                    return False
                # Teacher conflict
                if self.teacher_assignments[exam] == self.teacher_assignments[other_exam]:
                    return False
        return True

    def forward_checking(self, exam, slot_room, assignment, local_domains):
        for unassigned in self.variables:
            if unassigned not in assignment and unassigned != exam:
                new_domain = []
                for val in local_domains[unassigned]:
                    if self.is_consistent(unassigned, {**assignment, exam: slot_room}, val):
                        new_domain.append(val)
                local_domains[unassigned] = new_domain
                # 3️⃣ Empty domain check
                if not new_domain:
                    return False
        return True

    def backtrack(self, assignment, local_domains):
        if len(assignment) == len(self.variables):
            return assignment

        exam = [v for v in self.variables if v not in assignment][0]

        for slot_room in local_domains[exam]:
            if self.is_consistent(exam, assignment, slot_room):
                assignment[exam] = slot_room
                temp = copy.deepcopy(local_domains)
                if self.forward_checking(exam, slot_room, assignment, temp):
                    result = self.backtrack(assignment, temp)
                    if result:
                        return result
                del assignment[exam]
        return None

# ---------------- STREAMLIT UI ----------------
st.title("Exam Timetable Scheduler (CSP Based)")

st.header("Basic Information")
num_exams = st.number_input("Number of subjects", min_value=1, step=1)
exams = [st.text_input(f"Subject {i+1} name") for i in range(num_exams)]

num_rooms = st.number_input("Number of rooms", min_value=1, step=1)
rooms = []
room_caps = {}
for i in range(num_rooms):
    room = st.text_input(f"Room {i+1} name")
    cap = st.number_input(f"Capacity of room {i+1}", min_value=1, step=1)
    if room:
        rooms.append(room)
        room_caps[room] = cap

num_slots = st.number_input("Number of time slots", min_value=1, step=1)
slots = [st.text_input(f"Slot {i+1} (e.g., Monday 9AM)") for i in range(num_slots)]

st.header("Enrollments & Teachers")
enrollments = {}
teachers = {}
for exam in exams:
    students = st.text_input(f"Students in {exam} (comma separated)")
    enrollments[exam] = set(students.replace(" ", "").split(",")) if students else set()
    teachers[exam] = st.text_input(f"Teacher for {exam}")

# ---------------- RUN BUTTON ----------------
if st.button("Generate Timetable"):
    scheduler = ExamSchedulerCSP(exams, slots, rooms, enrollments, room_caps, teachers)

    conflict_messages = []

    # 1️⃣ Room capacity check
    for exam in exams:
        if scheduler.exam_sizes[exam] > max(room_caps.values()):
            conflict_messages.append(f"Exam '{exam}' cannot fit in any room due to capacity ({scheduler.exam_sizes[exam]} students).")

    # Only proceed if no immediate room capacity conflicts
    if conflict_messages:
        for msg in conflict_messages:
            st.error(msg)
    else:
        solution = scheduler.backtrack({}, scheduler.domains)

        if solution:
            st.subheader("Generated Timetable")
            for exam, (slot, room) in solution.items():
                st.success(f"{exam}: {slot} in {room}")
        else:
            # 2️⃣ Detailed conflict checks if backtracking fails
            st.error("No valid timetable possible with these constraints. Possible conflicts include:")

            # Check for student conflicts
            student_conflicts = []
            teacher_conflicts = []
            room_conflicts = []

            # Compare every pair of exams
            for i in range(len(exams)):
                for j in range(i+1, len(exams)):
                    e1, e2 = exams[i], exams[j]
                    students_overlap = enrollments[e1].intersection(enrollments[e2])
                    same_teacher = teachers[e1] == teachers[e2]
                    for slot in slots:
                        # Potential slot conflict
                        if students_overlap:
                            student_conflicts.append(f"{e1} and {e2} share students: {', '.join(students_overlap)}")
                        if same_teacher:
                            teacher_conflicts.append(f"{e1} and {e2} have the same teacher: {teachers[e1]}")

            # Room conflicts (same slot, same room)
            for room in rooms:
                exams_in_room = [e for e in exams if scheduler.exam_sizes[e] <= room_caps[room]]
                if len(exams_in_room) > 1:
                    room_conflicts.append(f"Multiple exams may need room '{room}' at same slot.")

            # Display all conflicts
            for msg in set(student_conflicts + teacher_conflicts + room_conflicts):
                st.warning(msg)
 
