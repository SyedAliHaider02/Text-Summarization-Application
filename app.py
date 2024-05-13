from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tokenize import sent_tokenize
from heapq import nlargest
import string
from collections import Counter

app = Flask(__name__)
app.secret_key = 'b83a1e0ea4e74d22c5d6a3a0ff5e6e66'
nlp = spacy.load("en_core_web_sm")

class Form(FlaskForm):
     text = StringField('Enter the text', validators=[DataRequired()])
     submit = SubmitField('Submit')

nltk.download('stopwords')
nltk.download('punkt')

@app.route('/', methods=['GET', 'POST'])
def home():
    form=Form()
    pred= None

    if form.validate_on_submit():
        text=form.text.data

        pred=prediction(text)
    return render_template('home.html',form=form,pred=pred)

def prediction(text):
    # Function to remove punctuation from the text
    def remove_punc(text):
        new_sent = []
        for sent in sent_tokenize(text):
            words = word_tokenize(sent)
            new_word=[]
            for i in words:
                if i not in string.punctuation:
                    new_word.append(i)
            new_sent.append(' '.join(new_word))
        return ' '.join(new_sent)

    # Function to remove specific HTML tags from the text
    def remove_tags(text):
        br_tags=['<br>','']
        new_sent = []
        for sent in sent_tokenize(text):
            words = word_tokenize(sent)
            new_word=[]
            for i in words:
                if i not in br_tags:
                    new_word.append(i)
            new_sent.append(' '.join(new_word))
        return ' '.join(new_sent)

    # Function to remove stopwords from the text
    def remove_stpwrds(text):
        stop_words = set(stopwords.words('english'))
        new_sent = []
        for sent in sent_tokenize(text):
            words = word_tokenize(sent)
            new_word=[]
            for i in words:
                if i.lower() not in stop_words:
                    new_word.append(i)
            new_sent.append(' '.join(new_word))
        return ' '.join(new_sent)

    # Function to extract keywords from the text
    def extract_keywords(text):
        doc = nlp(text)
        keywords = []
        tags = ['PROPN', 'ADJ', 'NOUN', 'VERB']
        for token in doc:
            if token.pos_ in tags:
                keywords.append(token.text)
        return keywords

    # Function to summarize the text based on keyword frequency
    def summarize_text(text):
        doc = nlp(text)
        text = remove_punc(text)
        text = remove_tags(text)
        text = remove_stpwrds(text)
        keywords = extract_keywords(text)
        freq = Counter(keywords)
        max_freq = freq.most_common(1)[0][1]
        for i in freq.keys():
            freq[i] = freq[i] / max_freq

        sent_strength = {}
        
        for sent in doc.sents:
            for word in sent:
                if word.text in freq.keys():
                    if sent in sent_strength.keys():
                        sent_strength[sent] += freq[word.text]
                    else:
                        sent_strength[sent] = freq[word.text]

        summarized_sentences = nlargest(4, sent_strength, key=sent_strength.get)
        return summarized_sentences

    # Call the summarization function and return the result
    summary = summarize_text(text)
    return summary

if __name__ == '__main__':
    app.run(debug=True)
