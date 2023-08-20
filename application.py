
# importing necessary modules
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import mysql.connector

# connecting to database
db = mysql.connector.connect(host="agalyadb.cuuatoz5ywpt.ap-southeast-2.rds.amazonaws.com",user="agalyadb",password="20agalya05",database="todo")

# creating cursor object
cursor = db.cursor()

# creating flask instance
application = app = Flask(__name__)

# setting secret key
app.secret_key = "cairocoders-ednalan"

user_id = 0

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

# registering with new user
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # process form data
            mailid = request.form['email']
            password = request.form['psw']
            # save the user to the database
            cursor.execute('INSERT INTO users(mailid,password) VALUES(%s,%s)',(mailid,password))
            # commit changes
            db.commit()
            # message flashing to the user
            flash('REGISTRATION SUCCESSFUL')
            return redirect(url_for('login'))
        # handling the exception
        except Exception as e:
            print("unexpected error : ",e)
            flash('Your Mail is already registered please select Login option ')
            # redirect to same page if error occurs
            return redirect(url_for('signup'))
    return render_template('signup.html')

# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # process the form data
        name = request.form['email']
        password = request.form['password']
        # checking if the user exists int he database
        cursor.execute('SELECT * FROM todo.users  WHERE mailid=%s AND password=%s',(name,password))
        r=cursor.fetchall()
        session.pop('user',None)
        if len(r)==1:
            # fetching user id
            session['user'] = r[0][2]
            user_id = r[0][2]
            # if user exists, login and redirect to index page
            return redirect(url_for('index',user_id=user_id))
        else:
            # flashing login failed message to the user
            flash('LOGIN FAILED PLEASE CHECK YOUR CREDENTIALS')
            # redirect to same page
            return redirect(url_for('login'))
    return render_template('login.html')

# index page to do CRUD operations
@app.route('/index/<user_id>')
def index(user_id):
    if g.user:
    # fetching tasks stored by particular user
        s = "SELECT * FROM task WHERE user_id = " + user_id + " ORDER BY date_time DESC"
        cursor.execute(s) # Execute the SQL
        list_tasks = cursor.fetchall()
        return render_template('index.html', list_tasks = list_tasks,u_id=user_id)
    return render_template('login.html')

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/dropsession')
def dropsession():
    session.pop('user',None)
    return render_template('login.html')
 

 # adding task to the database
@app.route('/add_task/<user_id>', methods=['POST','GET'])
def add_task(user_id):
    if request.method == 'POST':
        # process form data
        task_desc = request.form['task_desc']
        date_time = request.form['date_time']
        # inserting the task to the database by SQL command
        cursor.execute("INSERT INTO task (user_id, task_desc,date_time) VALUES (%s,%s,%s)", (user_id,task_desc,date_time))
        db.commit()
        # flashing task added message to the user 
        flash('Task Added successfully')
        return redirect(url_for('index',user_id=user_id))


# editing the task details
@app.route('/edit/<id>/<user_id>', methods = ['POST', 'GET'])
def get_task(id,user_id):
    if g.user:
        # fetching the particular task using task id
        cursor.execute('SELECT * FROM task WHERE task_id = %s', (id,))
        data = cursor.fetchall()
        print(data[0])
        # redirect to edit page to edit the task already added
        return render_template('edit.html', taskk = data[0],user_id=user_id)
    return render_template('login.html')


#updating the changes made to the task
@app.route('/update/<id>/<user_id>', methods=['POST'])
def update_task(id,user_id):
    if request.method == 'POST':
        # process the edited task details
        task_desc = request.form['task_desc']
        date_time= request.form['date_time']
        # updating the changes to the database
        cursor.execute('UPDATE task SET task_desc =%s,date_time =%s,status="processing" WHERE task_id =%s',(task_desc,date_time,id))
        flash('Task Updated Successfully')
        db.commit()
        # redirect to the index page
        return redirect(url_for('index',user_id=user_id))

#deleting the task
@app.route('/delete/<string:id>/<user_id>', methods = ['POST','GET'])
def delete_task(id,user_id):
    # fetching particular task to be deleted
    cursor.execute('DELETE FROM task WHERE task_id = {0}'.format(id))
    db.commit()
    # flash deleting message to the user
    flash('Task Removed Successfully')
    return redirect(url_for('index',user_id=user_id))


if __name__ == "__main__":
    app.run(debug=True)

