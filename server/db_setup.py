#!/usr/bin/python
#coding:utf-8
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
#from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import ARRAY
Base = declarative_base()


class Question(Base):
    __tablename__ = 'word'

    id = Column(Integer, primary_key=True)
    correct = Column(String(15), nullable=False)
    wrong1 = Column(String(15), nullable=False)
    wrong2 = Column(String(15), nullable=False)
    wrong3 = Column(String(15), nullable=False)
    level = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    fix = Column(Integer, nullable=False)
    group = Column(Integer, nullable=False)
    times_used = Column(Integer)

    def __init__(self):
        self.times_used = 0

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'correct': self.correct,
            'wrong1': self.wrong1,
            'wrong2': self.wrong2,
            'wrong3': self.wrong3,
            'level': self.level

        }


class Child(Base):
    __tablename__ = 'child'

    id = Column(Integer, primary_key=True)
    date_start = Column(String(10))
    ip = Column(String(20))
    sex = Column(String(2))
    age = Column(String(5))
    edu1 = Column(Integer)
    edu2 = Column(Integer)
    edu3 = Column(Integer)
    edu4 = Column(Integer)
    edu5 = Column(Integer)
    edu6 = Column(Integer)
    edu7 = Column(Integer)
    time_info = Column(String(10))


    level = Column(Integer)

    # 上一个选择是否正确,正确为1,错误为-1,不存在为0
    last = Column(Integer)
    # 上上一个选择是否正确
    llast = Column(Integer)

    # 目前最后回答的题目的group，用于产生新题
    lgroup = Column(Integer)

    # 目前回答的单词题目数
    num_word_test = Column(Integer)

    # 预测单词年龄
    pred_age = Column(Integer)

    # 几个详细调查的答案
    A11 = Column(String(10))
    A12 = Column(String(10))
    A13 = Column(String(10))
    A21 = Column(String(10))
    A22 = Column(String(10))
    A23 = Column(String(10))
    A31 = Column(String(10))
    A32 = Column(String(10))
    A33 = Column(String(10))
    A4 = Column(String(10))
    A5 = Column(String(10))
    A6 = Column(String(10))
    A7 = Column(String(10))
    time_survey = Column(String(10))
    num_ans_raven = Column(Integer)
    memory = Column(Integer)
    chance = Column(Integer)

    def __init__(self):
        self.num_ans = 0
        self.level = 1
        self.last = 0
        self.llast = 0
        self.num_word_test = 0
        self.lgroup = 0
        self.chance = 1
        self.num_ans_raven = 0
        self.memory = 3

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'sex': self.sex,
            'age': self.age,
            'edu1': self.edu1,
            'edu2': self.edu2,
            'edu3': self.edu3,
            'edu4': self.edu4,
            'edu5': self.edu5,
            'edu6': self.edu6,
            'edu7': self.edu7,
        }

class WordTest(Base):
    __tablename__ = 'wordtest'
    id = Column(Integer, primary_key=True)
    childID = Column(Integer)
    questionID = Column(Integer)
    answer = Column(String(15))
    time = Column(String(10))
    date = Column(String(10))


class RavenTest(Base):
    __tablename__ = 'raventest'
    id = Column(Integer, primary_key=True)
    childID = Column(Integer)
    questionID = Column(Integer)
    answer = Column(String(15))
    time = Column(String(10))
    date = Column(String(10))

class MemoryTest(Base):
    __tablename__ = 'memorytest'
    id = Column(Integer, primary_key=True)
    childID = Column(Integer)
    questionID = Column(Integer)
    answer = Column(String(15))
    time = Column(String(10))
    date = Column(String(10))

engine = create_engine('sqlite:///language_data.db')
#engine = create_engine('postgresql+psycopg2://openpg:openpgpwd@localhost:22/testdb',echo=True)
Base.metadata.create_all(engine)


