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
	return jsonify({'success': True,
									'data': {
										'course': {
											 'title': title,
											 'number': number,
											 'subject': subject,
											 'description': description,
											 'term': term,
											 'creditsMin': creditsMin,
											 'creditsMax': creditsMax,
											 'prereqs': prereqs
							}
						}})
@planner.route('/courses', methods=['GET'])
def pull():
	jsonList = []
	if request.args.get('subject') == None and request.args.get('term') == None:
		print('hit first')
		query = courses_dao.all_courses()
		
		for each in query:
			jsonList.append({'title': each.title,
							'number': each.number,
							'subject': each.subject,
							'description': each.description,
							'term': each.term,
							'creditsMin': each.creditsMin,
							'creditsMax': each.creditsMax,
							'prereqs': each.prereqs,
							'id': each.id
							})
		return jsonify({'success': True,
						'data':{
							'courses': jsonList
							}})
	elif request.args.get('term') != None:
		print('hit second')
		term = request.args.get("term")
		query = courses_dao.courses_by_term(term)
		for each in query:
			jsonList.append({'title': each.title,
							'number': each.number,
							'subject': each.subject,
							'description': each.description,
							'term': each.term,
							'creditsMin': each.creditsMin,
							'creditsMax': each.creditsMax,
							'prereqs': each.prereqs,
							'id': each.id
							})
		return jsonify({'success': True,
							'data': {
								'courses': jsonList
							}})
	elif request.args.get('subject') != None:
		print('hit third')
		subject = request.args.get('subject')
		query = courses_dao.courses_by_subject(subject)
		for each in query:
			jsonList.append({'title': each.title,
							'number': each.number,
							'subject': each.subject,
							'description': each.description,
							'term': each.term,
							'creditsMin': each.creditsMin,
							'creditsMax': each.creditsMax,
							'prereqs': each.prereqs,
							'id': each.id
							})
		return jsonify({'success': True,
							'data': {
								'courses': jsonList
							}})