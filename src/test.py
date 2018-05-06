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

# Pull all subjects and append to titleList
response = requests.get("https://classes.cornell.edu/api/2.0/config/subjects.json?roster=FA18")
data = response.json()
for each in data['data']['subjects']:
		titleList.append(str(each['value']))

def pullInfoForSubject(subj):
		request = "https://classes.cornell.edu/api/2.0/search/classes.json?roster=FA18&subject=" + subj
		response = requests.get(request)
		data = response.json()
		for each in data['data']['classes']:
				classObject = []
				newSubject = each['subject'].encode("ascii", 'ignore')
				classObject.append(newSubject)
				newNbr = each['catalogNbr'].encode("ascii", 'ignore')
				classObject.append(newNbr)
				newTitle = each['titleLong'].encode('ascii', 'ignore')
				classObject.append(newTitle)
				if each['description'] != None:
					new = each['description'].encode("ascii", 'ignore')
					classObject.append(new)
				else:
					classObject.append(" ")
				
				if each['catalogWhenOffered'] != None:
					new = each['catalogWhenOffered'].encode("ascii", 'ignore')
					classObject.append(new)
				else:
					classObject.append(" ")
				
				if each["enrollGroups"][0]["unitsMaximum"] != None:
					classObject.append(each["enrollGroups"][0]["unitsMaximum"])
				else:
					classObject.append(" ")
				
				if each["enrollGroups"][0]["unitsMinimum"] != None:
					classObject.append(each["enrollGroups"][0]["unitsMinimum"])
				else:
					classObject.append(" ")
				
				if each["catalogPrereqCoreq"] != "":
					classObject.append(each['catalogPrereqCoreq'])
				else:
					classObject.append(" ")
					allClasses.append(classObject)
						
for each in titleList:
		pullInfoForSubject(each)
print(allClasses)

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
	]

	boardGetAllColumns = [
		'inprogress_count',
		'todo_count',
		'title',
		'created_at',
		'updated_at',
		'id',
		'done_count'
	]

	boardGetColumns = [
		'title',
		'created_at',
		'updated_at',
		'done',
		'inprogress',
		'todo',
		'id'
	]

	elementPostColumns = [
		'board_id',
		'category',
		'description',
		'created_at',
		'updated_at',
		'id'
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

	def test_create_board(self):
		


		for each in allClasses:
				input_data = dict(title=each[2],
							subject=each[0],
							number=each[1],
							description=each[3],
							term=each[4],
							creditsMax=each[5],
							creditsMin=each[6],
							prereqs=each[7])
				result = json.loads(self.post(input_data, 'courses').data)
				assert(self.is_sub(self.coursePostColumns,result['data']['course'].keys()))
				assert(result['success'])

	def test_delete_board(self):
		input_data = dict(title='My Awesome Board')
		result = json.loads(self.post(input_data, 'courses').data)
		result_id = int(result['data']['board']['id'])
		input_data = dict(id=result_id)
		result = json.loads(self.app.delete('/planner/courses?%s' % self.input_dict_to_args(input_data), follow_redirects=False).data)
		assert(result == {'success': True})

		boards = json.loads(self.app.get('/planner/courses').data)['data']['boards']
		has_board = len([b['id'] for b in boards if b['id'] == result_id]) > 0
		assert(not has_board)

	def test_get_boards(self):
		input_data1 = dict(title='title',
					subject='subject',
					number='number',
					description='description',
					term='term',
					creditsMax=1,
					creditsMin=0,
					prereqs='prereqs')
		input_data = dict(title='title2',
					subject='subject2',
					number='number2',
					description='description2',
					term='term2',
					creditsMax=12,
					creditsMin=0,
					prereqs='prereqs2')
		result_id1 = json.loads(self.post(input_data1, 'courses').data)['data']['course']['id']
		result_id2 = json.loads(self.post(input_data, 'courses').data)['data']['course']['id']
		result = json.loads(self.app.get('/planner/courses').data)
		boards = result['data']['courses']
		assert(self.is_sub(self.coursePostColumns,boards[0].keys()))
		assert(result['success'])

	def test_subject(self):
		result_id = dict(subject='MATH')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		board = result['data']['courses']
		for each in board:
				assert(self.is_sub(self.coursePostColumns,each.keys()))
				assert(each['subject'] == 'MATH')
		assert(result['success'])
		print('just subjects passed')
				
				
	def test_terms(self):
		result_id = dict(term='fall and spring')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		board = result['data']['courses']
		for each in board:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term'])        
			assert(result['success'])

		result_id = dict(term='fall')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		board = result['data']['courses']
		for each in board:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term'])
			assert(result['success'])
													
		result_id = dict(term='spring')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		board = result['data']['courses']
		for each in board:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term'])
			assert(result['success'])

		print('just terms passed')

	def test_number(self):
		result_id= dict(number='1110')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		board = result['data']['courses']
		for each in board:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert(each['number'] == '1110')
			assert(result['success'])
																														
			print('just number passed')
																																		
	def test_subject_number(self):
		result_id= dict(subject='MATH',number='1110')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		board = result['data']['courses']
		for each in board:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert(each['subject'] == 'MATH' and each['number'] == '1110')
			assert(result['success'])

		print('subject + number passed')
																																												
	def test_subject_term(self):
		result_id= dict(subject='MATH',term='fall')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		board = result['data']['courses']
		for each in board:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert(each['subject'] == 'MATH' and ('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term']))
			assert(result['success'])

		print('subject + term passed')

	def test_number_term(self):
		result_id= dict(number='1110', term='spring')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		board = result['data']['courses']
		for each in board:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert(each['number'] == '1110' and ('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term']))
			assert(result['success'])

		print('number + term passed')  

	def test_subject_number_term(self):
		result_id= dict(subject='MATH', number='1110', term='spring')
		result = json.loads(self.app.get('/planner/courses?%s' % self.input_dict_to_args(result_id)).data)
		board = result['data']['courses']
		for each in board:
			assert(self.is_sub(self.coursePostColumns,each.keys()))
			assert(each['subject'] == 'MATH' and each['number'] == '1110' and ('Spring' in each['term'] or 'spring' in each['term'] or 'Fall' in each['term']))
			assert(result['success'])
		print('subject + number + term passed')

if __name__ == '__main__':
	unittest.main()
