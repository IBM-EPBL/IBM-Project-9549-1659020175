from flask import Flask, request, make_response,render_template,redirect
import ibm_db
import uuid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

app= Flask(__name__)

app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

con = ibm_db.connect("DATABASE=bludb;HOSTNAME=ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31505;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=xxr28209;PWD=dEMK5Mv2XMfpoXH6",'','')

def sendemail(email,password):
    # using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python



    sg = sendgrid.SendGridAPIClient(api_key="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")
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

if __name__=="__main__":
    app.run(debug=True)