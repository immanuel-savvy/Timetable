from json import JSONEncoder
import math

instructors = [str(i+1) for i in range(7)]
instructors_et_course = {
	"1": ['n+','a+','s+','server','ceh','cissp'],
	"2": ['graphic_design','ui/ux','digital_marketing','online_marketing'],
	"3": ['javascript','nodejs/express','mobile_app_dev'],
	"4": ['python', 'data_science', 'excel'],
	"5": ['java', 'jupyterbook', 'publisher', 'google_adwords'],
	"6": ['html/css', 'bootstrap', 'anaconda', 'seo'],
	"7": ['jquery', 'flutter', 'flutterwave', 'paystack', 'api'],
}
dow = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
timeframe = 60*90
instructors_dayoff = {
	dow[0]: [],
	dow[1]: ['1','4'],
	dow[2]: ['2'],
	dow[3]: ['3','7'],
	dow[4]: ['5', '6'],
}

three_time_course = ['javascript', 'python', 'graphic_design', 'ceh',
                     'server', 'api', 'html/css', 'java']
time_slots = [1,2,3,4]

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

classrooms = 5

instructors_counter = dict()
for i in instructors:
	instructors_counter[i] = 0

recent_instructor = instructors[0]
instructor_course_counter = 0

for day in timetable.keys():
	day_courses = list()
	for i in range(4):
		time_frame = list()
		for classroom in range(classrooms):
			should_break = False
			while len(time_frame) < classrooms:
				has_instructor = False
				for instructor_ in instructors:
					if instructors_workload[instructor_][day]:
						has_instructor = True
				print(instructors_workload[instructor_], day)
				if not has_instructor: break
				print('me')
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

fileset = open('./my_file.json','w')
print(JSONEncoder().encode(timetable), file=fileset)
