#! usr/bin/python
# coding=utf-8

from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Question, Child
import time

app = Flask(__name__)

engine = create_engine('sqlite:///language_data.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

NUMWORDTEST = 20
NUMRAVENTEST = 6
NUMMEMORYTEST = 5
# 查看ip
@app.route("/ip", methods=["GET"])
def get_my_ip():
    return jsonify(origin=request.headers.get('X-Forwarded-For', request.remote_addr)), 200

# 查看数据库题库
@app.route("/q", methods=["GET"])
def showQ():
    questions = session.query(Question).all()
    return jsonify(questions=[q.serialize for q in questions])

# 查看数据库小孩答题记录
@app.route("/child", methods=["GET"])
def showChild():
    children = session.query(Child).all()
    return jsonify(children=[child.serialize for child in children])

# 返回首页
@app.route('/', methods=['GET'])
def showIndex():
    return render_template('index.html')

# 返回填写信息页
@app.route('/info', methods=['GET'])
def showInfo():
    return render_template('info.html')


# 提交信息，返回单词测试页
@app.route('/begin', methods=['POST'])
def begin():
    newchild = Child()
    newchild.sex = request.form.get('sex')
    newchild.age = request.form.get('age')
    newchild.edu1 = request.form.get('edu1')
    newchild.edu2 = request.form.get('edu2')
    newchild.edu3 = request.form.get('edu3')
    newchild.edu4 = request.form.get('edu4')
    newchild.edu5 = request.form.get('edu5')
    newchild.edu6 = request.form.get('edu6')
    newchild.edu7 = request.form.get('edu7')
    newchild.t0 = str(time.time())
    # 记录孩子信息

    session.add(newchild)
    session.commit()
    # 数据入库

    print "create a new child, id = ", newchild.id

    question = session.query(Question).filter_by(id=1).one()
    # 挑选问题

    return render_template('selection.html',
                           childID=newchild.id,
                           questionID=1,
                           correct=question.correct,
                           word0=question.correct,
                           word1=question.wrong1,
                           word2=question.wrong2,
                           word3=question.wrong3,
                           isLastQuestion=0)

# 提交单测测试的一个题目，返回
@app.route('/wordtest', methods=['POST'])
def wordTest():
    childID = int(request.form.get('childID'))
    questionID = int(request.form.get('questionID'))
    answer = request.form.get('answer')
    # 获取答题信息

    num_ans = updateWordTestResult(childID, questionID, answer)
    # 更新答题信息


    questionID = questionID + 1
    question = session.query(Question).filter_by(id=questionID).one()
    # 挑选新的题目

    return render_template('selection.html',
                           childID=childID,
                           questionID=questionID,
                           correct=question.correct,
                           word0=question.correct,
                           word1=question.wrong1,
                           word2=question.wrong2,
                           word3=question.wrong3,
                           isLastQuestion=1 if num_ans == NUMWORDTEST - 1 else 0)

def updateWordTestResult(childID, questionID, answer):
    question = session.query(Question).filter_by(id=questionID).one()
    updateChild = session.query(Child).filter_by(id=childID).one()

    num_ans = updateChild.num_ans + 1
    if num_ans == 1:
        updateChild.ans1 = answer
        updateChild.q1 = questionID
        updateChild.t1 = str(time.time())
    elif num_ans == 2:
        updateChild.ans2 = answer
        updateChild.q2 = questionID
        updateChild.t2 = str(time.time())
    elif num_ans == 3:
        updateChild.ans3 = answer
        updateChild.q3 = questionID
        updateChild.t3 = str(time.time())

    updateChild.num_ans = num_ans

    session.add(updateChild)
    session.commit()

    print 'word test: childID:{}, questionID:{}, answer:{}, correct:{}, num_ans:{}'.format(childID, questionID, answer, question.correct, num_ans)

    return num_ans


@app.route('/wordtestresult', methods=['GET', 'POST'])
def wordTestResult():
    if request.method == 'POST':
        print "word test over"

        childID = int(request.form.get('childID'))
        questionID = int(request.form.get('questionID'))
        answer = request.form.get('answer')
        if NUMWORDTEST != updateWordTestResult(childID, questionID, answer):
            print "wrong num of questions!"

        pred_age = 15
        return render_template('selection_result.html', pred_age = pred_age, childID=childID)

@app.route('/survey', methods=['GET', 'POST'])
def surveySumbit():
    if request.method == 'POST':
        childID = request.form.get('childID')
        A11 = request.form.get('A11')
        A12 = request.form.get('A12')
        A13 = request.form.get('A13')
        A21 = request.form.get('A21')
        A22 = request.form.get('A22')
        A23 = request.form.get('A23')
        A31 = request.form.get('A31')
        A32 = request.form.get('A32')
        A33 = request.form.get('A33')
        A4 = request.form.get('A4')
        A5 = request.form.get('A5')
        A6 = request.form.get('A6')
        A7 = request.form.get('A7')
        return render_template('connection_page.html', childID=childID)

@app.route('/raventest', methods=['GET', 'POST'])
def ravenTest():
    if request.method == 'POST':
        childID = int(request.form.get('childID'))
        questionID = int(request.form.get('questionID'))
        answer = request.form.get('answer')
        return render_template('raven_test.html', childID=childID, questionID=questionID+1, isLastQuestion=1 if questionID == NUMRAVENTEST - 1 else 0)

    else:
        return render_template('raven_test.html', childID=childID, questionID=1, isLastQuestion=1)

@app.route('/raventestresult', methods=['GET', 'POST'])
def ravenTestResult():
    if request.method == 'POST':
        print "raven test over"

        childID = int(request.form.get('childID'))
        questionID = int(request.form.get('questionID'))
        answer = request.form.get('answer')
        if NUMRAVENTEST != questionID:
            print "wrong num of raven questions!"


        return render_template('connection_page2.html', childID=childID)

@app.route('/memorytest', methods=['GET', 'POST'])
def memoryTest():
    if request.method == 'POST':
        childID = int(request.form.get('childID'))
        lenth = int(request.form.get('lenth'))
        answer = request.form.get('answer')
        return render_template('memory_test.html', childID=childID, lenth=lenth+1, isLastQuestion=1 if lenth == NUMMEMORYTEST - 1 else 0)

    else:
        return render_template('memory_test.html', childID=childID, lenth=1, isLastQuestion=1)

@app.route('/memorytestresult', methods=['GET', 'POST'])
def memoryTestResult():
    if request.method == 'POST':
        print "memory test over"

        childID = int(request.form.get('childID'))
        lenth = int(request.form.get('lenth'))
        answer = int(request.form.get('answer'))
        if NUMMEMORYTEST != lenth:
            print "wrong num of memory questions!"


        return render_template('connection_page3.html', childID=childID)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
