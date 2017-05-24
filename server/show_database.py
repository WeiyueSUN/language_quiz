import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Question, Child

engine = create_engine('sqlite:///languageData.db')

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
        print question.id, question.correct, question.wrong1, question.wrong2, question.wrong3

showQuestions()
showChildRen()