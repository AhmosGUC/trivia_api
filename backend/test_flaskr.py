import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'postgres:1485@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.question = Question("Question Test search term here", "Ans", 1, 4)
        # question.insert()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_pagination_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        # self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        # self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertLessEqual(len(data['questions']), 10)

    def test_page_not_found(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        # self.assertEqual(data['success'], True)
        self.assertTrue(data['status'])
        self.assertTrue(data['message'])
        self.assertEqual(data['status'], 404)
        self.assertEqual(data['message'], 'not found')

    def test_delete_question(self):
        q = Question.query.first()
        q_id = q.id
        res = self.client().delete('/questions/'+str(q_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['deleted'])
        self.assertEqual(data['deleted'], q_id)
        q = Question.query.get(q_id)
        self.assertEqual(q, None)

    def test_delete_wrong_id_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertTrue(data['status'])
        self.assertEqual(data['status'], 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_term_match(self):
        self.question.insert()
        res = self.client().post('/questions/'+'search term')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertGreaterEqual(len(data['questions']), 1)
        self.question.delete()

    def test_search_term_no_match(self):
        res = self.client().post('/questions/'+'j5k52s')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        # self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 0)

    def test_create_question(self):
        body = dict(
            question="qtest",
            answer="atest",
            category=1,
            difficulty=1)
        res = self.client().post('/questions', data=json.dumps(body),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 200)

    def test_get_question_with_category(self):
        self.question.insert()
        test_cat = 1
        res = self.client().get('/categories/'+str(test_cat)+'/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        for question in data['questions']:
            self.assertEqual(test_cat, question["category"])
        self.question.delete()

    def test_get_question_with_wrong_category(self):
        test_cat = 1000
        res = self.client().get('/categories/'+str(test_cat)+'/questions')
        self.assertEqual(res.status_code, 422)

    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['categories'])

    def test_play_quiz(self):
        body = dict(
            previous_questions=[],
            quiz_category=dict(id=0, type=None))
        res1 = self.client().post('/quizzes', data=json.dumps(body),
                                  content_type='application/json')
        res2 = self.client().post('/quizzes', data=json.dumps(body),
                                  content_type='application/json')

        q1 = json.loads(res1.data)
        q2 = json.loads(res2.data)

        self.assertTrue(q1['question'])
        self.assertTrue(q2['question'])
        self.assertEqual(q1['success'], True)
        self.assertNotEqual(q1['question']['id'], q2['question']['id'])

    def test_play_quiz_fail(self):
        body = dict(
            previous_questions=[16, 17, 18, 19],
            quiz_category=dict(id=2, type=None))
        res1 = self.client().post('/quizzes', data=json.dumps(body),
                                  content_type='application/json')
        q1 = json.loads(res1.data)
        self.assertEqual(q1['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
