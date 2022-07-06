from json import JSONEncoder
from re import sub
import math, os

instructors_map = dict()
instructors = []
instructors_et_course = dict()
dow = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

total_work_time = 60*60*7
timeframe = 60*90
interval_timing = 60*15
classrooms = 5

instructors_dayoff = dict()
for d in dow:
	instructors_dayoff[d] = list()

three_time_course = list()

_three_time_course = "$three time courses"
_settings = "$settings"
current_instructor_mapping = None
current_instructor_naming = None

def split_time_string(time_string):
	time_string = sub(' ','', time_string).lower()
	hr_index = 0
	min_index = hr_index
	hr = min = 0

	try:
		hr_index = time_string.index('hr')
		hr = int(time_string[:hr_index])
	except ValueError:
		hr_index = 0
		hr = 0
	try:
		min_index = time_string.index('min')
		min = int(time_string[hr_index + 2 if hr_index else 0:min_index])
	except ValueError:
		min = 0

	timeframe = (hr * 60 * 60) + (min * 60)
	return timeframe

def load_instructors_et_courses_settings():
	global current_instructor_mapping, current_instructor_naming, \
		timeframe, interval_timing, classrooms
	try:
		payload = open('%s/timetable.csv'%os.environ['HOME'], 'r').read()
		split_rows = payload.split('\n')

		split_rows= [row for row in split_rows if row]
		for j in range(len(split_rows)):
			row = split_rows[j].strip(',')

			cells = row.split(',')
			cells = [cell for cell in cells if cell]
			for i in range(len(cells)):
				cell = cells[i].strip()
				if i == 0:
					current_instructor_naming = cell
					current_instructor_mapping = str(j+1)
					if cell.lower() == _three_time_course:
						pass
					elif cell.lower() == _settings:
						pass
					else:
						instructors_et_course[current_instructor_mapping] = list()
						instructors_map[cell] = current_instructor_mapping
						instructors.append(current_instructor_mapping)
				elif i+1 == len(cells) and j+1 < len(split_rows):
					if not list(instructors_dayoff.keys()).count(cell):
						if current_instructor_naming != _settings:
							instructors_et_course[current_instructor_mapping]\
								.append(cell)

					else:
						instructors_dayoff[cell].append(current_instructor_mapping)
				else:
					if current_instructor_naming.lower() == _three_time_course:
						three_time_course.append(cell)
					elif current_instructor_naming.lower() == _settings:
						key_value = cell.split(':')
						if len(key_value) != 2:
							continue
						if key_value[0] == 'timeframe':
							timeframe = split_time_string(key_value[1]) or timeframe
						elif key_value[0] == 'interval_timing':
							interval_timing = split_time_string(key_value[1]) \
							                  or interval_timing
						elif key_value[0] == 'classrooms':
							try:
								classrooms = int(key_value[1])
							except ValueError:
								classrooms = 5
					else:
						instructors_et_course[current_instructor_mapping].append(cell)

	except FileNotFoundError:
		print("No Timetable file .csv;")
		exit()

load_instructors_et_courses_settings()

time_slots = 0
while total_work_time > timeframe:
	total_work_time -= timeframe
	total_work_time -= interval_timing
	time_slots += 1

def find_instructor_by_course(course):
	for instructor in instructors_et_course.keys():
		if instructors_et_course[instructor].count(course):
			return instructor

timetable = dict()
for day in dow:
	timetable[day] = list()

courses = list()
for course in instructors_et_course.values():
	courses.extend(course)

total_course_frequencies = 0
courses_frequency = dict()
for course in courses:
	if three_time_course.count(course):
		courses_frequency[course] = 3
		total_course_frequencies += 3
	else:
		courses_frequency[course] = 2
		total_course_frequencies += 2
print("Weekdays Time Utility: %d"%(total_course_frequencies) + "%")

instructors_workload = dict()
for course in courses_frequency.keys():
	instructor = find_instructor_by_course(course)
	try:
		instructors_workload[instructor] += courses_frequency[course]
	except KeyError:
		instructors_workload[instructor] = courses_frequency[course]
_instructors_workload = instructors_workload.copy()
instructors_workload.clear()

instructor_day_count = dict()
for i in instructors:
	instructors_workload[i] = dict()
	instructor_day_count[i] = 0

for instructor in instructors_workload.keys():
	instructor_workload = _instructors_workload[instructor]
	for day_index in range(len(dow)):
		today = dow[day_index]
		if instructors_dayoff[today].count(instructor):
			continue

		day_count = instructor_day_count[instructor]
		today_wl = 0
		if day_count == 2:
			today_wl = math.ceil(instructor_workload / 2)
		elif day_count == 3:
			today_wl = instructor_workload
		else:
			today_wl = math.ceil(instructor_workload * .25)
		instructors_workload[instructor][today] = today_wl
		instructor_workload -= today_wl
		instructor_day_count[instructor] += 1
for instructor in _instructors_workload.keys():
	print("Instructor %s: %d"%
	      (instructor, (_instructors_workload[instructor]/20)*100)+"%")

instructors_counter = dict()
for i in instructors:
	instructors_counter[i] = 0

recent_instructor = instructors[0]
instructor_course_counter = 0

week_courses = list()
for day in timetable.keys():
	day_courses = list()
	for i in range(time_slots):
		time_frame = list()
		for classroom in range(classrooms):
			should_break = False
			for instructor in \
					instructors[instructors.index(recent_instructor):]:
				if instructors.index(recent_instructor)+1 == len(instructors):
					recent_instructor = instructors[0]
				else:
					recent_instructor = instructor
				if instructors_dayoff[day].count(instructor) or \
						not instructors_workload[instructor][day]:
					continue

				if len(time_frame) == classrooms:
					should_break = True
					break

				instructor_courses = instructors_et_course[instructor]
				instructor_counter = instructors_counter[instructor]
				if len(instructor_courses) <= instructor_counter:
					instructor_counter = 0

				if instructor_course_counter < len(instructor_courses):
					course = instructor_courses[instructor_course_counter]
					while True:
						if (week_courses.count(course) == 3 and
								three_time_course.count(course) )or \
								(week_courses.count(course) == 2 and
								not three_time_course.count(course)):
							course = instructor_courses[instructor_course_counter]
							if instructor_course_counter+1 < len(instructor_courses):
								instructor_course_counter += 1
							else: instructor_course_counter = 0
						else: break

					if day_courses.count(course):
						instructor_course_counter = 0
						continue

					should_continue = False
					for course_ in time_frame:
						if find_instructor_by_course(course_) == instructor:
							should_continue = True
					if should_continue: continue

					instructors_workload[instructor][day] -= 1
					time_frame.append(course)
					day_courses.append(course)
					week_courses.append(course)
					if instructor_course_counter + 1 == len(instructor_courses):
						instructor_course_counter = 0
					else:
						instructor_course_counter = instructor_course_counter + 1

				instructors_counter[instructor] = instructor_counter + 1
			if should_break:
				should_break = False
				break
		timetable[day].append((time_frame.copy()))
		time_frame.clear()
	timetable[day].sort(key=lambda x: len(x), reverse=True)
	day_courses.clear()

missing_courses = list()
def find_missing_courses():
	for course in courses*3:  # Recursive hack to run loop thrice
		if week_courses.count(course) == 3 and \
				three_time_course.count(course):
			pass
		elif week_courses.count(course) == 2 and \
			not three_time_course.count(course):
			pass
		else: missing_courses.append(course)
find_missing_courses()

def reinforce():
	for instructor in instructors_workload.keys():
		for day in instructors_workload[instructor]:
			if day:
				timeday = timetable[day]
				has_space = False
				for time_day in timeday:
					pass
				for time_ in timeday:
					if len(time_) < classrooms:
						not_for_instructor = False
						for time_course in time_:
							if find_instructor_by_course(time_course) == instructor:
								not_for_instructor = True
								break
						if not not_for_instructor:
							has_space = True
				if not has_space:
					for d in dow:
						timeday = timetable[d]
						has_space = False
						for time_ in timeday:
							if len(time_) < classrooms:
								not_for_instructor = False
								for time_course in time_:
									if find_instructor_by_course(time_course) == instructor:
										not_for_instructor = True
										break
								if not not_for_instructor:
									has_space = True
						if has_space: break

				for time_frame in timeday:
					if len(time_frame) < classrooms:
						in_time_frame = False
						for course in time_frame:
							if find_instructor_by_course(course) == instructor:
								in_time_frame = True
						if not in_time_frame:
							for missing_course in missing_courses:
								should_continue_ = False
								for tf in timeday:
									if tf.count(missing_course):
										should_continue_ = True
										break
								if should_continue_: continue

								if find_instructor_by_course(missing_course) \
										== instructor:
									if instructors_workload[instructor][day]:
										time_frame.append(missing_course)
										missing_courses\
											.pop(missing_courses.index(missing_course))
										instructors_workload[instructor][day] -= 1
										break


reinforce()

fileset = open('./my_file.json','w')
print(JSONEncoder().encode(timetable), file=fileset)

print(instructors_workload)
