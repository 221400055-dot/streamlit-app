import copy

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

        # Room capacity check
        if self.exam_sizes[exam] > self.room_capacities[chosen_room]:
            return False
        
        for other_exam, (other_slot, other_room) in assignment.items():
            # Same time slot constraints
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

        unassigned = [v for v in self.variables if v not in assignment]
        exam = unassigned[0]

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


# -----------------------------------------------------------
# USER INPUT INTERFACE (Console Form)
# -----------------------------------------------------------

print("\n--- Exam Timetable Scheduler (CSP Based) ---\n")

# Number of exams
num_exams = int(input("Enter number of subjects: "))
exams = []

for i in range(num_exams):
    exams.append(input(f"Enter subject {i+1} name: "))

# Rooms
num_rooms = int(input("\nEnter number of rooms: "))
rooms = []
room_caps = {}

for i in range(num_rooms):
    room = input(f"Enter room {i+1} name: ")
    rooms.append(room)
    room_caps[room] = int(input(f"Capacity of {room}: "))

# Time slots
num_slots = int(input("\nEnter number of time slots: "))
slots = []
for i in range(num_slots):
    slots.append(input(f"Slot {i+1} (e.g., Monday 9AM): "))

# Student enrollments
enrollments = {}
print("\nEnter enrolled students for each exam (comma-separated):")
for exam in exams:
    students = input(f"Students in {exam}: ").replace(" ", "").split(",")
    enrollments[exam] = set(students)

# Teacher assignments
teachers = {}
print("\nEnter teacher for each exam:")
for exam in exams:
    teachers[exam] = input(f"Teacher for {exam}: ")

# Create and solve CSP
scheduler = ExamSchedulerCSP(exams, slots, rooms, enrollments, room_caps, teachers)
solution = scheduler.backtrack({}, scheduler.domains)

print("\n--- Generated Timetable ---")
if solution:
    for exam, (slot, room) in solution.items():
        print(f"{exam}: {slot} in {room}")
else:
    print("No valid timetable possible with these constraints.")
