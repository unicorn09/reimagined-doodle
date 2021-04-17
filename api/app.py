# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 16:39:26 2021

@author: UNICORN
"""
import json
import flashtext
import stanza
stanza.download('en')
import re


from flashtext import KeywordProcessor
import flashtext

import python_utils
import spacy


import nltk
nltk.download('wordnet')
import difflib
from nltk.corpus import wordnet
from collections import defaultdict
from flashtext import KeywordProcessor


from flask import Flask, request, jsonify,render_template
from flask_cors import CORS, cross_origin

from urllib.parse import urlencode, quote_plus
import requests
app = Flask(__name__)
CORS(app, support_credentials=True)

keyword_dict = defaultdict(list)
keyword_dict_wedding = defaultdict(list)

nlp = stanza.Pipeline(lang='en', processors='tokenize,ner,pos')
alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"


with open('model_dictionary.json') as f:
  data=json.load(f)

for i in data.keys():
  data[i]=[x for x in data[i] if str(x)!='nan']

def get_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences





def bio_tagger(entity, start_char, end_char, tag):
    bio_tagged = {"tag":None, "end_char":None, "start_char":None,"len":None,"phrase":None}
    ne_tagged = entity.split()
    if len(ne_tagged) == 1:
        bio_tagged["start_char"] = start_char
        bio_tagged["end_char"] = start_char + len(ne_tagged[0])
        bio_tagged["tag"] = "B-"+tag
        bio_tagged["len"]="1" 
        bio_tagged["phrase"]=ne_tagged
    elif len(ne_tagged) == 2:
        bio_tagged["start_char"] = start_char
        bio_tagged["end_char"] = start_char + len(ne_tagged[0])
        bio_tagged["tag"] = "B-"+tag
        bio_tagged["len"]="1"
        

        bio_tagged["start_char"] = end_char - len(ne_tagged[-1])
        bio_tagged["end_char"] = end_char 
        bio_tagged["tag"] = "E-"+tag
        bio_tagged["len"]="2"
        bio_tagged["phrase"]=ne_tagged

    elif len(ne_tagged) >= 3:
        bio_tagged["start_char"] = start_char
        bio_tagged["end_char"] = start_char + len(ne_tagged[0])
        bio_tagged["tag"] = "B-"+tag
        bio_tagged["len"]="2"

        bio_tagged["start_char"] = end_char - len(ne_tagged[-1])
        bio_tagged["end_char"] = end_char 
        bio_tagged["tag"] = "E-"+tag
        bio_tagged["len"]="3"
        bio_tagged["phrase"]=ne_tagged

        cursor = start_char + len(ne_tagged[0]) + 2
        for tok in ne_tagged[1:-1]:
            bio_tagged["start_char"] = cursor
            bio_tagged["end_char"] = cursor + len(tok) 
            bio_tagged["tag"] = "I-"+tag
            bio_tagged["len"]=len(ne_tagged)
            bio_tagged["phrase"]=ne_tagged
            cursor = cursor + len(tok)  + 2
    return bio_tagged


def bio_corpus_builder(text, tags2dict):
    
    corpus = []
    document = []
    extract=[]

    for tag, tag_values in tags2dict.items():
        keyword_processor = KeywordProcessor()
        keyword_processor.add_keywords_from_list(tag_values)

        for sent in get_sentences(text):
            id=1
            word_tag_tagger = []
            each_token = {"id":None,"text": None, "upos":None, "xpos":None,"ner":None, "end_char":None, "start_char":None}
            entities_found = keyword_processor.extract_keywords(sent, span_info=True)
            if entities_found:
              
                for word_tag in entities_found:
                    word_tag_tagger.append(bio_tagger(word_tag[0], word_tag[1], word_tag[2], tag))
                
                doc = nlp(sent)
                sentence = doc.sentences[0]
                extract.append(word_tag_tagger)
                each_sent = []
                for token in sentence.tokens:
                    each_token["id"]=id
                    each_token["text"] = token.text
                    each_token["ner"] = token.ner
                    each_token["end_char"] = token.end_char
                    each_token["start_char"] = token.start_char
                    each_token["upos"] = token.to_dict()[0]["upos"]
                    each_token["xpos"] = token.to_dict()[0]["xpos"]
                    each_sent.append(dict(each_token))
                    id=id+1
               
                for tok in each_sent:
                    for word2tags in word_tag_tagger:
                        if (int(tok["start_char"]) == int(word2tags["start_char"])) and (int(tok["end_char"]) == int(word2tags["end_char"])):
                            tok["tag"] = word2tags['tag']


                document.append(each_sent)
           
        del keyword_processor
        

    doc=nlp(text)
    sentence = doc.sentences[0]
    return document,extract,sentence



def get_words(text):
  return text.split()

def codetosparql(s):
  req="PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX ab: <http://culture-of-india.herkokuapp.com/#>\n"

  req=req+'SELECT '

  x=-1
  lst=get_words(s)
  propert=[]
  query=[]
  category=lst[1]
  allqueries=''
  
  for i in range(3,len(lst)):
    if lst[i]=="-q":
      x=i
      break
    propert.append(lst[i])
  
  
  for i in range(x+1,len(lst)):
    allqueries=allqueries+lst[i]+' '
  
  query=(allqueries.split(";")) 
  
  
  for i in range(0,len(propert)):
    req=req+'?'+category+'_'+propert[i]+' '
  req=req+'\n'+'WHERE{'+'\n'
  
  

  for i in range(0,len(propert)):
    req=req+'?'+category+' ab:'+category+'_'+propert[i]+' ?'+category+'_'+propert[i]+"."+'\n'
   
  
  for i in range(0,len(query)-1):
    ta=query[i]
    data=[ta[ta.find("-")+1:]][0]
    data_prop=[ta[0:ta.find("-")]][0]
    if data_prop=='food' or data_prop=='festival':
      data_prop='name'
    req=req+'?'+category+' ab:'+category+'_'+data_prop+' ?'+category+'_'+data_prop+"."+'\n'
  for i in range(0,len(query)-1):
    ta=query[i]
    data=[ta[ta.find("-")+1:]][0]
    data_prop=[ta[0:ta.find("-")]][0]
    if data_prop=='food' or data_prop=='festival':
      data_prop='name'
    req=req+'FILTER CONTAINS(lcase(str(?'+category+'_'+data_prop+")),"+'"'+data.lower()+'").\n'
  req=req+"}"  
  
  return req

def nltosparql(txt):
  commonlist=['festival','food','wedding']
  dp_festival=["name","significance","clothes","time","celebration","region","state","food","desc"]
  dp_food=["name","ingredients","fat","carbohydrates","energy","protein","description","type","region"]  
  dp_wedding=["significance","clothes","region","state"]

  lst=list(keyword_processor.extract_keywords(txt))
  finalcode="-cat ";
  quer=''
  categ=''
  doc=bio_corpus_builder(txt, data)
  
  if len(doc[1])==0:

    for token in doc[2].tokens:
      if difflib.get_close_matches(token.text.lower(), commonlist):
        categ=difflib.get_close_matches(token.text.lower(), commonlist)[0]
      

      if categ=='festival':
        categ='festival'
      if categ=='food':   
        categ='food'
      if categ=='wedding':
        categ='wedding'
    
  else:
    for k in doc[1]:
      ta=k[0]['tag']
      ta_name=k[0]['phrase']
      ta_name=' '.join(ta_name)
  
      tags=[ta[ta.find("-")+1:]][0]
      

      quer=quer+(tags+'-'+ta_name)+';'

    if tags=='festival' or tags=='food':
      categ=tags

  
    if categ not in commonlist:
      for token in doc[2].tokens:

        if difflib.get_close_matches(token.text.lower(), commonlist):
          categ=difflib.get_close_matches(token.text.lower(), commonlist)[0]

   
  if len(lst)==0 and categ=='festival':
    
    if 'How' in txt or 'how' in txt:
      lst.append('celebration')
    if 'When' in txt or 'when' in txt:
      lst.append('time')
    if 'Where' in txt or 'where' in txt:
      lst.append('celebration')  
    if 'What' in txt or 'what' in txt:
      lst.append('desc')
      lst.append('name')  
    
  if len(lst)==0:
    lst.append('name')
    lst.append('celebration')  

  elif len(lst)==0 and categ=='food':
      
    if len(lst)==0:
      lst.append('name')
      lst.append('description')
      lst.append('ingredients')  
  
   

  finalcode=finalcode+categ+" -de "

  if categ=='festival':
    fest=["name","significance","clothes","time","celebration","region","state","food","desc"]
  elif categ=='food':
    fest=["name","ingredients","fat","carbohydrates","energy","protein","description","type","region"]  
  for i in lst:
    try:
      if categ=='food' and i in dp_food:
        finalcode=finalcode+(i)+' '
      elif categ=='festival' and i in dp_festival:
        finalcode=finalcode+(i)+' '  
    except:
      x=1
  finalcode=finalcode+' -q '+quer
  
  codtospa=codetosparql(finalcode)
  payload = {'query':codtospa}
  result = urlencode(payload, quote_via=quote_plus)
  res='http://20.62.194.80:3030/ds/query?'
  
  URL=res+result
  datajson = requests.get(URL).json()
  return(datajson)

fest=["name","significance","clothes","time","celebration","region","state","food","description","god","wear","eat","origin"]
food=["ingredients","fat","carbohydrates","energy","protein","description","type","category"]

for fes in fest:
  for synset in wordnet.synsets(fes):
    for lemma in synset.lemmas():
      keyword_dict[fes].append(lemma.name())
     
ls=keyword_dict["god"]
ls2=keyword_dict["wear"]
ls3=keyword_dict["eat"]
ls4=keyword_dict["origin"]

for i in ls:
  keyword_dict["significance"].append(i)
for i in ls2:
  keyword_dict["clothes"].append(i)
for i in ls3:
  keyword_dict["food"].append(i)    
for i in ls4:
  keyword_dict["significance"].append(i)    


keyword_dict["god"]=[]  
keyword_dict["wear"]=[]  
keyword_dict["eat"]=[]  
keyword_dict["origin"]=[]

for fes in food:
  for synset in wordnet.synsets(fes):
    for lemma in synset.lemmas():
      keyword_dict[fes].append(lemma.name())

ls=keyword_dict["category"]
for i in ls:
  keyword_dict["type"].append(i)
keyword_dict["category"]=[]  


keyword_processor = KeywordProcessor()
keyword_processor.add_keywords_from_dict(keyword_dict)


@app.route('/getsparql/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    ques = request.args.get("ques", None)
    
    # For debugging
    print(f"got query {ques}")

    # Check if user sent a name at all
    response={'ans':nltosparql(ques)}
    print(response)
    # Return the response in json format
    return jsonify(response)

@app.route('/getweb/', methods=['GET'])
@cross_origin(supports_credentials=True)
def responds():
    # Retrieve the name from url parameter
    ques = request.args.get("ques", None)
    # For debugging
    print(f"got query {ques}")
    
    # Check if user sent a name at all
    response={'ans':nltosparql(ques)}
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(response)
    # Return the response in json format
    return jsonify(response)
@app.route('/home')
def home():
    return render_template('index.html')
# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to unicorn server !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
