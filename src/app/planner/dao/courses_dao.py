from app.constants import *
from . import *

"""
Add more methods below!!!
"""

def begin_filter(parameterDictionary):
	keys = parameterDictionary.keys()
	if 'term' in keys:
		finalList = courses_by_term(parameterDictionary['term'], query)
		return finalList
	if 'subject' in keys and 'number' in keys:
		query = Course.query.filter_by(subject.like("%" + "%s" % parameterDictionary['subject'] + "%"), number.like("%" + "%s" % parameterDictionary['number'] + "%"))
	elif 'subject' in keys:
		query = Course.query.filter_by(subject.like("%" + "%s" % parameterDictionary['subject'] + "%"))
	elif 'number' in keys:
		query = Course.query.filter_by(number.like("%" + "%s" % parameterDictionary['number'] + "%"))
	else:
		query = Course.query.all()
	return query


def courses_by_term(term,query):
	"""
	Get Courses by Term
	"""
	finalList = []
	realFall = "Fall"
	realSpring = "Spring"
	secondSpring = "spring"

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


def create_course(subject, number, title, description, term, creditsMax, creditsMin, prereqs, gradingType, distribution):
	"""
	Create new course
	"""
	course = Course(subject      =subject,
					number       =number, 
					title        =title, 
					description  =description,
					term         =term,
					creditsMax   =creditsMax,
					creditsMin   =creditsMin,
					prereqs      =prereqs,
					gradingType  =gradingType,
					distribution =distribution)
	db.session.add(course)
	try:
		db.session.commit()
		return course
	except Exception as e:
		db.session.rollback()
		return e
