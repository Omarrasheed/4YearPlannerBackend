import simplejson as json
import unittest
from datetime import datetime
from sqlalchemy import inspect
from flask import Flask, jsonify
from app import app,db,base
from sqlalchemy.orm import joinedload
import requests
import json

titleList = []
allClasses = []

"""# Pull all subjects and append to titleList
response = requests.get("https://classes.cornell.edu/api/2.0/config/subjects.json?roster=FA18").text
data = json.loads(str(response))
for each in data['data']['subjects']:
	titleList.append(str(each['value']))

def pullInfoForSubject(subj):
	request = "https://classes.cornell.edu/api/2.0/search/classes.json?roster=FA18&subject=" + subj
	response = requests.get(request).text
	data = json.loads(str(response))
	for each in data['data']['classes']:
		# Initialize new list for class
		classObject = []

		# Subject Attribute
		newSubject = each['subject'].encode("utf-8")
		newSubject = newSubject.replace('\xc2\xa0', ' ')
		classObject.append(newSubject)

		# Class Number Attribute
		newNbr = str(each['catalogNbr'].encode("utf-8"))
		newNbr = newNbr.replace('\xc2\xa0', ' ')
		classObject.append(newNbr)

		# Title Attribute
		newTitle = str(each['titleLong'].encode("utf-8"))
		newTitle = newTitle.replace('\xc2\xa0', ' ')
		classObject.append(newTitle)

		# Description Attribute
		if each['description'] != None:
			newDesc = str(each['description'].encode("utf-8"))
			newDesc = newDesc.replace('\xc2\xa0', ' ')
			classObject.append(newDesc)
		else:
			classObject.append(None)
		
		# Term Attribute
		if each['catalogWhenOffered'] != None:
			newTerm = str(each['catalogWhenOffered'].encode("utf-8"))
			newTerm = newTerm.replace('\xc2\xa0', ' ')
			classObject.append(newTerm)
		else:
			classObject.append(None)
				
		# UnitsMax Attribute
		if each["enrollGroups"][0]["unitsMaximum"] != None:
			classObject.append(str(each["enrollGroups"][0]["unitsMaximum"]))
		else:
			classObject.append(None)
		
		# UnitsMin Attribute
		if each["enrollGroups"][0]["unitsMinimum"] != None:
			classObject.append(str(each["enrollGroups"][0]["unitsMinimum"]))
		else:
			classObject.append(None)
		
		# Prerequisites Attribute
		if each["catalogPrereqCoreq"] != None:

			prereq = str(each['catalogPrereqCoreq'].encode('utf-8'))
			prereq = prereq.replace('\xc2\xa0', ' ')
			classObject.append(prereq)
		else:
			classObject.append(None)
			
		# Grading Type Attribute
		gradingType = str(each['enrollGroups'][0]['gradingBasisShort'].encode('utf-8'))
		classObject.append(gradingType)

		# Distribution Requirements Attribute
		if each['catalogDistr'] != None:
			distr = str(each['catalogDistr'])
			distr = distr.replace('(', '')
			classObject.append(distr)
		else:
			classObject.append(None)

		# Add each class to final list of classes
		allClasses.append(classObject)
					
# Run Script on each subject in Cornell's database
for each in titleList:
	pullInfoForSubject(each)"""

class test(unittest.TestCase):

	coursePostColumns = [
		'title',
		'subject',
		'number',
		'description',
		'creditsMin',
		'creditsMax',
		'term',
		'prereqs',
		'distribution',
		'gradingType'
	]

	def input_dict_to_args(self, input_dict):
		return '&'.join(['%s=%s' % tup for tup in input_dict.items()])

	def is_sub(self, sub, lst):
		lst_s = set(lst)
		for s in sub:
			if s not in lst_s:
				return False
		return True

	def object_as_dict(self, obj):
		return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

	def commit(self):
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			print(e)

	def post(self, input_data, modelType):
		return self.app.post('/planner/%s?%s' % (modelType, self.input_dict_to_args(input_data)), follow_redirects=False)

	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True
		self.app_context = app.app_context()
		self.app_context.push()

	def tearDown(self):
		db.session.execute('DELETE FROM courses;')
		self.commit()
		self.app_context.pop()

	def test_create_course(self):
		"""for each in allClasses:
			input_data = dict(subject    = each[0],
							number       = each[1],
							title        = each[2],
							description  = each[3],
							term         = each[4],
							creditsMax   = each[5],
							creditsMin   = each[6],
							prereqs      = each[7],
							gradingType  = each[8],
							distribution = each[9])
			result = json.loads(self.post(input_data, 'courses').data)
			assert(self.is_sub(self.coursePostColumns,result['data']['course'].keys()))
			assert(result['success'])"""
		input_data = dict(subject    = 'MATH',
							number   = '1110',
							title    = 'something important',
							term     = 'fall')

		input_data2 = dict(subject    = 'MATHasdf',
							number    = '1110',
							title     = 'something important2',
							term      = 'fall and spring')

		input_data3 = dict(subject    = 'MA',
							number    = '1110',
							title     = 'something important3',
							term      = 'spring')

		result = json.loads(self.post(input_data, 'courses').data)
		result2 = json.loads(self.post(input_data2, 'courses').data)
		result3 = json.loads(self.post(input_data3, 'courses').data)
		assert(self.is_sub(self.coursePostColumns,result['data']['course'].keys()))
		assert(self.is_sub(self.coursePostColumns,result2['data']['course'].keys()))
		assert(self.is_sub(self.coursePostColumns,result3['data']['course'].keys()))
		assert(result['success'])

	def test_get_all_courses(self):
		input_data1 = dict(title    = 'title',
							subject = 'subject',
							number  = '1110',
							term    = 'fall and spring')

		input_data2 = dict(title    = 'title2',
							subject = 'subject2',
							number  = '1110',
							term    = 'fall')

		result = json.loads(self.post(input_data1, 'courses').data)
		result2 = json.loads(self.post(input_data2, 'courses').data)
		all_result = json.loads(self.app.get('/planner/courses').data)
		courses = all_result['data']['courses']
		assert(len(courses) == 2)
		for each in range(len(courses)):
			assert(self.is_sub(self.coursePostColumns,courses[each].keys()))
		assert(all_result['success'])

	def test_subject(self):
		result_id = dict(subject = 'MATH')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
				assert(self.is_sub(self.coursePostColumns,each.keys()))
				assert('MATH' in each['subject'])
		assert(result['success'])
		print('just subjects passed')
				
				
	def test_terms(self):
		result_id = dict(term = 'fall and spring')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term'])        
			assert(result['success'])

		result_id = dict(term = 'fall')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term'])
			assert(result['success'])
													
		result_id = dict(term = 'spring')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term'])
			assert(result['success'])

		print('just terms passed')

	def test_number(self):
		result_id= dict(number = '1110')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('1110' in each['number'])
			assert(result['success'])
																														
			print('just number passed')
																																		
	def test_subject_number(self):
		result_id= dict(subject='MATH',number='1110')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('MATH' in each['subject'] and '1110' in each['number'])
			assert(result['success'])

		print('subject + number passed')
																																												
	def test_subject_term(self):
		result_id= dict(subject='MATH',term='fall')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('MATH' in each['subject'] and ('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term']))
			assert(result['success'])

		print('subject + term passed')

	def test_number_term(self):
		result_id= dict(number='1110', term='spring')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('1110' in each['number'] and ('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term']))
			assert(result['success'])

		print('number + term passed')  

	def test_subject_number_term(self):
		result_id= dict(subject='MATH', number='1110', term='spring')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('MATH' in each['subject'] and '1110' in each['number'] and ('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term']))
			assert(result['success'])
		print('subject + number + term passed')

if __name__ == '__main__':
	unittest.main()
