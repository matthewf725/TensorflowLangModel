# -*- coding: utf-8 -*-
"""Copy of chatbot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12TFzfodVghEwz_hqjiHhkpQWp_uYu1Ej
"""

import random
import json
import pickle
import numpy as np
import nltk
import tensorflow as tf
import re


from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD, RMSprop

text = open('grammar.txt', 'r').read().lower()
regex.sub('', text)

characters = sorted(set(text))

char_to_index = dict((c, i) for i, c in enumerate(characters))
index_to_char = dict((i, c) for i, c in enumerate(characters))

SEQ_LENGTH = 40
STEP_SIZE = 3

sentences = []
next_characters = []

sentences = []
next_characters = []

for i in range(0, len(text) - SEQ_LENGTH, STEP_SIZE):
  sentences.append(text[i: i + SEQ_LENGTH])
  next_characters.append(text[i + SEQ_LENGTH])

x = np.zeros((len(sentences), SEQ_LENGTH, len(characters)), dtype=np.bool)
y = np.zeros((len(sentences), len(characters)), dtype=np.bool)

for i, sentence in enumerate(sentences):
  for t, character in enumerate(sentence):
    x[i, t, char_to_index[character]] = 1
  y[i, char_to_index[next_characters[i]]] = 1

langModel = Sequential()
langModel.add(LSTM(128, input_shape=(SEQ_LENGTH, len(characters))))
langModel.add(Dense(len(characters)))
langModel.add(Activation('softmax'))

langModel.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.01))

langModelHistory = langModel.fit(x, y, batch_size=256, epochs=10)
langModel.save("langModel.h5", langModelHistory)

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = []
classes = []
documents = []
ignore_letters = ["?", "!", ".", ","]

for intent in intents['intents']:
  for pattern in intent['patterns']:
    word_list = nltk.word_tokenize(pattern)
    words.extend(word_list)
    documents.append((word_list, intent['tag']))
    if intent['tag'] not in classes:
      classes.append(intent['tag'])

words = [lemmatizer.lemmatize(word) for word in words if word not in ignore_letters]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
      bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training)

train_x = list(training[:, 0])
train_y = list(training[:, 1])

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

sgd = SGD(lr=0.01, decay= 1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save('chatbotmodel.h5', hist)

print('done')
