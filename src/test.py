import simplejson as json
import unittest
from datetime import datetime
from sqlalchemy import inspect
from flask import Flask, jsonify
from app import app,db,base
from sqlalchemy.orm import joinedload
import requests
import json
import unicodedata

subjectList = []
allClasses = []

def pullSubjects(season, year):
	""" 
	Pull all subjects and append to subjectList
	"""
	response = requests.get("https://classes.cornell.edu/api/2.0/config/subjects.json?roster=" + season[:2].upper() + str(year%100)).text
	data = json.loads(str(response))
	for each in data['data']['subjects']:
		subjectList.append(str(each['value']))

def pullInfoForSubject(subj, season, year):
	"""
	Pull all of the classes from Cornell API & parse information
	Only takes:
		Title
		Subject
		Class Number
		Description
		Term offered in
		Max amount of units offered for
		Minimum amount of units offered for
		Prerequisites
		Grading type
		Distribution
		Academic Group
	"""

	request = "https://classes.cornell.edu/api/2.0/search/classes.json?roster=" + season[:2].upper() + str(year%100) + "&subject=" + subj
	response = requests.get(request).text
	data = json.loads(response)
	for each in data['data']['classes']:
		if each['enrollGroups'][0]['classSections'][0]['campus'] == 'MAIN':
			# Initialize new list for class
			classObject = {}

			# Subject Attribute
			newSubject = unicodedata.normalize('NFKD', each['subject']).encode('ascii', 'ignore')
			classObject['subject'] = newSubject
			
			# Class Number Attribute
			newNbr = unicodedata.normalize('NFKD', each['catalogNbr']).encode('ascii', 'ignore')
			classObject['number'] = newNbr

			# Title Attribute
			newTitle = unicodedata.normalize('NFKD', each['titleLong']).encode('ascii', 'ignore')
			classObject['title'] = newTitle

			# Description Attribute
			if each['description'] != None:
				newDesc = unicodedata.normalize('NFKD', each['description']).encode('ascii', 'ignore')
				classObject['description'] = newDesc
			else:
				classObject['description'] = None
		
			# Term Attribute
			if each['catalogWhenOffered'] != None:
				newTerm = unicodedata.normalize('NFKD', each['catalogWhenOffered']).encode('ascii', 'ignore')
				classObject['term'] = newTerm
			else:
				classObject['term'] = None
					
			# UnitsMax Attribute
			if each["enrollGroups"][0]["unitsMaximum"] != None:
				unitsMax = str(each['enrollGroups'][0]['unitsMaximum'])
				classObject['unitsMax'] = unitsMax
			else:
				classObject['unitsMax'] = None
			
			# UnitsMin Attribute
			if each["enrollGroups"][0]["unitsMinimum"] != None:
				unitsMin = str(each['enrollGroups'][0]['unitsMinimum'])
				classObject['unitsMin'] = unitsMin
			else:
				classObject['unitsMin'] = None
			
			# Prerequisites Attribute
			if each["catalogPrereqCoreq"] != None:
				prereq = unicodedata.normalize('NFKD', each['catalogPrereqCoreq']).encode('ascii', 'ignore')
				classObject['prereqs'] = prereq
			else:
				classObject['prereqs'] = None
				
			# Grading Type Attribute
			gradingType = unicodedata.normalize('NFKD', each['enrollGroups'][0]['gradingBasisShort']).encode('ascii', 'ignore')
			classObject['gradingType'] = gradingType

			# Distribution Requirements Attribute
			if each['catalogDistr'] != None:
				distr = str(each['catalogDistr'])
				distr = distr.replace('(', '')
				distr = distr.replace(')', '')
				classObject['distribution'] = distr
			else:
				classObject['distribution'] = None

			acadGroup = unicodedata.normalize('NFKD', each['acadGroup']).encode('ascii', 'ignore')
			classObject['acadGroup'] = acadGroup

			subjNum = newSubject + " " + str(newNbr)
			classObject['subjNum'] = subjNum

			# Add each class to final list of classes
			allClasses.append(classObject)

def runScript(season, year):

	pullSubjects(season, year)
	for subject in subjectList:
		pullInfoForSubject(subject, season, year)

runScript('fall', 2018)

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
		'gradingType',
		'acadGroup',
		'subjNum'
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
		db.session.execute('DELETE FROM course;')
		self.commit()
		self.app_context.pop()

	def test_create_course(self):

		# UNCOMMENT WHEN ADDING TO THE DATABASE
		
		for each in allClasses:
			input_data = dict(subject    = each['subject'],
							number       = each['number'],
							title        = each['title'],
							description  = each['description'],
							term         = each['term'],
							creditsMax   = each['unitsMax'],
							creditsMin   = each['unitsMin'],
							prereqs      = each['prereqs'],
							gradingType  = each['gradingType'],
							distribution = each['distribution'],
							acadGroup    = each['acadGroup'],
							subjNum      = each['subjNum'])
			result = json.loads(self.post(input_data, 'courses').data)
			assert(self.is_sub(self.coursePostColumns,result['data']['course'].keys()))
			assert(result['success'])
		
		"""
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
		assert(result['success'])"""

	def test_get_all_courses(self):
		input_data1 = dict(title    = 'title',
							subject = 'subject',
							number  = '1110',
							term    = 'fall and spring')

		input_data2 = dict(title    = 'title2',
							subject = 'subject2',
							number  = '1110',
							term    = 'fall')

		

		"""result = json.loads(self.post(input_data1, 'courses').data)
		result2 = json.loads(self.post(input_data2, 'courses').data)"""
		all_result = json.loads(self.app.get('/planner/courses').data)
		courses = all_result['data']['courses']
		assert(len(courses) == len(allClasses))
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

	def test_academic_group(self):
		result_id= dict(recommended='AS')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		courses = result['data']['courses']
		for each in courses:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert(each['acadGroup'] == 'AS')
			assert(result['success'])
		print('Academic Group passed')
if __name__ == '__main__':
	unittest.main()
