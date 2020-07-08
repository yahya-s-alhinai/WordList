from flask import Flask, request, Response, render_template
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Regexp
import re
import json

class WordForm(FlaskForm):
    avail_letters = StringField("Letters &nbsp;", validators= [Regexp(r'^$|^[a-z]+$', message="must contain letters only")], render_kw={"class": "select-box2"})
    words_length = SelectField('words length  &nbsp;', choices=[('0', ' '), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], render_kw={"class": "select-box"})
    words_limit = StringField("Limit  &nbsp;", validators= [Regexp(r'^$|^[a-z.]+$', message="must contain letters and . only ")], render_kw={"class": "select-box2"})
    submit = SubmitField("Search", render_kw={"class": "submit-button"})


csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/')
def home():
    form = WordForm()
    return render_template("index.html", form=form)


@app.route('/index')
def index():
    form = WordForm()
    return render_template("index.html", form=form)


@app.route('/words', methods=['POST','GET'])
def letters_2_words():
    
    form = WordForm()
    letters = form.avail_letters.data
    limit = form.words_limit.data
    wLength = int(form.words_length.data)
    if form.validate_on_submit() and (letters != "" or limit != "") and (wLength == 0 or len(limit) == 0 or len(limit) == wLength):
        wLength = int(form.words_length.data)
    else:
        return render_template("index.html", form=form)

    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())

    word_set = []
    if letters == "":
        word_set = good_words
    else: 
        for l in range(3,len(letters)+1):
            word_permut = set()
            if wLength != 0 and l != wLength:
                continue
            for word in itertools.permutations(letters,l):
                w = "".join(word)
                if w in good_words:
                    word_permut.add(w)
            word_set += sorted(word_permut)

    if limit != "":
        r = re.compile('^' + limit + '$')
        word_set = filter(r.match, word_set)
    
    
    shortDef = []
    for word in word_set:
        ref = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/' + word + '?key=5952a898-04c7-450f-b1f0-425174acc97f'
        resb = requests.get(ref).content
        res = json.loads(resb)

        if len(res) == 20:
            shortDef.append(' '.join(res))
        else:
            keep = ''
            for i in range(0 , len(res)):
                if len(res[i]['shortdef']) == 1:
                    keep = keep + res[i]['shortdef'][0] + '\n'
            # shortDef.append(res[0]['shortdef'][0])
            shortDef.append(keep)

    return render_template('wordlist.html', wordlist=word_set, letterNum=len(word_set), shortDef=shortDef)


@app.route('/proxy')
def proxy():
    result = requests.get(request.args['url'])
    resp = Response(result.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp


