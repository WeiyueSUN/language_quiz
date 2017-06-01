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
NUMRAVENTEST = 8
NUMMEMORYTEST = 5

'''
以下为自定义路由
'''


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


'''
以下为实际用到的路由
'''


# ①首页
@app.route('/', methods=['GET'])
def showIndex():
    return render_template('index.html')


# ②填写信息页
@app.route('/info', methods=['GET'])
def showInfo():
    return render_template('info.html')


# ③提交信息，返回单词测试页，为远端分配childID
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


# ④提交单词测试的一个题目
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


# 数据更新
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

    print 'word test: childID:{}, questionID:{}, answer:{}, correct:{}, num_ans:{}'.format(childID, questionID, answer,
                                                                                           question.correct, num_ans)

    return num_ans


# ⑤返回单词测试结果
@app.route('/wordtestresult', methods=['POST'])
def wordTestResult():
    print "word test over"

    childID = int(request.form.get('childID'))
    questionID = int(request.form.get('questionID'))
    answer = request.form.get('answer')

    if NUMWORDTEST != updateWordTestResult(childID, questionID, answer):
        print "wrong num of questions!"

    # 在这里加入计算分数的代码，并将其写入变量pred_age

    pred_age = 15
    return render_template('selection_result.html', pred_age=pred_age, childID=childID)


# ⑥返回家长填写信息页
@app.route('/parent', methods=['GET'])
def parent():
    return render_template('parent.html')


# ⑦处理家长填写信息，并返回瑞文推理引导语页
@app.route('/survey', methods=['POST'])
def surveySumbit():
    childID = request.form.get('childID')
    Q11 = request.form.get('Q11')
    Q12 = request.form.get('Q12')
    Q13 = request.form.get('Q13')
    Q21 = request.form.get('Q21')
    Q22 = request.form.get('Q22')
    Q23 = request.form.get('Q23')
    Q31 = request.form.get('Q31')
    Q32 = request.form.get('Q32')
    Q33 = request.form.get('Q33')
    Q4 = request.form.get('Q4')
    Q5 = request.form.get('Q5')
    Q6 = request.form.get('Q6')
    Q7 = request.form.get('Q7')

    # 在这里执行数据入库操作...

    return render_template('raven_before.html', childID=childID)


# ⑧开始执行瑞文测试
@app.route('/ravenbegin', methods=['POST'])
def ravenBegin():
    childID = int(request.form.get('childID'))
    return render_template('raven_test.html', childID=childID, questionID=1,
                           isLastQuestion=0)


# ⑨瑞文测试
@app.route('/raventest', methods=['POST'])
def ravenTest():
    childID = int(request.form.get('childID'))
    questionID = int(request.form.get('questionID'))
    answer = request.form.get('answer')

    # 在这里执行数据入库操作...

    return render_template('raven_test.html', childID=childID, questionID=questionID + 1,
                           isLastQuestion=1 if questionID == NUMRAVENTEST - 1 else 0)


# ⑩瑞文测试结果
@app.route('/raventestresult', methods=['POST'])
def ravenTestResult():
    print "raven test over"

    childID = int(request.form.get('childID'))
    questionID = int(request.form.get('questionID'))
    answer = request.form.get('answer')

    # 在这里执行数据入库操作...

    if NUMRAVENTEST != questionID:
        print "wrong num of raven questions!"

    # 在这里计算瑞文推理测试结果...

    return render_template('raven_result.html', childID=childID)


# ⑪开始进行记忆测试
@app.route('/memorybegin', methods=['GET'])
def memoryBegin():
    return render_template('audio.html', length=1,
                           isLastQuestion=0)

# 开始处理记忆测试
@app.route('/memorytest', methods=['POST'])
def memoryTest():
    childID = int(request.form.get('childID'))
    length = int(request.form.get('length'))
    answer = request.form.get('answer')
    return render_template('audio.html', childID=childID, length=length + 1,
                           isLastQuestion=1 if length == NUMMEMORYTEST - 1 else 0)


# ⑫给出记忆测试结果
@app.route('/memorytestresult', methods=['GET', 'POST'])
def memoryTestResult():
    if request.method == 'POST':
        print "memory test over"

        childID = int(request.form.get('childID'))
        length = int(request.form.get('length'))
        answer = int(request.form.get('answer'))
        if NUMMEMORYTEST != length:
            print "wrong num of memory questions!"

        return render_template('connection_page3.html', childID=childID)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
