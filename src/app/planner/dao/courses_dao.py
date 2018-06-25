from app.constants import *
from . import *
from sqlalchemy.sql import func

"""
Add more methods below!!!
"""

def begin_filter(parameterDictionary):
	"""
	Determines which filteres were given and queries based on them
	"""
	keys = parameterDictionary.keys()

	# Handles Filters
	if 'subject' in keys and 'number' in keys:
		query = Course.query.filter(Course.subject.like(parameterDictionary['subject'] + "%"), Course.number.like(parameterDictionary['number'] + "%")).order_by(func.substr(Course.number, 1, 1), Course.subjNum).all()
	elif 'subject' in keys:
		query = Course.query.filter(Course.subject.like(parameterDictionary['subject'] + "%")).order_by(func.substr(Course.number, 1, 1), Course.subjNum).all()
	elif 'number' in keys:
		query = Course.query.filter(Course.number.like(parameterDictionary['number'] + "%")).order_by(func.substr(Course.number, 1, 1), Course.subjNum).all()
	elif 'recommended' in keys:
		query = Course.query.filter_by(acadGroup=parameterDictionary['recommended']).order_by(func.substr(Course.number, 1, 1), Course.subjNum).all()
		# query += Course.query.filter(Course.acadGroup != parameterDictionary['recommended']).order_by(func.substr(Course.number, 1, 1), Course.subjNum).all()

	# Handles All Courses
	else:
		query = Course.query.order_by(func.substr(Course.number, 1, 1), Course.subjNum).all()
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

def create_course(subject, number, title, description, term, creditsMax, creditsMin, prereqs, gradingType, distribution, acadGroup, subjNum):
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
					acadGroup    =acadGroup,
					subjNum      =subjNum)

	db.session.add(course)
	try:
		db.session.commit()
		return course
	except Exception as e:
		db.session.rollback()
		return e
