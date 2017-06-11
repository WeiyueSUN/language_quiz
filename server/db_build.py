import pandas as pd
from db_setup import Base, Question
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql
engine = create_engine('sqlite:///language_data.db')
#engine = create_engine('postgresql+psycopg2://openpg:openpgpwd@localhost:22/testdb',echo=True)
DBSession = sessionmaker(bind=engine)
session = DBSession()

questionData = pd.read_csv("ques_data.csv")
print questionData
for i in questionData.index:
    question = Question()
    question.correct = questionData['correct'][i]
    question.wrong1 = questionData['wrong1'][i]
    question.wrong2 = questionData['wrong2'][i]
    question.wrong3 = questionData['wrong3'][i]

    question.level = questionData['level'][i]
    question.age = questionData['age'][i]
    question.fix = questionData['fix'][i]
    question.group = questionData['group'][i]
    session.add(question)
    session.commit()