from app.constants import *
import requests
from flask import request
import json
from . import *

@planner.route('/courses', methods=['POST'])
def boards_crud():

	"""
	Route for creating new courses
	"""

	subject      = request.args.get('subject')
	number       = request.args.get('number')
	title        = request.args.get('title')
	description  = request.args.get('description')
	term         = request.args.get('term')
	creditsMax   = request.args.get('creditsMax')
	creditsMin   = request.args.get('creditsMin')
	prereqs      = request.args.get('prereqs')
	gradingType  = request.args.get('gradingType')
	distribution = request.args.get('distribution')
	acadGroup    = request.args.get('acadGroup')

	course = courses_dao.create_course(subject,
										number,
										title,
										description,
										term,
										creditsMax,
										creditsMin,
										prereqs,
										gradingType,
										distribution,
										acadGroup)

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
							'prereqs': prereqs,
							'gradingType': gradingType,
							'distribution': distribution,
							'acadGroup': acadGroup
							}
						}
					})
@planner.route('/courses', methods=['GET'])
def pull():
	"""
	Handles all routes for queries
	"""
	parameterDict = {}

	requestedSubject = request.args.get('subject')
	requestedNumber  = request.args.get('number')
	requestedTerm    = request.args.get('term')
	recommended      = request.args.get('recommended')

	if requestedSubject != None:
		parameterDict['subject'] = requestedSubject
	if requestedNumber != None:
		parameterDict['number'] = requestedNumber
	if requestedTerm != None:
		parameterDict['term'] = requestedTerm
	if recommended != None:
		parameterDict['recommended'] = recommended
	query = courses_dao.begin_filter(parameterDict)
	jsonList = []
	for each in query:
		jsonList.append({'title': each.title,
						'number': each.number,
						'subject': each.subject,
						'description': each.description,
						'term': each.term,
						'creditsMin': each.creditsMin,
						'creditsMax': each.creditsMax,
						'prereqs': each.prereqs,
						'id': each.id,
						'gradingType': each.gradingType,
						'distribution': each.distribution,
						'acadGroup': each.acadGroup
						})
	return jsonify({'success': True,
						'data': {
							'courses': jsonList}})
