import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, Question, Child, WordTest, RavenTest, MemoryTest
import pandas as pd

engine = create_engine('sqlite:///language_data.db')

DBSession = sessionmaker(bind=engine)
session = DBSession()
def add():
    child = Child()
    child.age=2
    session.add(child)
    session.commit()

def showChildRen():
    children = session.query(Child).all()
    for child in children:
         print child.id, child.is_male, child.is_female, child.age, child.edu1, child.edu2, child.edu3, child.edu4, child.edu5, child.edu6, child.edu7, '\n'

def showQuestions():
    questions = session.query(Question).all()
    for question in questions:
        print question.id, question.level, question.correct, question.wrong1, question.wrong2, question.wrong3

def genCSV():

    data = pd.DataFrame()

    children = session.query(Child).all()
    for child in children:
        childID = child.id
        datai = {}

        datai['childID'] = childID
        datai['ip'] = child.ip
        datai['date_start'] = child.date_start
        datai['sex'] = child.sex
        datai['age'] = child.age
        datai['edu1'] = child.edu1
        datai['edu2'] = child.edu2
        datai['edu3'] = child.edu3
        datai['edu4'] = child.edu4
        datai['edu5'] = child.edu5
        datai['edu6'] = child.edu6
        datai['edu7'] = child.edu7
        datai['time_info'] = child.time_info
        datai['level'] = child.level
        datai['num_word_test'] = child.num_word_test

        datai['A11'] = child.A11
        datai['A12'] = child.A12
        datai['A13'] = child.A13
        datai['A21'] = child.A21
        datai['A22'] = child.A22
        datai['A23'] = child.A23
        datai['A31'] = child.A31
        datai['A32'] = child.A32
        datai['A33'] = child.A33
        datai['A4'] = child.A4
        datai['A5'] = child.A5
        datai['A6'] = child.A6
        datai['A7'] = child.A7
        datai['time_survey'] = child.time_survey
        datai['memory'] = child.memory

        word_records = session.query(WordTest).filter_by(childID=childID).all()
        for i, word_record in zip(range(1, 21), word_records):
            #print word_record.questionID
            datai['word_qID'+str(i)] = word_record.questionID
            datai['word_ans'+str(i)] = word_record.answer
            datai['word_time'+str(i)] = word_record.time
            datai['word_date'+str(i)] = word_record.date
            question = session.query(Question).filter_by(id=word_record.questionID).one()
            datai['word_correct'+str(i)] = question.correct
            datai['word_level'+str(i)] = question.level

        raven_records = session.query(RavenTest).filter_by(childID=childID).all()
        for raven_record in raven_records:
            datai['raven_ans'+str(raven_record.questionID)] = raven_record.answer
            datai['raven_time'+str(raven_record.questionID)] = raven_record.time
            datai['raven_date'+str(raven_record.questionID)] = raven_record.date

        memory_records = session.query(MemoryTest).filter_by(childID=childID).all()
        for memory_record in  memory_records:
            datai['memory_ans'+str(memory_record.questionID)] = memory_record.answer
            datai['memory_time'+str(memory_record.questionID)] = memory_record.time
            datai['memory_date'+str(memory_record.questionID)] = memory_record.date

        datai = pd.DataFrame(datai, index=[childID])
        data = pd.concat([data, datai])
    #print data.columns
    columns = ['childID', 'ip', 'date_start', 'sex', 'age',
    'edu1', 'edu2', 'edu3', 'edu4', 'edu5', 'edu6', 'edu7', 'time_info',
    'level', 'num_word_test']

    for i in range(1, 21):
        columns = columns + ['word_qID'+str(i), 'word_level'+str(i),
        'word_correct'+str(i), 'word_ans'+str(i),
        'word_time'+str(i), 'word_date'+str(i)]
    columns = columns + ['A11', 'A12', 'A13', 'A21', 'A22', 'A23',
    'A31', 'A32', 'A33', 'A4', 'A5', 'A6', 'A7', 'time_survey']

    for i in range(1, 9):
        columns = columns + ['raven_ans'+str(i), 'raven_time'+str(i), 'raven_date'+str(i)]

    for i in range(1, 35):
        columns = columns + ['memory_ans'+str(i), 'memory_time'+str(i), 'memory_date'+str(i)]

    data.to_csv("languageData.csv", columns=columns)
#showQuestions()
#showChildRen()

genCSV()