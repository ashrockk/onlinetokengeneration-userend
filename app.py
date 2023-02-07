from flask import Flask, render_template,request,json,redirect,session
import socketio
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
    def get_name(self):
        return self.name
    def get_email(self):
        return self.email()
    def notify(self):
        if check_avalailability()==1:
            return 1
        else: 
            return 0
    def checktokenonetime_request(self):
        tokenid=str()
        query="Select tokenid from tokendata where email=%s"
        values=(self.email)
        cursor.execute(query,(values,))
        access_pass=cursor.fetchall()
        for i in access_pass:
            tokenid=access_pass[0]
        if check_onetimetokenrequest(self.email)==1:
            return f"your token is:{tokenid}"
        else:
            return "you havenot taken any token:"
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/userpagevalid', methods=['POST'])
def userpagevalid():
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
        return render_template('userpage.html',data=customer)
    else:
        return "sry"

@app.route('/sucesspage',methods=['POST'])
def sucesspage():
    new_name=request.form.get("name")
    new_email=request.form.get("email")
    session['email']=new_email
    new_password=request.form.get("password")
    new_confirmpassword=request.form.get("name")
    query = 'INSERT INTO user (email, name, password) VALUES (%s, %s,%s)'
    values = (new_email,new_name,new_password)
    cursor.execute(query,values)
    cnx.commit()
    customer=user_forlogin(new_name,new_email,new_password)
    return render_template('userpage.html',data=customer)

@app.route("/loadtoken",methods=['POST','GET'])
def loadtoken():
    email=session.get('email')
    sio.emit('message', {'msg':email})
    if request.method=='POST':
        if request.form.get('action1')=='Get Token':
            data={'msg':"hibro"}
            return "sucess:"
        else:
            return "25%"
    elif request.method =='GET':
        if check_onetimetokenrequest(email)==0:
            tokenid=get_token(email)
            data={'msg1':tokenid}
        else:
            data={'msg1':"you have already taken token:"}
        return render_template("tokenpage.html",data=data)

@app.route('/tokenpage',methods=['POST'])
def tokenpage():
    email=session.get('email')
    if check_onetimetokenrequest():
        if check_avalailability():
            # a=get_token(email)
            data={'msg':"hi"}
            return render_template("userpage.html",data=data)
        else :
            data={'email':'"sry token not found:"'}
            return render_template("userpage.html",data=data)
    else:
        return render_template("userpage.html",data='sry you have already taken token:')

if __name__=="__main__":
    sio.connect('http://localhost:5000')
    app.run(debug=True,port=8000)

