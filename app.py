import streamlit as st
import copy

# ---------------- CSP CLASS (UNCHANGED LOGIC) ----------------
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

        if self.exam_sizes[exam] > self.room_capacities[chosen_room]:
            return False

        for other_exam, (other_slot, other_room) in assignment.items():
            if chosen_slot == other_slot:
                if chosen_room == other_room:
                    return False
                if self.student_enrollments[exam].intersection(self.student_enrollments[other_exam]):
                    return False
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

exams = []
for i in range(num_exams):
    exams.append(st.text_input(f"Subject {i+1} name"))

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

slots = []
for i in range(num_slots):
    slots.append(st.text_input(f"Slot {i+1} (e.g., Monday 9AM)"))

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
    solution = scheduler.backtrack({}, scheduler.domains)

    st.subheader("Generated Timetable")

    if solution:
        for exam, (slot, room) in solution.items():
            st.success(f"{exam}: {slot} in {room}")
    else:
        st.error("No valid timetable possible with these constraints.")
