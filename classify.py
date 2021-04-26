import re
import pandas as pd
from pandas import DataFrame
import pythainlp
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn import model_selection, preprocessing, linear_model, naive_bayes, metrics, svm
from sklearn.naive_bayes import BernoulliNB, ComplementNB, MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix, classification_report
import time

def clean(ls_sms):
    temp = []
    for i in ls_sms:
        i = re.sub(r'\s|[*/$฿&/.,;:{}""+-=@#~%^<>()↲!?|_]|\d|[a-z]|[A-Z]','',i)
        temp.append(i)
    ls_sms = temp
    return ls_sms

def token(ls_sms):
    temp = []
    for i in ls_sms:
        words = word_tokenize(i, engine = 'newmm')
        temp.append(words)
    return temp

def remove_stop(temp, added_stop):
    nltk_th_stop = set(pythainlp.corpus.common.thai_stopwords())
    temp3 = []
    for i in temp:
        temp2 = []
        for j in i:
            if j not in nltk_th_stop and not j in added_stop: 
                temp2.append(j)
                x = " ".join(temp2)
        temp3.append(x)
    ls_sms = temp3
    return ls_sms

# Prepare data
# Import data
data = pd.read_csv("sms2.csv", encoding = "utf-8")
# Print sample
print()
print("+"*10 ,"Sample Data", "+"*10)
print(data.head())
print()

# Clean text
data['sms'] = clean(data['sms'])
token = token(data['sms'])
added_stop = ["สวัสดี", "เฉพาะ", "คุณ", "มค", "กพ", "มีค", "เมย", "พค", "มิย", "กค", "สค", "กย", "ตค", "พย", "ธค"]
data['sms'] = remove_stop(token, added_stop)

# Split data into train and validation
train_x, valid_x, train_y, valid_y = model_selection.train_test_split(data["sms"], data["label"], test_size = 0.25, random_state = 0)

# Encode and TFIDF
encoder = preprocessing.LabelEncoder()
train_y = encoder.fit_transform(train_y)
valid_y = encoder.fit_transform(valid_y)
tfidf_vect = TfidfVectorizer(analyzer = 'word', token_pattern=r'\w{1,}')
tfidf_vect.fit(data["sms"])
xtrain_tfidf = tfidf_vect.transform(train_x)
xvalid_tfidf = tfidf_vect.transform(valid_x)
xtrain_tfidf.data

# Training & testing algorithm
# MultinomialNB, MultinomialNB, and ComplementNB with alpha = 1.0, 0.1, 0.01, and 0.001 
classifier = [MultinomialNB(alpha = 1.0), BernoulliNB(alpha = 1.0), ComplementNB(alpha = 1.0)]

for i in classifier:
    start = time.time()
    i.fit(xtrain_tfidf, train_y)
    pred_y = i.predict(xvalid_tfidf)
    end = time.time()

    accuracy = metrics.accuracy_score(pred_y, valid_y)
    precision = metrics.precision_score(pred_y, valid_y)
    recall = metrics.recall_score(pred_y, valid_y)
    confusion = metrics.confusion_matrix(pred_y, valid_y)
    target_names = ["0 gambling", "1 ok"]
    class_report = metrics.classification_report(pred_y, valid_y, target_names = target_names)

    print()
    print(i)
    print("Sample row and column: ", xtrain_tfidf.shape)
    print("Time: ", end - start)
    print("Accuracy: ", accuracy)
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("Confusion matrix:")
    print(confusion)
    print("Classification report:")
    print(class_report)
    print("-"*10)
