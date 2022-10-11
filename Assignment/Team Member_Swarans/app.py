from flask import Flask,request,render_template
import pickle

app = Flask(__name__, template_folder='template')


@app.route('/')
def hello_world():
    return render_template("login.html")
database={'FlaskApp':'123','sar':'aac','vp':'asdsf'}

@app.route('/form_signup',methods=['GET','POST'])
def create():
      return render_template('login.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
      return render_template('signup.html')

@app.route('/about',methods=['GET','POST'])
def about():
      return render_template('about.html')

@app.route('/login',methods=['GET','POST'])
def log():
      return render_template('login.html')

@app.route('/form_login',methods=['POST','GET'])
def login():
    name1=request.form['username']
    pwd=request.form['password']
    if name1 not in database:
	    return render_template('signup.html',info='Invalid User')
    else:
        if database[name1]!=pwd:
            return render_template('login.html',info='Invalid Password')
        else:
	         return render_template('home.html',name=name1)

if __name__ == '__main__':
    app.debug = True
    app.run()
