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
        self.assertEqual(len(data['questions']), 1)
        self.question.delete()

    def test_search_term_no_match(self):
        res = self.client().post('/questions/'+'j5k52s')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        # self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 0)

    def test_create_question(self):
        with self.app.app_context():
            body = dict(
                question="qtest",
                answer="atest",
                category=1,
                difficulty=1)
            res = self.client().post('/questions', data=json.dumps(body),
                                     content_type='application/json')
            self.assertEqual(res.status_code, 200)

    # def test_get_question_with_category(self):
    #     self.question.insert()
    #     res = self.client().post('/categories/'+str(1)+'/questions')
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data['questions'])
    #     self.assertNotEqual(len(data['questions']), 0)
    #     self.question.delete()

    # def test_get_question_with_wrong_category(self):
    #     return True

    # def test_get_categories(self):
    #     return True

    # def test_play_quiz(self):
    #     return True


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
