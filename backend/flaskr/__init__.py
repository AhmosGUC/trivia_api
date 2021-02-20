import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

    CORS(app)

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        categories = [category.format()['id'] for category in categories]
        return jsonify({'success': True, 'categories': categories})

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    def pagination(request, questions):
        page = request.args.get("page", 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        current_questions = questions[start:end]
        return current_questions

    @app.route('/questions', methods=['GET'])
    def get_questions():
        categories = Category.query.all()
        # categories = [category.format() for category in categories]
        current_category = categories[0].id
        categories = [category.format() for category in categories]
        # print(current_category['type'])
        questions = Question.query.filter(
            Question.category == current_category).all()
        questions = [question.format() for question in questions]
        current_questions = pagination(request, questions)
        if len(current_questions) == 0:
            abort(404)
        else:
            return jsonify({'questions': current_questions,
                            'total_questions': len(questions),
                            'categories': categories,
                            'current_category': current_category})

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:q_id>', methods=["DELETE"])
    def delete_question(q_id):
        q = Question.query.get(q_id)
        if q is None:
            abort(422)
        else:
            q.delete()
            return jsonify({'deleted': q_id})

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=["POST"])
    def create_question():
        q_data = request.get_json()
        q = Question(q_data["question"],
                     q_data["answer"],
                     q_data["category"],
                     q_data["difficulty"])
        q.insert()
        return jsonify({'success': True})

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/questions/<search_term>', methods=["POST"])
    def search_questions(search_term):
        search_term = '%'+str(search_term)+'%'
        search_term = search_term.lower()
        questions = Question.query.filter(
            Question.question.like(search_term)).all()
        questions = [question.format() for question in questions]
        return jsonify({"questions": questions})

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:cid>/questions', methods=["GET"])
    def get_questions_with_category(cid):
        search_category = Category.query.get(cid)
        if search_category is None:
            abort(404)
        else:
            search_category = search_category.format()['id']
            questions = Question.query.filter(
                Question.category == search_category).all()
            questions = questions = [question.format()
                                     for question in questions]
            return jsonify({'questions': questions})

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def play():
        form = request.get_json()
        prev_quest = form['previous_questions']
        category = form['quiz_category']
        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(
                Question.category == category['id']).all()
        questions = [question.format() for question in questions]
        while len(questions) != 0:
            q = random.randint(0, len(questions)-1)
            if questions[q]['id'] in prev_quest:
                del questions[q]
            else:
                return jsonify({'question': questions[q]})
        return jsonify({'success': False})
    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'not found', 'status': 404}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({'message': 'unprocessable', 'status': 422}), 422

    return app
