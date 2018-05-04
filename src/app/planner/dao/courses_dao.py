from app.constants import *
from . import *

"""
Add more methods below!!!
"""

def course_by_title(course_title):
  	"""
  	Get board by ID
  	"""
  	return Course.query.filter_by(title=course_title).first()

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
