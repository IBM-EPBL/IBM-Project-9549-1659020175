from contextlib import redirect_stderr
from turtle import title
from flask import Flask, jsonify, request, make_response,render_template,redirect
from flask import json
import ibm_db
import uuid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

app= Flask(__name__)

app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

con = ibm_db.connect("DATABASE=bludb;HOSTNAME=ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31505;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=xxr28209;PWD=dEMK5Mv2XMfpoXH6",'','')

def sendemail(email,password):
    # using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python



    sg = sendgrid.SendGridAPIClient(api_key="")
    from_email = Email("gb170216@gmail.com")  # Change to your verified sender
    to_email = To(str(email))  # Change to your recipient
    subject = "Sending with SendGrid is Fun"
    content = Content("text/plain", "your username is " + email + " and password is " + password)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)



@app.route("/",methods=["GET"])
def main():
    print(con)
    print(uuid.uuid4())
    return render_template("home.html")

@app.route("/register",methods=["GET"])
def register_get():
    return render_template("register.html")

@app.route("/register",methods=["POST"])
def register_post():
    email=request.form['email']
    password=request.form['password']
    name = request.form['username']
    phone = request.form['phone']

    print(email,password) 

    userDetailSql = """INSERT INTO  "XXR28209"."USERDETAIL" ("NAME","PHONE","EMAIL")  VALUES(?,?,?);"""
    userDetailStmt = ibm_db.prepare(con,userDetailSql)

    ibm_db.bind_param(userDetailStmt,1,name)
    ibm_db.bind_param(userDetailStmt,2,phone)
    ibm_db.bind_param(userDetailStmt,3,email)

    ibm_db.execute(userDetailStmt)

    loginCredSql="""INSERT INTO  "XXR28209"."LOGINCRED" ("EMAIL","PASSWORD") VALUES(?,?);"""
    loginCredStmt = ibm_db.prepare(con,loginCredSql)

    ibm_db.bind_param(loginCredStmt,1,email)   
    ibm_db.bind_param(loginCredStmt,2,password)   

    ibm_db.execute(loginCredStmt)

    sendemail(email,password)

    return redirect("/login")

@app.route("/login",methods=["GET"])
def login_get():

    return render_template("login.html")


@app.route("/login",methods=["POST"])
def login_post():

    userEmail = request.form['email']
    userPassword = request.form['password']

    userFetchSql = """SELECT  *  FROM "XXR28209"."LOGINCRED" where email = '{email}' and password = '{password}';""".format(email=userEmail,password=userPassword)

    userFetchStmt = ibm_db.exec_immediate(con, userFetchSql)
    fetchEmail=""
    while ibm_db.fetch_row(userFetchStmt) != False:
        fetchEmail = ibm_db.result(userFetchStmt, 0)

    if(fetchEmail == userEmail):
        # session['username'] = username
        print(fetchEmail)
        return redirect("/")

    return render_template("login.html")
    

@app.route("/news",methods=["GET"])
def news():

    return render_template("news.html")


@app.route("/addnews",methods=["GET"])
def addnews_get():
    id = str(uuid.uuid4().int)[:10]
    print(len(id))
    print(id)
    return render_template("addnews.html")

@app.route("/addnews",methods=["POST"])
def addnews_post():
    date = str(request.form['date'])
    time = str(request.form['time'])
    title = request.form['title']
    content = request.form['content']
    id = str(uuid.uuid4().int)[:10]
    genre = request.form['genre']

    idFetchSql = """SELECT "NEWSID" FROM "XXR28209"."NEWS";"""

    idFetched = ibm_db.exec_immediate(con,idFetchSql)
    allId =[]
    while(ibm_db.fetch_row(idFetched)):
        allId.append(ibm_db.result(idFetched,0))
    print(allId)
    while(id in allId):
        id=str(uuid.uuid4())[:10]
    
    print(date,time,title,content,id)


    addNewsSql = """INSERT INTO  "XXR28209"."NEWS" ("TITLE","CONTENT","DATE","TIME","NEWSID","GENRE")  VALUES(?,?,?,?,?,?);"""
    addNewsStmt = ibm_db.prepare(con,addNewsSql)

    ibm_db.bind_param(addNewsStmt,1,title)
    ibm_db.bind_param(addNewsStmt,2,content)
    ibm_db.bind_param(addNewsStmt,3,date)
    ibm_db.bind_param(addNewsStmt,4,time)
    ibm_db.bind_param(addNewsStmt,5,id)
    ibm_db.bind_param(addNewsStmt,6,genre)

    ibm_db.execute(addNewsStmt)

    return redirect("/addnews")

@app.route("/news/<newsId>",methods=["GET"])
def news_fetch(newsId):
    print(newsId)
    newsFetchSql = """SELECT * FROM "XXR28209"."NEWS" WHERE NEWSID = '{nid}';""".format(nid=str(newsId))

    newsFetched = ibm_db.exec_immediate(con,newsFetchSql)
    title=""
    content=""
    date=""
    time=""
    id=""

    while(ibm_db.fetch_row(newsFetched)):
        title=ibm_db.result(newsFetched,0)
        content=ibm_db.result(newsFetched,1)
        date=ibm_db.result(newsFetched,2)
        time=ibm_db.result(newsFetched,3)
        id=ibm_db.result(newsFetched,4)
    print(title,content,date,time,id)
    return render_template("news.html",title=title,content=content,id=id,date=date,time=time)

@app.route("/dashboard",methods=["GET"])
def displayNews():
    genre = request.args.get('genre')
    idFetchSql = f"""SELECT "TITLE","NEWSID" FROM "XXR28209"."NEWS" """
    if(genre !="" and genre!=None and genre!="All"): 
        idFetchSql+=f"""WHERE "GENRE" = '{genre}'"""
    idFetchSql+="ORDER BY DATE;"
    dataFetched = ibm_db.exec_immediate(con,idFetchSql)
    allIds =[]
    allTitles =[]
    while(ibm_db.fetch_row(dataFetched)):
        allTitles.append(ibm_db.result(dataFetched,0))
        allIds.append(ibm_db.result(dataFetched,1))
    print(allTitles)
    print(allIds)

    return render_template("dashboard.html",allids = allIds,alltitles=allTitles)



if __name__=="__main__":
    app.run(debug=True)