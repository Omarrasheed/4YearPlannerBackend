from app.constants import *
from . import *

"""
Add more methods below!!!
"""

def begin_filter(parameterDictionary):
	"""
	Determines which filteres were given and queries based on them
	"""
	keys = parameterDictionary.keys()
	if 'subject' in keys and 'number' in keys:
		query = Course.query.filter(Course.subject.like(parameterDictionary['subject'] + "%"), Course.number.like(parameterDictionary['number'] + "%")).order_by(Course.subject, Course.number).all()
	elif 'subject' in keys:
		query = Course.query.filter(Course.subject.like(parameterDictionary['subject'] + "%")).order_by(Course.subject, Course.number).all()
	elif 'number' in keys:
		query = Course.query.filter(Course.number.like(parameterDictionary['number'] + "%")).order_by(Course.subject, Course.number).all()
	elif 'recommended' in keys:
		query = Course.query.filter_by(acadGroup=parameterDictionary['recommended']).order_by(Course.subject, Course.number).all()
		query += Course.query.filter(Course.acadGroup != parameterDictionary['recommended']).order_by(Course.subject, Course.number).all()
	else:
		query = Course.query.order_by(Course.subject, Course.number).all()
	if 'term' in keys:
		finalList = courses_by_term(parameterDictionary['term'], query)
		return finalList
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

def create_course(subject, number, title, description, term, creditsMax, creditsMin, prereqs, gradingType, distribution, acadGroup):
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
					distribution =distribution,
					acadGroup    =acadGroup)

	db.session.add(course)
	try:
		db.session.commit()
		return course
	except Exception as e:
		db.session.rollback()
		return e
