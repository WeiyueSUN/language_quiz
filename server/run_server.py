#! usr/bin/python
# coding=utf-8

from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Question, Child, WordTest, RavenTest, MemoryTest
import time
import random

app = Flask(__name__)

engine = create_engine('sqlite:///language_data.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

NUMWORDTEST = 20
NUMRAVENTEST = 8
MINLEVEL = 1
MAXLEVEL = 6
# 固定词在每个级别的词数量，需依次排在csv文件前面
FIX_NUM = {
    1: 2,
    2: 2,
    3: 2,
    4: 4,
    5: 4,
    6: 4
}
FIX_QUESTIONS = {
    1: [1, 2],
    2: [3, 4],
    3: [5, 6],
    4: [7, 8, 9, 10],
    5: [11, 12, 13, 14],
    6: [15, 16, 17, 18]
}
QUESTIONID_MARK = {
    1: 1,
    2: 3,
    3: 5,
    4: 7,
    5: 11,
    6: 15
}

NUMMEMORYTEST = 20
# lenth = i, 2i-1, 2i
MEMORY_QUESTION = {
    1: '1',
    2: '9',
    3: '12',
    4: '21',
    5: '123',
    6: '321',
    7: '1234',
    8: '4321',
    9: '12345',
    10: '54321',
    11: '123456',
    12: '654321',
    13: '1234567',
    14: '7654321',
    15: '12345678',
    16: '87654321',
    17: '123456789',
    18: '987654321',
    19: '1234567890',
    20: '0987654321'
}
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
def child():
    children = session.query(Child).all()
    return jsonify(children=[child.serialize for child in children])


'''
以下为实际用到的路由
'''


# 首页
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# 填写孩子信息页
@app.route('/info_kid', methods=['GET'])
def info_kid():
    return render_template('info_kid.html')


# 由一个单词的使用次数对应轮盘赌的权值
def func_weight(times_used):
    if times_used == 0:
        return 4
    elif times_used == 1:
        return 8
    elif times_used == 2:
        return 16
    elif times_used >= 3:
        return 1
    else:
        print 'wrong times_used', times_used
        return 0


# 轮盘赌算法
# x list of number
# wi: the weight to choose xi
def func_roulette(x, w):
    lenth = len(x)
    array = []
    for i in range(lenth):
        for j in range(int(w[i])):
            array = array + [x[i]]
    return array[random.randint(0, len(array) - 1)]


def newWordTestQuestionID(childID):
    # 数据库查这个孩子
    child = session.query(Child).filter_by(id=childID).one()

    # 数据库查该孩子的答题记录
    records = session.query(WordTest).filter_by(childID=childID)

    # 更新这个孩子的下题的level
    if child.last + child.llast == 2:
        # 升级
        child.level = min(child.level + 1, MAXLEVEL)

        # 清空最近题目的缓存
        child.last = 0
        child.llast = 0

    elif child.last + child.llast == -2:
        # 降级
        child.level = max(child.level - 1, MINLEVEL)

        # 清空最近题目的缓存
        child.last = 0
        child.llast = 0

    # 累加一下该孩子的各题答题总数
    num_ans = 0

    # 找出目标级别答过的题
    questionIDs_answered_this_level = []
    for record in records:
        num_ans = num_ans + 1
        question = session.query(Question).filter_by(id=record.questionID).one()
        if question.level == child.level:
            questionIDs_answered_this_level = questionIDs_answered_this_level + [question.id]

    # 该级别已经回答过的题目数量
    num_answered_this_level = len(questionIDs_answered_this_level)

    if num_answered_this_level < FIX_NUM[child.level]:
        # 答固定题
        questionID = FIX_QUESTIONS[child.level][num_answered_this_level]
    else:
        # 轮盘赌抽题

        # 该级别所有题
        questionIDs = []
        questions = session.query(Question).filter_by(level=child.level)
        for question in questions:
            questionIDs = questionIDs + [question.id]

        # 备选题，做集合减
        questionIDs_to_answer = list(set(questionIDs) - set(questionIDs_answered_this_level))

        # 查一下这些题的权重
        weights = []
        for questionID in questionIDs_to_answer:
            # 效率有点低
            question = session.query(Question).filter_by(id=questionID).one()
            times_used = question.times_used
            weights = weights + [func_weight(times_used)]

        # 轮盘赌
        questionID = func_roulette(questionIDs_to_answer, weights)

    # child更新了level
    session.add(child)
    session.commit()
    return questionID, num_ans


# 提交信息，返回单词测试说明页，为远端分配childID
@app.route('/info_kid_submit', methods=['POST', 'GET'])
def kid_info_submit():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        newchild = Child()
        newchild.date_start = str(time.time())
        newchild.ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        newchild.sex = request.form.get('sex')
        newchild.age = request.form.get('age')
        newchild.edu1 = request.form.get('edu1')
        newchild.edu2 = request.form.get('edu2')
        newchild.edu3 = request.form.get('edu3')
        newchild.edu4 = request.form.get('edu4')
        newchild.edu5 = request.form.get('edu5')
        newchild.edu6 = request.form.get('edu6')
        newchild.edu7 = request.form.get('edu7')
        newchild.time_info = request.form.get('time')
        # 记录孩子信息

        session.add(newchild)
        session.commit()
        # 数据入库
        print "create a new child, id = ", newchild.id

        return render_template('selection_before.html',
                               childID=newchild.id)


# 返回单词测试练习页
@app.route('/sel_practice', methods=['POST', 'GET'])
def sel_practice():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        return render_template('selection_practice.html')


# 返回单词测试
@app.route('/sel_begin', methods=['POST', 'GET'])
def sel_begin():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        childID = request.form.get('childID')
        questionID, num_ans = newWordTestQuestionID(childID)
        if num_ans != 0:
            print 'wrong num_ans'
        question = session.query(Question).filter_by(id=questionID).one()

        # 挑选问题

        return render_template('selection_test.html',
                               questionID=questionID,
                               correct=question.correct,
                               word0=question.correct,
                               word1=question.wrong1,
                               word2=question.wrong2,
                               word3=question.wrong3,
                               isLastQuestion=0)  # 添加任一种类型的一道题目的答案到数据库


def addTestResult(testClass, childID, questionID, answer, time_on_this):
    record = testClass()
    record.childID = childID
    record.questionID = questionID
    record.answer = answer
    record.time = time_on_this
    record.date = str(time.time())
    session.add(record)
    session.commit()


# 提交单词测试的一个题目
@app.route('/sel_test', methods=['POST', 'GET'])
def sel_test():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        childID = int(request.form.get('childID'))
        questionID = int(request.form.get('questionID'))
        answer = request.form.get('answer')
        time = request.form.get('time')
        # 获取答题信息

        # 记录答题信息
        child = session.query(Child).filter_by(id=childID).one()
        child.num_word_test = child.num_word_test + 1
        num_ans = child.num_word_test
        addTestResult(WordTest, childID, questionID, answer, time)

        # 更新question计数， 更新child的答题缓存
        question = session.query(Question).filter_by(id=questionID).one()
        question.times_used = question.times_used + 1
        child.llast = child.last
        child.last = 1 if answer == question.correct else -1
        session.add(child)
        session.add(question)
        session.commit()
        print 'wordtest: childID:{}, questionID:{}, level:{}, correct:{}, answer:{}, time:{}, num_ans:{}'.format(
            childID,
            questionID,
            question.level,
            question.correct,
            answer,
            time,
            num_ans)

        # 分配下一个question
        questionID, num_ans_examine = newWordTestQuestionID(childID)
        if num_ans != num_ans_examine:
            print 'wrong num_ans'
        question = session.query(Question).filter_by(id=questionID).one()
        # 挑选新的题目

        return render_template('selection_test.html',
                               questionID=questionID,
                               correct=question.correct,
                               word0=question.correct,
                               word1=question.wrong1,
                               word2=question.wrong2,
                               word3=question.wrong3,
                               isLastQuestion=1 if num_ans == NUMWORDTEST - 1 else 0)


# 根据info信息计算预测的英语折合年龄，需保证childID已在数据库
def predAgeWordTest(childID):
    # 待填写...
    val = 15
    assert (-1 < val < 31)
    return val


# 返回单词测试结果
@app.route('/sel_result', methods=['POST', 'GET'])
def sel_result():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        print "word test over"

        childID = int(request.form.get('childID'))
        questionID = int(request.form.get('questionID'))
        answer = request.form.get('answer')
        time = request.form.get('time')

        child = session.query(Child).filter_by(id=childID).one()
        child.num_word_test = child.num_word_test + 1
        num_ans = child.num_word_test
        if num_ans != NUMWORDTEST:
            print 'wrong num word test'
        session.add(child)

        addTestResult(WordTest, childID, questionID, answer, time)

        # 更新question计数
        question = session.query(Question).filter_by(id=questionID).one()
        question.times_used = question.times_used + 1
        session.add(question)
        session.commit()
        print 'wordtest: childID:{}, questionID:{}, level:{}, correct:{}, answer:{}, num_ans:{}'.format(childID,
                                                                                                        questionID,
                                                                                                        question.level,
                                                                                                        question.correct,
                                                                                                        answer, num_ans)
        pred_age = predAgeWordTest(childID)
        return render_template('selection_result.html', pred_age=pred_age)


# 返回家长填写信息页
@app.route('/info_parent', methods=['POST', 'GET'])
def info_parent():
    if request.method == 'POST':
        return render_template('info_parent.html')
    elif request.method == 'GET':
        return render_template('index.html')


# 处理家长填写信息，并返回瑞文推理引导语页
@app.route('/info_parent_submit', methods=['POST', 'GET'])
def info_parent_submit():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        childID = request.form.get('childID')

        child = session.query(Child).filter_by(id=childID).one()

        child.A11 = request.form.get('A11')
        child.A12 = request.form.get('A12')
        child.A13 = request.form.get('A13')
        child.A21 = request.form.get('A21')
        child.A22 = request.form.get('A22')
        child.A23 = request.form.get('A23')
        child.A31 = request.form.get('A31')
        child.A32 = request.form.get('A32')
        child.A33 = request.form.get('A33')
        child.A4 = request.form.get('A4')
        child.A5 = request.form.get('A5')
        child.A6 = request.form.get('A6')
        child.A7 = request.form.get('A7')
        child.time_survey = request.form.get('time')

        session.add(child)
        session.commit()

        return render_template('raven_before.html')


# 返回瑞文推理练习题
@app.route('/raven_practice', methods=['POST', 'GET'])
def raven_practice():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        return render_template('raven_practice.html')


# 开始执行瑞文测试
@app.route('/raven_begin', methods=['POST', 'GET'])
def raven_begin():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        return render_template('raven_test.html',
                               ques_letter='A1',
                               questionID=1,
                               isLastQuestion=0)


# 瑞文测试
@app.route('/raven_test', methods=['POST', 'GET'])
def raven_test():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        childID = int(request.form.get('childID'))
        questionID = int(request.form.get('questionID'))
        answer = request.form.get('answer')
        time = request.form.get('time')

        addTestResult(RavenTest, childID, questionID, answer, time)

        letter = ''
        next_ques = questionID + 1
        if next_ques == 2:
            letter = 'A5'
        elif next_ques == 3:
            letter = 'A6'
        elif next_ques == 4:
            letter = 'A7'
        elif next_ques == 5:
            letter = 'A11'
        elif next_ques == 6:
            letter = 'A12'
        elif next_ques == 7:
            letter = 'B5'
        elif next_ques == 8:
            letter = 'B12'

        return render_template('raven_test.html',
                               ques_letter=letter,
                               questionID=questionID + 1,
                               isLastQuestion=1 if questionID == NUMRAVENTEST - 1 else 0)


# 瑞文测试结果
@app.route('/raven_result', methods=['POST', 'GET'])
def raven_result():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        print "raven test over"

        childID = int(request.form.get('childID'))
        questionID = int(request.form.get('questionID'))
        answer = request.form.get('answer')
        time = request.form.get('time')

        addTestResult(RavenTest, childID, questionID, answer, time)

        if NUMRAVENTEST != questionID:
            print "wrong num of raven questions!"

        # 如何计算瑞文推理题目的正确率...待填写 填充到correct_ratio变量中，
        # 如0.56代表56%
        correct_ratio = 0.56

        return render_template('raven_result.html', ratio=correct_ratio * 100)


# 记忆测试前的说明
@app.route('/memory_before', methods=['GET', 'POST'])
def memory_before():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        return render_template('memory_before.html')


# 记忆测试练习题
@app.route('/memory_practice', methods=['GET', 'POST'])
def memory_practice():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        return render_template('memory_practice.html')


# 开始进行记忆测试
@app.route('/memory_begin', methods=['GET', 'POST'])
def memory_begin():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        return render_template('memory_test.html', length=3)


"""
@app.route('/memory_test', methods=['POST', 'GET'])
def memory_test():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        childID = int(request.form.get('childID'))
        questionID = int(request.form.get('length'))
        answer = request.form.get('answer')
        time_on_this = request.form.get('time')

        addTestResult(MemoryTest, childID, questionID, answer, time_on_this)
        correct = MEMORY_QUESTION[questionID]
        if correct == answer:
            print childID, questionID, 'correct!'
            questionID = ((questionID + 1) / 2 + 1) * 2 - 1
        else:
            print childID, questionID, correct, answer
            if questionID % 2 != 0:
                questionID = questionID + 1
            else:
                child = session.query(Child).filter_by(id=childID).one()
                child.memory = (questionID + 1) / 2
                child.date_end = str(time.time())
                session.add(child)
                session.commit()
                return render_template('memory_result.html')

        if questionID > NUMMEMORYTEST:
            child = session.query(Child).filter_by(id=childID).one()
            child.memory = (questionID + 1) / 2
            child.date_end = str(time.time())
            session.add(child)
            session.commit()
            return render_template('memory_result.html')
        else:
            return render_template('memory_test.html', questionID=questionID)
"""


# 记忆测试
@app.route('/memory_test', methods=['POST', 'GET'])
def memory_test():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        childID = int(request.form.get('childID'))
        length = int(request.form.get('length'))
        is_correct = int(request.form.get('correct'))
        time_on_this = request.form.get('time')

        # 更新数据...
        # 说明：随机生成数字序列和判断正误都在前端进行
        # （后来考虑到刷新会使得播放次数可以重复，因此每次生成的数字序列都要求不同）
        # 返回childID，当前题目的length，回答是否正确is_correct以及答题时间
        # 根据这些数据后端在数据库做相应记录，并且更新数据，决定返回什么样的结果回来

        if (is_correct):
            if (length == 16):
                return render_template('memory_result.html', length=16)
            else:
                return render_template('memory_test.html', length=length + 1)
        else:
            return render_template('memory_result.html', length=length - 1)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
