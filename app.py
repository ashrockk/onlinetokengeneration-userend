from flask import Flask, render_template,request,json,redirect,session,url_for,make_response
import socketio,time
from reportlab.pdfgen import canvas
from tokenavailable import get_token,check_avalailability,check_notification,check_onetimetokenrequest
from databasecon import cnx,cursor
app=Flask(__name__,template_folder="template")
app.secret_key = 'secret_key'
sio = socketio.Client()
@sio.event
def connect():
    print('connection established')
@sio.event
def disconnect():
    print('disconnected from server')
@sio.event
def message(data):
    print('message received:', data)

def get_password(email):
    a=list()
    query= 'SELECT name,password FROM user WHERE email= %s '
    values=email
    access_pass=tuple()
    cursor.execute(query,(values,))
    access_pass=cursor.fetchall()
    for i in access_pass:
        ac_name=i[0]
        ac_pass=i[1]
    cnx.commit()
    a=[ac_name,ac_pass]
    return a

class user_forlogin:
    def __init__(self,name,email,password):
        self.name=name
        self.email=email
        self.password=password
    def checktokenforsuser(self):
         if check_onetimetokenrequest(self.email)==1:
              return 1
                #token taken already
         else:
              # token not taken
              return 0
    def get_name(self):
        return self.name
    def get_email(self):
        return self.email
    def user_tokenid(self):
        usertoken_info=get_token(self.email)
        return usertoken_info[0]
    def user_arrivaltime(self):
        usertoken_info=get_token(self.email)
        return usertoken_info[1]
    def user_waitingtime(self):
        usertoken_info=get_token(self.email)
        return usertoken_info[2]
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/userpagevalid', methods=['POST','GET'])
def userpagevalid():
    if request.method=='GET':
        email=session.get('email')
        name=session.get('name')
        password=session.get('password')
        data=user_forlogin(name,email,password)
        return render_template("userpage.html",data=data)
    elif request.method=='POST':
        ac_name=str()
        ac_pass=str()
        email=request.form.get("email")
        password=request.form.get("password")
        a=get_password(email)
        ac_name=a[0]
        ac_pass=a[1]
        customer=user_forlogin(ac_name,email,password)
        if ac_pass==password:
            session['email']=email
            session['name']=ac_name
            session['password']=ac_pass
            return render_template('userpage.html',data=customer)

@app.route('/sucesspage',methods=['POST'])
def sucesspage():
    new_name=request.form.get("name")
    new_email=request.form.get("email")
    session['email']=new_email
    session['name']=new_name
    new_password=request.form.get("password")
    session['password']=new_password
    new_confirmpassword=request.form.get("name")
    query = 'INSERT INTO user(email, name, password) VALUES (%s, %s,%s)'
    values = (new_email,new_name,new_password)
    cursor.execute(query,values)
    cnx.commit()
    customer=user_forlogin(new_name,new_email,new_password)
    return render_template('userpage.html',data=customer)

@app.route("/loadtoken",methods=['POST'])
def loadtoken():
    email=session.get('email')
    sio.emit('message', {'msg':email})
    name=session.get('name')
    password=session.get('password')
    data=user_forlogin(name,email,password)  
    return render_template('tokenpage.html',data=data)

@app.route("/userpage")
def userpage():
        return redirect(url_for("userpagevalid"))

if __name__=="__main__":
    sio.connect('http://localhost:5000')
    app.run(debug=True,port=8000)

