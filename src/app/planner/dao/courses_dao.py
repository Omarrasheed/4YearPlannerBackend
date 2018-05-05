from app.constants import *
from . import *

"""
Add more methods below!!!
"""

def courses_by_subject(course_subject):
  	"""
  	Get board by ID
  	"""
  	return Course.query.filter_by(subject=course_subject)

def courses_by_term(term):
	"""
	Get Course by Subject
	"""
	finalList = []
	realFall = "Fall"
	realSpring = "Spring"
	secondSpring = "spring"

	query = Course.query.all()
	for each in query:
		if term == 'fall':
			if (realFall in each.term):
				finalList.append(each)
		elif term == 'spring':
			if (realSpring in each.term) or (secondSpring in each.term):
				finalList.append(each)
		elif term == 'fall and spring':
			if (realFall in each.term) or (realSpring in each.term) or (secondSpring in each.term) :
				finalList.append(each)
	return finalList


def all_courses():
	return Course.query.all()

def create_course(subject, number, title, description, term, creditsMax, creditsMin, prereqs):
	"""
	Create new course
	"""
	course = Course(subject=subject,
					number=number, 
					title=title, 
					description=description,
					term=term,
					creditsMax=creditsMax,
					creditsMin=creditsMin,
					prereqs=prereqs)
	db.session.add(course)
	try:
		db.session.commit()
		return course
	except Exception as e:
		db.session.rollback()
		return e
