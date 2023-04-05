from flask import render_template, request, redirect, url_for
from sqlalchemy import func

from nd_testas.forms import NewTestForm, NewQuestionForm
from nd_testas.models import Test, User, Result, Score, Question, Answer
from nd_testas import app, db


@app.route('/')
def index():
    tests = Test.query.all()
    return render_template('index.html', tests=tests)


@app.route('/test/<int:test_id>')
def test(test_id):
    test = Test.query.get(test_id)
    score = request.args.get('score')
    name = request.args.get('name')
    user = User.query.filter_by(name=name).first()
    if user:
        selected_results = Result.query.filter_by(test_id=test_id, user_id=user.id).all()
        selected_answer_ids = [result.answer_id for result in selected_results]
    else:
        selected_answer_ids = []
    results = db.session.query(User.name, Score.score). \
        join(Score, Score.user_id == User.id). \
        filter(Score.test_id == test_id).all()

    sorted_list = sorted(results, key=lambda x: x[1], reverse=True)
    return render_template('test.html', test=test, score=score, name=name, results=sorted_list, selected_answer_ids=selected_answer_ids)


@app.route('/submit_test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    name = request.form['name']
    selected_answers = request.form.getlist('answers[]')
    user = User(name=name)
    db.session.add(user)
    db.session.commit()

    test = Test.query.get(test_id)
    correct_answers = []
    for question in test.questions:
        for answer in question.answers:
            if answer.is_correct:
                correct_answers.append(str(answer.id))

    score = 0
    for selected_answer, question in zip(selected_answers, test.questions):
        result = Result(test=test, user=user, question_id=question.id, answer_id=selected_answer)
        db.session.add(result)
        db.session.commit()
        if selected_answer in correct_answers:
            score += 1
    score_for_db = Score(user_id=user.id, score=score, test_id=test_id)
    db.session.add(score_for_db)
    db.session.commit()

    return redirect(url_for('test', test_id=test_id, score=score, name=name))


@app.route('/new_test', methods=['GET', 'POST'])
def new_test():
    form = NewTestForm()
    if form.validate_on_submit():
        name = form.name.data
        number_of_questions = form.num_questions.data
        new_test = Test(name=name, num_questions=number_of_questions)
        db.session.add(new_test)
        db.session.commit()
        return redirect(url_for('new_question', test_id=new_test.id))
    return render_template('new_test.html', form=form)


@app.route('/new_question/<int:test_id>', methods=['GET', 'POST'])
def new_question(test_id):
    form = NewQuestionForm()
    if form.validate_on_submit():
        main_quest = form.question.data
        question = Question(text=main_quest, test_id=test_id)
        db.session.add(question)
        db.session.commit()
        question_id = question.id
        num_answers = form.num_answers.data
        return redirect(url_for('answers', question_id=question_id, num_answers=num_answers, test_id=test_id))
    return render_template('new_question.html', test_id=test_id, form=form)


@app.route('/answers/<int:question_id>/<int:num_answers>/<int:test_id>', methods=['GET', 'POST'])
def answers(question_id, num_answers, test_id):
    next_button = True
    finish_button = True
    if request.method == 'POST':
        answers = {}
        for i in range(num_answers):
            answer_key = "answer-" + str(i)
            checkbox_key = "checkbox-" + str(i)
            answer_value = request.form.get(answer_key)
            checkbox_value = request.form.get(checkbox_key)
            answers[answer_key] = answer_value
            answers[checkbox_key] = checkbox_value
            if not checkbox_value:
                is_correct = False
            else:
                is_correct = True
            answer = Answer(text=answer_value, is_correct=is_correct, question_id=question_id)
            db.session.add(answer)
            db.session.commit()

        if 'next' in request.form:
            return redirect(url_for('new_question', test_id=test_id, question_id=question_id))
        elif 'finish' in request.form:
            num_rows = db.session.query(func.count(Question.text)).filter(Question.test_id == test_id).scalar()
            test = Test.query.get(test_id)
            test.num_questions = num_rows
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('answers.html', question_id=question_id, number_of_answers=num_answers, test_id=test_id, next_button=next_button, finish_button=finish_button)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=8000, debug=True)
