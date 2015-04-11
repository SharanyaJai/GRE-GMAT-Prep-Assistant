#!/usr/bin/env python
#
# Copyright (C) 2013 Federico Ceratto and others, see AUTHORS file.
# Released under GPLv3+ license, see LICENSE.txt
#
# Cork example web application
#
# The following users are already available:
#  admin/admin, demo/demo

import bottle
from beaker.middleware import SessionMiddleware
from cork import Cork
from cork.backends import SQLiteBackend
import logging
from bottle import request, route, template
import random
import nltk
from Statistics.Statistics import *
from Spellings.Spellings import *
from Grammar.Grammar import *
from operator import itemgetter
from random import randint
import operator



logging.basicConfig(format='localhost - - [%(asctime)s] %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)
bottle.debug(True)

def populate_backend():
    b = SQLiteBackend('example.db', initialize=True)
    b.connection.executescript("""
        INSERT INTO users (username, email_addr, desc, role, hash, creation_date) VALUES
        (
            'admin',
            'admin@localhost.local',
            'admin test user',
            'admin',
            'cLzRnzbEwehP6ZzTREh3A4MXJyNo+TV8Hs4//EEbPbiDoo+dmNg22f2RJC282aSwgyWv/O6s3h42qrA6iHx8yfw=',
            '2012-10-28 20:50:26.286723'
        );
        INSERT INTO roles (role, level) VALUES ('special', 200);
        INSERT INTO roles (role, level) VALUES ('admin', 100);
        INSERT INTO roles (role, level) VALUES ('editor', 60);
        INSERT INTO roles (role, level) VALUES ('user', 50);
    """)
    return b


def return_backend():
    b = SQLiteBackend('example.db')
    
    return b
b = return_backend()
aaa = Cork(backend=b, email_sender='sharanyajai65@gmail.com', smtp_url='smtp://smtp.magnet.ie')



app = bottle.app()
session_opts = {
    'session.cookie_expires': True,
    'session.encrypt_key': 'please use a random key and keep it secret!',
    'session.httponly': True,
    'session.timeout': 3600 * 24,  # 1 day
    'session.type': 'cookie',
    'session.validate_key': True,
}
app = SessionMiddleware(app, session_opts)


# #  Bottle methods  # #

def postd():
    return bottle.request.forms


def post_get(name, default=''):
    return bottle.request.POST.get(name, default).strip()


@bottle.post('/login')
def login():
    """Authenticate users"""
    username = post_get('username')
    password = post_get('password')
    aaa.login(username, password, success_redirect='/essay', fail_redirect='/login')

@bottle.route('/user_is_anonymous')
def user_is_anonymous():
    if aaa.user_is_anonymous:
        return 'True'

    return 'False'

@bottle.route('/logout')
def logout():
    aaa.logout(success_redirect='/login')


@bottle.post('/register')
def register():
    """Send out registration email"""
    aaa.register(post_get('username'), post_get('password'), post_get('email_address'))
    return 'Please check your mailbox.'


@bottle.route('/validate_registration/:registration_code')
def validate_registration(registration_code):
    """Validate registration, create user account"""
    aaa.validate_registration(registration_code)
    return 'Thanks. <a href="/login">Go to login</a>'


@bottle.post('/reset_password')
def send_password_reset_email():
    """Send out password reset email"""
    aaa.send_password_reset_email(
        username=post_get('username'),
        email_addr=post_get('email_address')
    )
    return 'Please check your mailbox.'


@bottle.route('/change_password/:reset_code')
@bottle.view('password_change_form')
def change_password(reset_code):
    """Show password change form"""
    return dict(reset_code=reset_code)


@bottle.post('/change_password')
def change_password():
    """Change password"""
    aaa.reset_password(post_get('reset_code'), post_get('password'))
    return 'Thanks. <a href="/login">Go to login</a>'


@bottle.route('/')
def index():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')
    return 'Welcome! <a href="/admin">Admin page</a> <a href="/logout">Logout</a>'


@bottle.route('/restricted_download')
def restricted_download():
    """Only authenticated users can download this file"""
    aaa.require(fail_redirect='/login')
    return bottle.static_file('static_file', root='.')


@bottle.route('/my_role')
def show_current_user_role():
    """Show current user role"""
    session = bottle.request.environ.get('beaker.session')
    print "Session from simple_webapp", repr(session)
    aaa.require(fail_redirect='/login')
    return aaa.current_user.role


# Admin-only pages

@bottle.route('/admin')
@bottle.view('admin_page')
def admin():
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/sorry_page')
    return dict(
        current_user=aaa.current_user,
        users=aaa.list_users(),
        roles=aaa.list_roles()
    )


@bottle.post('/create_user')
def create_user():
    try:
        aaa.create_user(postd().username, postd().role, postd().password)
        return dict(ok=True, msg='')
    except Exception, e:
        return dict(ok=False, msg=e.message)


@bottle.post('/delete_user')
def delete_user():
    try:
        aaa.delete_user(post_get('username'))
        return dict(ok=True, msg='')
    except Exception, e:
        print repr(e)
        return dict(ok=False, msg=e.message)


@bottle.post('/create_role')
def create_role():
    try:
        aaa.create_role(post_get('role'), post_get('level'))
        return dict(ok=True, msg='')
    except Exception, e:
        return dict(ok=False, msg=e.message)


@bottle.post('/delete_role')
def delete_role():
    try:
        aaa.delete_role(post_get('role'))
        return dict(ok=True, msg='')
    except Exception, e:
        return dict(ok=False, msg=e.message)


# Static pages

@bottle.route('/login')
@bottle.view('login_form')
def login_form():
    """Serve login form"""
    return {}


@bottle.route('/sorry_page')
def sorry_page():
    """Serve sorry page"""
    return '<p>Sorry, you are not authorized to perform this action</p>'




@bottle.route('/essay')
def prin():

  printme= '''<html>             <body>  <form action="/essay" method="POST">    <a href="/">Home</a>        Enter essay:        <input type="text" size=1000 name="ess"></input><br/><input type="submit" name="submit"/>       </body>       </html></form>'''
  return printme
       
       
       
@bottle.route('/essay', method='POST')
def prin():
    essaycontent = request.forms.get('ess')
    print essaycontent
    global essaycontent
    essay = str(essaycontent)
    
    print "essay is ",essay
    printme="<html><a href='/'>Home</a><br/>"
    printme+="Your essay is <br/>"+essay+"<br/>"
#Statistics
    wordCount = getWordCount(essay)
    sentCount = getSentenceCount(essay)
    paraCount = getParaCount(essay)
    avgSentLen = getAvgSentenceLength(essay)
    stdDevSentLen = getStdDevSentenceLength(essay)
  

    printme+="Spell-checking...<br/>"

  #Spellings
    numMisspelt, misspeltWordSug = spellCheck(essay)


    printme+="Analyzing Grammar and Structure...<br/>"


  #Grammar
    grammarCumScore, grammarSentScore = getGrammarScore(essay)
    


  #Overall
    overallScore = str(format((((1-(float(numMisspelt)/wordCount))*5) + grammarCumScore)/3, '.2f'))
    printme+="Essay score is <b>"+ overallScore+ "</b><br/><a href='\wordlist'>Wordlist</a>"
    printme+='''<div style=" font-size:18pt" id = "scoretable"><h2> Overall Score</h2><table border="1">                        <tr> <th class = "big">GRADE (0-5)</th> <th class = "big">'''
    printme+= str(overallScore)
    printme+='''</th></tr><tr> <th>Spelling(0-5)</th><td>'''
    printme+=str(format((1-(float(numMisspelt)/wordCount))*5,'.2f'))
    printme+='''</td></tr> <tr> <th>Grammar(0-5)</th><td>'''
    printme+=str(format(grammarCumScore,'.2f'))
    printme+='''</td></tr>                       </table>                        </div>                        <br/>                        <br/>                <div  id = "statistics">                        <h2> Essay Statistics</h2>                        <table border = "1" align="left">                                <tr align='left'> <th>Word Count</th> <td>'''
    printme+=str(wordCount)
    printme+='''</td></tr>                                <tr align='left'> <th>Sentence Count</th> <td>'''
    printme+=str(sentCount)
    printme+= '''</td></tr>                                <tr align='left'> <th>Paragraph Count</th> <td>'''
    printme+= str(paraCount)
    printme+='''</td></tr>                                <tr align='left'> <th>Average Sentence Length</th> <td>'''
    printme+=str(format(avgSentLen,'.2f'))
    printme+='''</td> </tr>                                <tr align='left'> <th>Standard Deviation from the Average Sentence Length</th> <td>'''
    printme+=str(format(stdDevSentLen,'.2f'))
    printme+= '''</td> </tr>                       </table>                </div>            </div>                     <br/><br/><br/><br/><br/><br/><br/><br/>                <div id = "spellings">                               <h2> Spellings </h2>                        <h3>Number of Misspelt Words ::''' 
    printme+= str(numMisspelt)
    printme+= '''</h3>                        <h2 class="score" >Score :: '''
    printme+= str(format((1-(float(numMisspelt)/wordCount))*5,'.2f'))
    printme+='''</h2>                        <table border="1">                                <thead> <tr> <th>Misspelt Word</th> <th> Spelling Suggestions</th> </tr> </thead>                                <tbody>'''
    for key in misspeltWordSug:
       printme+= "<tr> <td>" + key + "</td> <td> " + str(misspeltWordSug[key]) + "</td> </tr>"


    printme+= '''</tbody>                        </table>                </div>                <br /> <hr /> <hr /> <br />                        <h2> Grammar </h2>                        <h2  class = "score" >Score :: '''
    printme+=str(format(grammarCumScore,'.2f'))
    printme+='''</h2>                        <table border="0">                                <thead> <tr> <th>Sentences</th> <th> Score</th> </tr> </thead>                                <tbody>'''
                                
  #prints sorted table
    for key in reversed(sorted(list(grammarSentScore.items()), key=itemgetter(1))):
        printme+= "<tr> <td>" + key[0] + "</td> <td> " + str(key[1]) + "</td> </tr>"      
        
    printme+= ''' </tbody>                        </table>                </div>                <br /> <hr /> <hr /> <br />                                        </html>'''

    print "Essay has been Graded and the Score Report has been generated!!"
    return printme

# #  Web application main  # #



global correctansno

@bottle.route('/wordlist')
def wordlist():
  global correctansno
  '''Serve wordlist'''
  files=open("list.txt","r")
  content= []
  wordlist=[]
  incorrect1=""
  incorrect2=""
  incorrect3=""
  mapping={}
  correct=""
  showme=""
  for line in files:
    pointer=0
    word=[]
    defn=[]
    words=''
    defns=''
    while (line[pointer]!='\t' and line[pointer]!='\n'):
      word.append(line[pointer])
      pointer=pointer+1
    while (line[pointer]!='\n'):
      if(line[pointer]!="\t"):
        defn.append(line[pointer])
      pointer=pointer+1
      words=''.join(word)
      defns=''.join(defn)
      defns=defns[1:]
    mapping[words]=defns
    wordlist.append(words)
  showme=showme+"What does this word mean?<br/><br/>"
  anslist=[]
  print "Wordlist size is "
  lenword=str(len(wordlist))
  print lenword
  showword=wordlist[randint(0,4000)]
  correct=mapping[showword]
  anslist.append(correct)
  incorrect1=mapping[wordlist[randint(1,4000)]]
  anslist.append(incorrect1)
  incorrect2=mapping[wordlist[randint(1,4000)]]
  anslist.append(incorrect2)
  incorrect3=mapping[wordlist[randint(1,4000)]]
  anslist.append(incorrect3)
  random.shuffle(anslist)
  for i in range(0,4):
    if(anslist[i]==correct):
      correctansno=i
      print "Correct answer num is "+ str(correctansno)
      
  showme+="<br/>"
  showme+=incorrect1
  showstring='''What does this word mean: '''
  showstring+=showword
  showstring+= ''' <form action="/wordlist" method="post">'''+ str(anslist[0])+''' <input type="radio" name="ans" value="0"/><br/>'''+  str(anslist[1])+'''<input type="radio" name="ans" value="1"/><br/>'''+str(anslist[2])+'''
            <input type="radio" name="ans" value="2"/><br/>'''+ str(anslist[3])+''' <input type="radio" name="ans" value="3"/> <br/> <input value="Submit" type="submit" /> </form> '''
  return showstring

@bottle.route('/wordlist', method='POST')
def do_login():
    global correctansno
    choice = request.forms.get('ans')
    if str(choice)==str(correctansno):
        #session = bottle.request.environ.get('beaker.session')
        #aaa.require(fail_redirect='/login')
        #aaa.current_user.username
        #b = SQLiteBackend('example.db', initialize=True)
        return "<p>Your answer was correct.</p><a href='\wordlist'>Next word</a><br/><a href='\math'>Math</a>"
    else:
        return "<p>Your answer was incorrect</p><a href='\wordlist'>Next word</a><br/><a href='\math'>Math</a"
# #  Web application main  # #



global mathanswer
@bottle.route('/math')

def random_question():
    global mathanswer
    """Generate a pair consisting of a random question (as a string)
    and its answer (as a number)"""
    binary_operations = [    ('+', operator.add),    ('-', operator.sub),    ('*', operator.mul),]

    op_sym, op_func = random.choice(binary_operations)
    n1 = random.randint(0, 10000)
    n2 = random.randint(0, 10000)
    question = '{} {} {}'.format(n1, op_sym, n2)
    mathanswer = op_func(n1, n2)
    showstring=question
    showstring+= ''' <br/><form action="/math" method="post">            <input type="text" name="ans"/><br/><input value="Submit" type="submit" /> </form> '''
    return showstring
  
  
@bottle.route('/math', method='POST')
def do_login():
    global mathanswer
    ans = request.forms.get('ans')
    if str(ans)==str(mathanswer):
        #session = bottle.request.environ.get('beaker.session')
        #aaa.require(fail_redirect='/login')
        #aaa.current_user.username
        #b = SQLiteBackend('example.db', initialize=True)
        return "<p>Your answer was correct.</p><a href='\wordlist'>Next word</a><br/><a href='\math'>Next Math Question</a>"
    else:
        return "<p>Your answer was incorrect</p><a href='\wordlist'>Next word</a><br/><a href='\math'>Next Math Question</a"


def main():

    # Start the Bottle webapp
    bottle.debug(True)
    bottle.run(app=app, quiet=False, reloader=True, port=8092)

if __name__ == "__main__":
    main()
