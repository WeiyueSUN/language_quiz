import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()

class Question(Base):
    __tablename__ = 'word'

    id = Column(Integer, primary_key=True)
    correct = Column(String(15), nullable=False)
    wrong1 = Column(String(15), nullable=False)
    wrong2 = Column(String(15), nullable=False)
    wrong3 = Column(String(15), nullable=False)
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'correct': self.correct,
            'wrong1': self.wrong1,
            'wrong2': self.wrong2,
            'wrong3': self.wrong3
        }

class Child(Base):
    __tablename__ = 'child'

    id = Column(Integer, primary_key=True)
    url = Column(String(20))
    sex = Column(String(2))
    age = Column(String(5))
    edu1 = Column(Integer)
    edu2 = Column(Integer)
    edu3 = Column(Integer)
    edu4 = Column(Integer)
    edu5 = Column(Integer)
    edu6 = Column(Integer)
    edu7 = Column(Integer)


    num_ans = Column(Integer)
    q1 = Column(Integer)
    ans1 = Column(Integer)
    q2 = Column(Integer)
    ans2 = Column(Integer)
    q3 = Column(Integer)
    ans3 = Column(Integer)
    def __init__(self):
        self.num_ans = 0

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'sex': self.sex,
            'age': self.age,
            'edu1':self.edu1,
            'edu2':self.edu2,
            'edu3':self.edu3,
            'edu4':self.edu4,
            'edu5':self.edu5,
            'edu6':self.edu6,
            'edu7':self.edu7,
            'q1':self.q1,
            'ans1':self.ans1,
            'q2':self.q2,
            'ans2':self.ans2,
            'q3':self.q3,
            'ans3':self.ans3,
            'num_ans':self.num_ans
        }
        '''

'''
engine = create_engine('sqlite:///languageData.db')


Base.metadata.create_all(engine)

