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
    is_male = Column(Integer)
    is_female = Column(Integer)
    age = Column(String(5))
    edu1 = Column(Integer)
    edu2 = Column(Integer)
    edu3 = Column(Integer)
    edu4 = Column(Integer)
    edu5 = Column(Integer)
    edu6 = Column(Integer)
    edu7 = Column(Integer)


    num_ans = Column(Integer)
    word_id1 = Column(Integer)
    choose_id1 = Column(Integer)
    word_id2 = Column(Integer)
    is_correct2 = Column(Integer)
    word_id3 = Column(Integer)
    is_correct3 = Column(Integer)
    def __init__(self):
        self.num_ans = 0

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'is_male': self.is_male,
            'is_female': self.is_female,
            'age': self.age
        }
        '''

'''
engine = create_engine('sqlite:///languageData.db')


Base.metadata.create_all(engine)

