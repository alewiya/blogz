from flask import Flask, request, redirect, render_template, session ,flash
from flask_sqlalchemy import SQLAlchemy
app= Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] =True
db = SQLAlchemy(app)

class Blog(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(120))
    body=db.Column(db.String(120))
    owner_id=db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,body,owner):

        self.title=title
        self.body=body
        self.owner=owner

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(120),unique=True)
    password=db.Column(db.String(120))
    blogs=db.relationship('Blog', backref='owner')

    def __init__(self,username,password):

        self.username=username
        self.password=password
    def __repr__(self):
        return self.username

@app.before_request
def required_login():
    permited_routes=['login','signup','blog','index']
    if request.endpoint not in permited_routes and 'username' not in session:
        return redirect('/login')
@app.route('/login',methods=['POST','GET'])
def login():
    name_error=''
    password_error=''

    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        if int(len(username)) <= 0 :
            name_error="That's not a valid username"
        elif int(len(username)) < 3 or int(len(username)) > 20 or " " in username :
            name_error = "That's not a valid username"
        if int(len(password)) <= 0:
            password_error="That's not a valid password"
            password=''
        elif int(len(password)) < 3 or int(len(password)) > 20:
            password_error="That's not a valid password"
            password=''
        if not name_error and not password_error:
            user=User.query.filter_by(username=username).first()
            if user and user.password == password:
                session['username']=username
                flash('welcome back You logged in')
            return redirect('/newpost')
        else:
            return render_template('login.html',name_error=name_error, password_error=password_error)
    return render_template('login.html',name_error=name_error, password_error=password_error)
@app.route('/signup', methods=['POST','GET'])
def signup():
    name_error=''
    password_error=''
    verify_error=''
    username=''
    password=''
    verify=''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if username == '':
            name_error="That's not a valid username"
            username=''
        elif int(len(username)) < 3 or int(len(username)) > 20 or " " in username :
            name_error = "That's not a valid username"
            username=''
        if password == '':
            password_error="That's not a valid password"
            password =''
        elif int(len(password)) < 3 or int(len(password)) > 20:
            password_error="That's not a valid password"
            password=''
        if verify != password:
            verify_error="passowrd do not match"
            verify=''
        if not name_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = new_user.username
                flash('You Signup')
                return redirect('/newpost')
            else:
                flash('username already exists')
            return redirect('/login')   
        else:
            return render_template('signup.html' , name_error=name_error, password_error=password_error, 
            verify_error=verify_error ,username=username)
    return render_template('signup.html')
@app.route('/newpost', methods=['POST','GET'])
def add_post():
    error_title=''
    error_body=''
    if request.method =='POST':
        post_title=request.form['title']
        post_blog=request.form['new-blog']
        
        if post_title == "":
            error_title='Please insert the title of your new post'
        if post_blog == "":
            error_body='Please insert the body of  your new post'
        if not error_title and not error_body: 
            owner=User.query.filter_by(username=session['username']).first()
            new_blog=Blog(post_title,post_blog,owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/get-id?id={}".format(new_blog.id))

        else:
            return render_template('newpost.html', error_title=error_title, error_body=error_body)
    else:
        return render_template('newpost.html')
@app.route('/blog')
def blog():
    owner_name= request.args.get('owner')
    username=User.query.filter_by(username=owner_name).first()
    if username:
        blogs=Blog.query.filter_by(owner=username).all()
        return render_template('blog.html',posts=blogs)
    blog_posts=  Blog.query.all()
    return render_template('blog.html',blog_posts=blog_posts)
# #create different app route to redirect to /blog?id={id} to display get-id.html template
@app.route('/get-id')
def display_post():
    if request.args.get('id'): 
        blog_id=request.args.get('id')
        blog_posts=Blog.query.filter_by(id=blog_id).first()
    return render_template('get-id.html',post=blog_posts)
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')   
@app.route('/')
def index():
    users=User.query.all()
    return render_template('index.html',users=users)
app.secret_key = 'y337kGcys&zP3B'
if __name__=='__main__':
    app.run()