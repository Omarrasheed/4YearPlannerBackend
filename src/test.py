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
    db.session.execute('DELETE FROM course;')
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

  """def test_delete_board(self):
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

  def test_get_board(self):
    input_data = dict(title='My Awesome Board')
    result_id = json.loads(self.post(input_data, 'boards').data)['data']['board']['id']
    input_data1 = dict(
      board_id=result_id,
      description='A Todo Task, I should get this done!',
      category='inprogress')
    input_data2 = dict(
      board_id=result_id,
      description='A Todo Task, I should get this done!',
      category='inprogress')
    input_data3 = dict(
      board_id=result_id,
      description='A Todo Task, I should get this done!',
      category='todo')
    input_data4 = dict(
      board_id=result_id,
      description='A Todo Task, I should get this done!',
      category='done')
    self.post(input_data1, 'board_elements')
    self.post(input_data2, 'board_elements')
    self.post(input_data3, 'board_elements')
    self.post(input_data4, 'board_elements')
    result = json.loads(self.app.get('/kanban/boards/%s' % result_id).data)
    board = result['data']['board']
    assert(len(board['todo']) ==  1)
    assert(len(board['inprogress']) ==  2)
    assert(len(board['done']) ==  1)
    assert(self.is_sub(self.boardGetColumns,board.keys()))
    assert(self.is_sub(self.elementPostColumns,board['todo'][0].keys()))
    assert(result['success'])

  def test_advance_element(self):
    input_data = dict(title='My Awesome Board')
    result_id = json.loads(self.post(input_data, 'boards').data)['data']['board']['id']
    input_data1 = dict(
      board_id=result_id,
      description='A Todo Task, I should get this done!',
      category='inprogress')
    input_data2 = dict(
      board_id=result_id,
      description='A Todo Task, I should get this done!',
      category='inprogress')
    input_data3 = dict(
      board_id=result_id,
      description='A Todo Task, I should get this done!',
      category='todo')
    input_data4 = dict(
      board_id=result_id,
      description='A Todo Task, I should get this done!',
      category='done')
    self.post(input_data1, 'board_elements')
    self.post(input_data2, 'board_elements')
    result_id2 = json.loads(self.post(input_data3, 'board_elements').data)['data']['board_element']['id']
    result_id3 = json.loads(self.post(input_data4, 'board_elements').data)['data']['board_element']['id']
    result = json.loads(self.app.get('/kanban/boards').data)
    assert(result['data']['boards'][0]['todo_count'] == 1)
    assert(result['data']['boards'][0]['inprogress_count'] == 2)
    assert(result['data']['boards'][0]['done_count'] == 1)
    input_data1 = dict(id=result_id2)
    result = json.loads(self.post(input_data1, 'board_elements/advance').data)
    assert(result == {'success': True})
    input_data2 = dict(id=result_id3)
    self.post(input_data2, 'board_elements/advance')
    result = json.loads(self.app.get('/kanban/boards').data)
    assert(result['data']['boards'][0]['todo_count'] == 0)
    assert(result['data']['boards'][0]['inprogress_count'] == 3)
    assert(result['data']['boards'][0]['done_count'] == 1)"""

if __name__ == '__main__':
  unittest.main()
