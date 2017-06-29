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
# 固定词在每个级别的词数量
FIX_NUM = 4
RAVEN_ANS = [-1, 4, 6, 3, 6, 4, 5, 1, 5]
RAVEN_LETTER = ['', 'A1', 'A5', 'A6', 'A7', 'A11', 'A12', 'B5', 'B12']
MINMEMORY = 3
MAXMEMORY = 16

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
    if len(x) != len(w) or len(x) <= 0:
        print 'wrong roulette x'
        return -1

    length = len(x)
    array = []
    for i in range(length):
        for j in range(int(w[i])):
            array = array + [x[i]]
    return array[random.randint(0, len(array) - 1)]


def newWordTestQuestionID(childID):
    # 数据库查这个孩子
    child = session.query(Child).filter_by(id=childID).one()

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

    session.add(child)
    session.commit()
    ### 此后只访问，不更新数据库 ###

    # 数据库查该孩子的答题记录
    records = session.query(WordTest).filter_by(childID=childID)

    # 累加该孩子的各题答题总数
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

    # 先调出不考虑是否作答的所有题目
    if num_answered_this_level < FIX_NUM:
        # 同级别题中固定题

        if num_answered_this_level == 1:
            # 刚回答过一个时，下一个要给出group不同的
            questions = session.query(Question).filter_by(level=child.level, fix=1, group=1 - child.lgroup)
        else:
            # 除此之外无需考虑group的问题
            questions = session.query(Question).filter_by(level=child.level, fix=1)
    else:
        # 所有同级别题
        questions = session.query(Question).filter_by(level=child.level)

    # 转换成题号
    questionIDs = []
    for question in questions:
        questionIDs = questionIDs + [question.id]

    # 可行题，做集合减，除去已经答的
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

    return questionID, num_ans


# 提交信息，返回单词测试说明页，为远端分配childID
@app.route('/info_kid_submit', methods=['POST', 'GET'])
def kid_info_submit():
    if request.method == 'GET':
        newchild = Child()
        newchild.date_start = str(time.time())
        newchild.ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        newchild.sex = request.args.get('sex')
        newchild.age = request.args.get('age')
        newchild.edu1 = request.args.get('edu1')
        newchild.edu2 = request.args.get('edu2')
        newchild.edu3 = request.args.get('edu3')
        newchild.edu4 = request.args.get('edu4')
        newchild.edu5 = request.args.get('edu5')
        newchild.edu6 = request.args.get('edu6')
        newchild.edu7 = request.args.get('edu7')
        newchild.time_info = request.args.get('time')
        # 记录孩子信息
        if (newchild.sex == None or newchild.age == None):
            return render_template('index.html')

        session.add(newchild)
        session.commit()
        # 数据入库
        print "create a new child, id = ", newchild.id, newchild.age

        return render_template('selection_before.html',
                               childID=newchild.id)


# 返回单词测试练习页
@app.route('/sel_practice', methods=['POST', 'GET'])
def sel_practice():
    if request.method == 'GET':
        childID = request.args.get('childID')
        if (childID == None):
            return render_template('index.html')
        return render_template('selection_practice.html')


# 返回单词测试
@app.route('/sel_begin', methods=['POST', 'GET'])
def sel_begin():
    if request.method == 'GET':
        if (request.args.get('childID') == None):
            return render_template('index.html')
        childID = int(request.args.get('childID'))
        print 'childID: ', childID
        # 挑选问题
        questionID, num_ans = newWordTestQuestionID(childID)
        if num_ans != 0:
            print 'wrong num_ans'
        question = session.query(Question).filter_by(id=questionID).one()

        return render_template('selection_test.html',
                               questionID=questionID,
                               correct=question.correct,
                               word0=question.correct,
                               word1=question.wrong1,
                               word2=question.wrong2,
                               word3=question.wrong3,
                               isLastQuestion=0)


# 添加任一种类型的一道题目的答案到数据库
def addTestResult(testClass, childID, questionID, answer, time_this):
    records = session.query(testClass).filter_by(childID=childID, questionID=questionID)
    n = 0
    for record in records:
        n = n + 1
    if n == 0:
        record = testClass()
        record.childID = childID
        record.questionID = questionID
        record.answer = answer
        record.time = time_this
        record.date = str(time.time())
        session.add(record)
        session.commit()
        print 'new record'
        return 1
    else:
        print 'record existed'
        return 0


# 提交单词测试的一个题目
@app.route('/sel_test', methods=['POST', 'GET'])
def sel_test():
    if request.method == 'GET':
        # 获取答题信息

        if (request.args.get('childID') == None or request.args.get('questionID') == None):
            return render_template('index.html')
        childID = int(request.args.get('childID'))
        questionID = int(request.args.get('questionID'))
        answer = request.args.get('answer')
        time = request.args.get('time')

        child = session.query(Child).filter_by(id=childID).one()
        question = session.query(Question).filter_by(id=questionID).one()
        # 添加答题记录

        if addTestResult(WordTest, childID, questionID, answer, time) == 1:
            # 如果合法
            # 更新该child已回答的数量， 近两次回答是否正确
            # last是上次，llast是上上次，1是正确，-1是错误
            child.num_word_test = child.num_word_test + 1
            child.llast = child.last
            child.last = 1 if answer == question.correct else -1
            child.lgroup = question.group

            # 更新question计数， 更新child的答题缓存
            question.times_used = question.times_used + 1

            print 'wordtest: childID:{}, questionID:{}, level:{}, correct:{}, answer:{}, time:{}, num_ans:{}'.format(
                childID,
                questionID,
                question.level,
                question.correct,
                answer,
                time,
                child.num_word_test)
            session.add(child)
            session.add(question)
            session.commit()

        ### 至此已完成提交的题目的维护，开始分配下一道题 ###

        # 分配下一个questionID，通过和答题记录对比验证答题数量
        questionID, num_ans_examine = newWordTestQuestionID(childID)
        if child.num_word_test != num_ans_examine:
            print 'wrong num_ans'
        question = session.query(Question).filter_by(id=questionID).one()

        return render_template('selection_test.html',
                               questionID=questionID,
                               correct=question.correct,
                               word0=question.correct,
                               word1=question.wrong1,
                               word2=question.wrong2,
                               word3=question.wrong3,
                               isLastQuestion=1 if child.num_word_test >= NUMWORDTEST - 1 else 0)


# 根据info信息计算预测的英语折合年龄，需保证childID已在数据库
def predAgeWordTest(childID):
    # 待填写...
    records = session.query(WordTest).filter_by(childID=childID)
    age = 0
    num_ans = 0
    num_correct = 0
    for record in records:
        questionID = record.questionID
        question = session.query(Question).filter_by(id=questionID).one()
        # 如果答对了
        if question.correct == record.answer:
            age = max(age, question.age)
            num_correct = num_correct + 1

        num_ans = num_ans + 1

    if num_ans != NUMWORDTEST:
        print 'wrong num_ans in func predAge'

    print "id={}, num_correct={}, pred_age={}".format(childID, num_correct, age)

    return age


# 返回单词测试结果
@app.route('/sel_result', methods=['POST', 'GET'])
def sel_result():
    if request.method == 'GET':
        print "word test over"
        # 获取信息

        if (request.args.get('childID') == None or request.args.get('questionID') == None):
            return render_template('index.html')

        childID = int(request.args.get('childID'))
        questionID = int(request.args.get('questionID'))
        answer = request.args.get('answer')
        time = request.args.get('time')

        child = session.query(Child).filter_by(id=childID).one()
        question = session.query(Question).filter_by(id=questionID).one()

        # 记录
        if addTestResult(WordTest, childID, questionID, answer, time) == 1:
            # 如果合法
            # 更新child答题数量
            child.num_word_test = child.num_word_test + 1
            num_ans = child.num_word_test

            # 更新question计数
            question.times_used = question.times_used + 1

            print 'wordtest: childID:{}, questionID:{}, level:{}, correct:{}, answer:{}, num_ans:{}'.format(
                childID, questionID, question.level, question.correct, answer, num_ans)

            # 结束标志
            if num_ans != NUMWORDTEST:
                print 'wrong num total word test'

            # 预测
            child.pred_age = predAgeWordTest(childID)

            session.add(child)
            session.add(question)
            session.commit()

        return render_template('selection_result.html', pred_age=child.pred_age)


# 返回家长填写信息页
@app.route('/info_parent', methods=['POST', 'GET'])
def info_parent():
    if request.method == 'GET':
        childID = request.args.get('childID')
        if (childID == None):
            return render_template('index.html')
        return render_template('info_parent.html')


# 处理家长填写信息，并返回瑞文推理引导语页
@app.route('/info_parent_submit', methods=['POST', 'GET'])
def info_parent_submit():
    if request.method == 'GET':
        if (request.args.get('childID') == None):
            return render_template('index.html')
        childID = int(request.args.get('childID'))

        child = session.query(Child).filter_by(id=childID).one()

        child.A11 = request.args.get('A11')
        child.A12 = request.args.get('A12')
        child.A13 = request.args.get('A13')
        child.A21 = request.args.get('A21')
        child.A22 = request.args.get('A22')
        child.A23 = request.args.get('A23')
        child.A31 = request.args.get('A31')
        child.A32 = request.args.get('A32')
        child.A33 = request.args.get('A33')
        child.A4 = request.args.get('A4')
        child.A5 = request.args.get('A5')
        child.A6 = request.args.get('A6')
        child.A7 = request.args.get('A7')
        child.time_survey = request.args.get('time')

        if (child.A11 == None):
            return render_template('index.html')
        session.add(child)
        session.commit()

        return render_template('raven_before.html')


# 返回瑞文推理练习题
@app.route('/raven_practice', methods=['POST', 'GET'])
def raven_practice():
    if request.method == 'GET':
        childID = request.args.get('childID')
        if (childID == None):
            return render_template('index.html')
        return render_template('raven_practice.html')


# 开始执行瑞文测试
@app.route('/raven_begin', methods=['POST', 'GET'])
def raven_begin():
    if request.method == 'GET':
        childID = request.args.get('childID')
        if (childID == None):
            return render_template('index.html')
        return render_template('raven_test.html',
                               ques_letter='A1',
                               questionID=1,
                               isLastQuestion=0)


# 瑞文测试
@app.route('/raven_test', methods=['POST', 'GET'])
def raven_test():
    if request.method == 'GET':
        if (request.args.get('childID') == None or request.args.get('questionID') == None):
            return render_template('index.html')
        childID = int(request.args.get('childID'))
        questionID = int(request.args.get('questionID'))
        answer = request.args.get('answer')
        time = request.args.get('time')

        child = session.query(Child).filter_by(id=childID).one()

        if addTestResult(RavenTest, childID, questionID, answer, time) == 1:
            child.num_ans_raven = child.num_ans_raven + 1

        return render_template('raven_test.html',
                               ques_letter=RAVEN_LETTER[child.num_ans_raven + 1],
                               questionID=child.num_ans_raven + 1,
                               isLastQuestion=1 if child.num_ans_raven >= NUMRAVENTEST - 1 else 0)


# 瑞文测试结果
@app.route('/raven_result', methods=['POST', 'GET'])
def raven_result():
    if request.method == 'GET':
        print "raven test over"
        # 获取记录
        if (request.args.get('childID') == None or request.args.get('questionID') == None):
            return render_template('index.html')
        childID = int(request.args.get('childID'))
        questionID = int(request.args.get('questionID'))
        answer = request.args.get('answer')
        time = request.args.get('time')

        # 添加记录到数据库
        if addTestResult(RavenTest, childID, questionID, answer, time) == 1:
            pass

        if NUMRAVENTEST != questionID:
            print "wrong num of raven questions!"

        # 计算正确率
        records = session.query(RavenTest).filter_by(childID=childID)
        num_correct = 0
        num_ans = 0
        for record in records:
            print record.answer
            if int(record.answer) == RAVEN_ANS[record.questionID]:
                num_correct = num_correct + 1
            num_ans = num_ans + 1

        if num_ans != NUMRAVENTEST:
            print 'wrong num_ans in raven result'

        print num_correct
        correct_ratio = float(int(num_correct * 1000 / NUMRAVENTEST)) / 10.0

        return render_template('raven_result.html', ratio=correct_ratio)


# 记忆测试前的说明
@app.route('/memory_before', methods=['GET', 'POST'])
def memory_before():
    if request.method == 'GET':
        childID = request.args.get('childID')
        if (childID == None):
            return render_template('index.html')
        return render_template('memory_before.html')


# 记忆测试练习题
@app.route('/memory_practice', methods=['GET', 'POST'])
def memory_practice():
    if request.method == 'GET':
        childID = request.args.get('childID')
        if (childID == None):
            return render_template('index.html')
        return render_template('memory_practice.html')


# 开始进行记忆测试
@app.route('/memory_begin', methods=['GET', 'POST'])
def memory_begin():
    if request.method == 'GET':
        childID = request.args.get('childID')
        if (childID == None):
            return render_template('index.html')
        return render_template('memory_test.html', length=MINMEMORY)


# 记忆测试
@app.route('/memory_test', methods=['POST', 'GET'])
def memory_test():
    if request.method == 'GET':
        # 获取记录

        if (request.args.get('childID') == None or request.args.get('length') == None):
            return render_template('index.html')
        childID = int(request.args.get('childID'))
        length = int(request.args.get('length'))
        is_correct = int(request.args.get('correct'))
        time = request.args.get('time')

        child = session.query(Child).filter_by(id=childID).one()

        records = session.query(MemoryTest).filter_by(childID=childID, questionID=length * 2)
        n = 0
        for record in records:
            n = n + 1

        if n == 0 and child.memory == length:
            addTestResult(MemoryTest, childID, length * 2, is_correct, time)
        else:
            records = session.query(MemoryTest).filter_by(childID=childID, questionID=length * 2 + 1)
            n = 0
            for record in records:
                n = n + 1
            if n == 0 and child.memory == length:
                addTestResult(MemoryTest, childID, length * 2 + 1, is_correct, time)
            else:
                return render_template('memory_test.html', length=child.memory)

        # 更新数据...
        # 说明：随机生成数字序列和判断正误都在前端进行
        # （后来考虑到刷新会使得播放次数可以重复，因此每次生成的数字序列都要求不同）
        # 返回childID，当前题目的length，回答是否正确is_correct以及答题时间
        # 根据这些数据后端在数据库做相应记录，并且更新数据，决定返回什么样的结果回来



        is_finish = 0
        if is_correct == 1:
            # 做对了
            child.memory = length + 1
            # 升级了，机会恢复为1
            child.chance = 1
            if child.memory > MAXMEMORY:
                # 超上限了
                is_finish = 1
        else:
            # 做错了
            child.memory = length
            # 机会--
            child.chance = child.chance - 1
            if child.chance < 0:
                # 没机会了
                is_finish = 1

        session.add(child)
        session.commit()
        if is_finish == 1:
            child = session.query(Child).filter_by(id=childID).one()
            return render_template('memory_result.html', length=child.memory)
        else:
            return render_template('memory_test.html', length=child.memory)


if __name__ == '__main__':
    app.debug = True
    while(1):
        try:
            app.run(host='0.0.0.0', port=8000, threaded=True)
        except:
            continue
