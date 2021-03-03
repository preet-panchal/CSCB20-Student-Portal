from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app = Flask(__name__)
app.secret_key='patel'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'
db = SQLAlchemy(app)

def get_user_type():
	# this function returns a string 'student' or 'instructor' 
	# depending on who the session belongs to
	usertype = """
		SELECT *
		FROM users
		where username='{}'""".format(session['username'])
	user_type_result = db.engine.execute(text(usertype))
	for row in user_type_result:
		ut = row.user_type
	return ut

def get_firstname(username):
	# this function takes in a username and returns the first_name associated to that username in the database
	sql = """
		SELECT *
		FROM users
		where username='%s'"""%(username)
	results = db.engine.execute(text(sql))
	for row in results:
		first_name=row.first_name
	return first_name

@app.route('/',methods=['GET','POST'])
@app.route('/login',methods=['GET','POST'])
def login():
	#print request.headers.get('User-Agent') # dont know what this line does.. it was in Abbas' file
	if request.method=='POST':
		sql = """
			SELECT *
			FROM users
			"""
		results = db.engine.execute(text(sql))
		for result in results:
			if result['username'].lower()==request.form['username'].lower():     # check if the entered username and password exists in database
				if result['password']==request.form['password']:
					session['username']=request.form['username'].lower()
					return redirect(url_for('index'))
		error='Invalid credentials'
		return render_template('login.html',error=error)
	elif 'username' in session:
		return render_template('index.html',ut=get_user_type())
	elif request.method=="GET":
		error=request.args.get('error')
		return render_template('login.html',error=error)
	else:
		return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
	if request.method=='POST':
		sql = """
			SELECT *
			FROM users
			"""
		results = db.engine.execute(text(sql))    # now check if username already exists
		for result in results:
			if result['username'].lower()==request.form['username'].lower():   
				error='Username already exists'
				return render_template('register.html',error=error)
		# now we know username doesnt exists
		# now we need to enter the data into the database
		sql = """
			INSERT 
			INTO users (username,password,email,first_name,user_type) 
			VALUES ('%s','%s','%s','%s','%s')
			"""%(request.form['username'].lower(),request.form['password'],request.form['email'],request.form['first_name'],request.form['user_type'])
		db.engine.execute(text(sql))
		
		# if the registration was for student then we need to create a row for that user
		# in the marks table
		if request.form['user_type']=="student":
			sql = """
				INSERT 
				INTO marks (username) 
				VALUES ('%s')
				"""%(request.form['username'].lower())
			db.engine.execute(text(sql))
		error='Registration successfull'
		# return render_template('register.html',error=error)
		return redirect(url_for('login',error=error))
	elif 'username' in session:
		return render_template('index.html',ut=get_user_type())		
	else:
		return render_template('register.html')
	
@app.route('/logout')
def logout():
	error=session['username']+" has been successfully logged out"
	session.pop('username', None)
	return redirect(url_for('login',error=error))
	
@app.route('/grades',methods=['GET','POST'])	
def grades():
	if request.method=='POST':
		#*** If an instructor updated the marks then store the new 
		# marks in the database
		if get_user_type() == 'instructor':
			sql = """
				SELECT *
				FROM users
				WHERE user_type = 'student'
				"""
			results = db.engine.execute(text(sql))   
			sqls = []
			for result in results:
				sqls.append("""update marks
					set q1={}, q2={},q3={},q4={},a1={},a2={},a3={},midterm={},final={},practical={}
					where username='{}'""".format(int(request.form[result.username+'_q1']),int(request.form[result.username+'_q2']),int(request.form[result.username+'_q3']),
						int(request.form[result.username+'_q4']),int(request.form[result.username+'_a1']),int(request.form[result.username+'_a2']),int(request.form[result.username+'_a3']),
						int(request.form[result.username+'_midterm']),int(request.form[result.username+'_final']),int(request.form[result.username+'_practical']),result.username))
			for each_query in sqls:
				db.engine.execute(text(each_query))

			return update_gradespage()
			
		# if a student did a post requesnt then its for the remark request
		# take the request and store it in the database
		elif get_user_type() == 'student':
			sql = """
				INSERT 
				INTO remark_req (username,assessment_name,explaination) 
				VALUES ('%s','%s','%s')
				"""%(session['username'],request.form['ins_username'],request.form['msg1'])
			db.engine.execute(text(sql))
			return update_gradespage()
	elif 'username' in session:
		return update_gradespage()
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))

def update_gradespage():
	# if the session belongs to student then show only that student's marks with correct options for remark request
	if get_user_type() == "student":
		firstname = get_firstname(session['username'])
		test_categories_sql = """SELECT * FROM Assessment_names"""
		test_categories = db.engine.execute(text(test_categories_sql))
		sql = """
			SELECT *
			FROM marks
			where username='{}'""".format(session['username'])
		results = db.engine.execute(text(sql))
		return render_template('grades.html',data=results,ut=get_user_type(), test_categories=test_categories, firstname=firstname)
	# if the session belongs to instructor then show everyone's marks
	else:
		sql = """
			SELECT *
			FROM marks
			"""
		results = db.engine.execute(text(sql))
		return render_template('grades.html',data=results,ut=get_user_type())
		
@app.route('/feedback',methods=['GET','POST'])	
def feedback():
	# if a student posted a feedback then store it in the database
	if request.method=='POST':
		sql = """
			INSERT 
			INTO feedback (username,que1,que2,que3,que4) 
			VALUES ('%s','%s','%s','%s','%s')
			"""%(request.form['ins_username'],request.form['msg1'],request.form['msg2'],request.form['msg3'],request.form['msg4'])
		db.engine.execute(text(sql))
		sql = """
				SELECT *
				FROM users
				where user_type='instructor'"""
		notice = "Your feedback has been sent to '%s'"%(get_firstname(request.form['ins_username']))
		results = db.engine.execute(text(sql))
		return render_template('feedback.html',data=results, notice=notice,ut=get_user_type())
	elif 'username' in session:
		# if session belongs to student then get all instructor's usernames from database to give the options in dropdown 
		if get_user_type() == 'student':
			sql = """
					SELECT *
					FROM users
					where user_type='instructor'"""
			results = db.engine.execute(text(sql))
			return render_template('feedback.html',data=results,ut=get_user_type())
		# if session belongs to instructor then show all their feedback to them
		else:
			sql = """
					SELECT *
					FROM feedback
					where username='{}'""".format(session['username'])
			results = db.engine.execute(text(sql))
			return render_template('feedback.html',ins_feedbacks=results,ut=get_user_type())
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))

@app.route('/remark_req',methods=['GET','POST'])	
def remark_req():
	# import all remark requests from the database as show it to the instructor
	if 'username' in session:
		sql = """SELECT * FROM remark_req"""
		remarks = db.engine.execute(text(sql))
		return render_template('remark_req.html',remarks=remarks,ut=get_user_type())
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))

@app.route('/index')	
def index():
	if 'username' in session:
		firstname = get_firstname(session['username'])
		return render_template('index.html',ut=get_user_type(),firstname=firstname)
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))

@app.route('/announcements')	
def announcements():
	if 'username' in session:
		return render_template('announcements.html',ut=get_user_type())
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))
		
@app.route('/calendar')	
def calendar():
	if 'username' in session:
		return render_template('calendar.html',ut=get_user_type())
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))
		
@app.route('/lectures')	
def lectures():
	if 'username' in session:
		return render_template('lectures.html',ut=get_user_type())
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))

@app.route('/assignments')	
def assignments():
	if 'username' in session:
		return render_template('assignments.html',ut=get_user_type())
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))

@app.route('/exams')	
def exams():
	if 'username' in session:
		return render_template('exams.html',ut=get_user_type())
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))
		
@app.route('/resources')	
def resources():
	if 'username' in session:
		return render_template('resources.html',ut=get_user_type())
	else:
		error='You are not logged in'
		return redirect(url_for('login',error=error))
		

if __name__=="__main__":
	app.run(debug=True,host='0.0.0.0')