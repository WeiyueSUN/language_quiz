import pandas as pd
from database_setup import Base, Question
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///languageData.db')

DBSession = sessionmaker(bind=engine)
session = DBSession()

questionData = pd.read_csv("questionData.csv")
print questionData
for i in questionData.index:
    question = Question()
    print questionData['correct']
    question.correct = questionData['correct'][i]
    question.wrong1 = questionData['wrong1'][i]
    question.wrong2 = questionData['wrong2'][i]
    question.wrong3 = questionData['wrong3'][i]
    session.add(question)
    session.commit()