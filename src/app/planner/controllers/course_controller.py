from app.constants import *
import requests
from flask import request
import json
from . import *

@planner.route('/courses', methods=['POST'])
def boards_crud():
	subject = request.args.get('subject')
	number = request.args.get('number')
	title = request.args.get('title')
	description = request.args.get('description')
	term = request.args.get('term')
	creditsMax = request.args.get('creditsMax')
	creditsMin = request.args.get('creditsMin')
	prereqs = request.args.get('prereqs')
	course = courses_dao.create_course(subject,
							number,
							title,
							description,
							term,
							creditsMax,
							creditsMin,
							prereqs)
	query = courses_dao.course_by_title(course.title)
  	return jsonify({'success': True,
  					'data': {
  						'course': {
  							'title': query.title,
  							'number': query.number,
  							'subject': query.subject,
  							'description': query.description,
  							'term': query.term,
  							'creditsMin': query.creditsMin,
  							'creditsMax': query.creditsMax,
  							'prereqs': query.prereqs,
  							'id': query.id
  						}
  					}})
@planner.route('/courses', methods=['GET'])
def pull():
	if request.args.get('title') == None:
		query = courses_dao.all_courses()
		for each in query:
		jsonList.append({'title': query.title,
  						'number': query.number,
  						'subject': query.subject,
  						'description': query.description,
  						'term': query.term,
  						'creditsMin': query.creditsMin,
  						'creditsMax': query.creditsMax,
  						'prereqs': query.prereqs,
  						'id': query.id
  						})
		return jsonify({'success': True,
						'data':{
							'courses': jsonList
							}})
	else:
		title = request.args.get("title")
		query = courses_dao.course_by_title(title)
		return jsonify({'success': True,
  						'data': {
  							'course': {
  								'title': query.title,
  								'number': query.number,
  								'subject': query.subject,
  								'description': query.description,
  								'term': query.term,
  								'creditsMin': query.creditsMin,
  								'creditsMax': query.creditsMax,
  								'prereqs': query.prereqs,
  								'id': query.id
  							}
  						}})