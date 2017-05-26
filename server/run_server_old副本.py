from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Question, Child
from flask import send_file
import time


app = Flask(__name__, static_folder='/vagrant/project/1')
engine = create_engine('sqlite:///language_data.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def currentTime():
    return str(time.time())

@app.route('/child/JSON')
def childJSON():
    children = session.query(Child).all()
    return jsonify(MenuItems=[child.serialize for child in children])


@app.route("/ip", methods=["GET"])
def get_my_ip():
    return jsonify(origin=request.headers.get('X-Forwarded-For', request.remote_addr)), 200


@app.route("/q", methods=["GET"])
def showQ():
    questions = session.query(Question).all()
    return jsonify(questions=[q.serialize for q in questions])

@app.route("/child", methods=["GET"])
def showChild():
    children = session.query(Child).all()
    return jsonify(children=[child.serialize for child in children])

@app.route('/', methods=['GET','POST'])
def showIndex():

    print 'ip: ', request.access_route

    return jsonify(childID=1, questionID=1, wordList=['a','b'], isLastQuestion=0)



@app.route('/begin', methods=['GET', 'POST'])
def begin():
    if request.method == 'POST':
        print "begin"
        basicInfo = request.get_json()
        newchild = Child()
        newchild.sex = basicInfo['sex']
        newchild.age = basicInfo['age']
        newchild.edu1 = basicInfo['edu1']
        newchild.edu2 = basicInfo['edu2']
        newchild.edu3 = basicInfo['edu3']
        newchild.edu4 = basicInfo['edu4']
        newchild.edu5 = basicInfo['edu5']
        newchild.edu6 = basicInfo['edu6']
        newchild.edu7 = basicInfo['edu7']
        newchild.t0 = currentTime()
        session.add(newchild)
        session.commit()
        print "create a new child, id = ", newchild.id
        question = session.query(Question).filter_by(id=1).one()
        wordList = [question.correct, question.wrong1, question.wrong2, question.wrong3]
        return jsonify(childID=newchild.id, questionID=1, wordList=wordList, isLastQuestion=0)

def updateWordTestResult(childID, questionID, answer):
    print childID, questionID, answer
    question = session.query(Question).filter_by(id=questionID).one()
    updateChild = session.query(Child).filter_by(id=childID).one()
    num_ans = updateChild.num_ans + 1
    if num_ans == 1:
        updateChild.ans1 = answer
        updateChild.q1 = questionID
        updateChild.t1 = currentTime()
    elif num_ans == 2:
        updateChild.ans2 = answer
        updateChild.q2 = questionID
        updateChild.t2 = currentTime()
    elif num_ans == 3:
        updateChild.ans3 = answer
        updateChild.q3 = questionID
        updateChild.t3 = currentTime()

    updateChild.num_ans = num_ans

    session.add(updateChild)
    session.commit()
    return num_ans

@app.route('/wordtest', methods=['GET', 'POST'])
def wordTest():
    if request.method == 'POST':
        print 'test result: '
        testResult = request.get_json()

        childID = int(testResult['childID'])
        questionID = int(testResult['questionID'])
        answer = testResult['answer']
        num_ans = updateWordTestResult(childID, questionID, answer)

        questionID = questionID+1
        question = session.query(Question).filter_by(id=questionID).one()
        wordList = [question.correct, question.wrong1, question.wrong2, question.wrong3]
        if num_ans == 2:
            return jsonify(childID=childID, questionID=questionID, wordList=wordList, isLastQuestion=1)
        else:
            return jsonify(childID=childID, questionID=questionID, wordList=wordList, isLastQuestion=0)

@app.route('/wordtestresult', methods=['GET', 'POST'])
def wordTestResult():
    if request.method == 'POST':
        print "word test over"
        testResult = request.get_json()

        childID = int(testResult['childID'])
        questionID = int(testResult['questionID'])
        answer = testResult['answer']
        if 3 != updateWordTestResult(childID, questionID, answer):
            print "wrong num of questions!"

        return jsonify(ageTest=666)




if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
