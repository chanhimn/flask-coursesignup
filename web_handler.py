from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
db_filename = "coursesignup.db"

@app.route('/')
def index():
    db = sqlite3.connect(db_filename)
    results = db.execute("SELECT Courses.Id, Courses.CourseName, Courses.CourseQuota FROM Courses").fetchall()
    records = []
    for result in results:
        num_signup = db.execute("SELECT COUNT (*) FROM SignUps WHERE Id = ?", (result[0],)).fetchone()[0]
        record = []
        record.extend(result)
        record.append(num_signup)
        records.append(record)
    db.close()
    return render_template('index.html', records = records)

@app.route('/new_course', methods = ['GET', 'POST'])
def new_course():
    if request.method == 'POST':
        db = sqlite3.connect(db_filename)
        db.execute("INSERT INTO Courses(CourseName, CourseQuota) VALUES (?, ?)", (request.form['course_name'], request.form['course_quota']))
        db.commit()
        db.close()
        return redirect(url_for('index'))
    else:
        return render_template('new_course.html')

@app.route('/display_participants/<string:rid>', methods = ["GET", "POST"])
def display_participants(rid):
    db = sqlite3.connect(db_filename)
    course_name = db.execute("SELECT Courses.CourseName FROM Courses WHERE Courses.Id = ?", (rid,)).fetchall()[0][0]       
    records = db.execute("SELECT ParticipantId, Email FROM SignUps WHERE Id = ?", (rid,)).fetchall()
    html = render_template('display_participants.html', course_name=course_name, records=records)
    return html


@app.route('/sign_up/<string:rid>', methods = ["GET", "POST"])
def sign_up(rid):
    if request.method == 'GET':
        db = sqlite3.connect(db_filename)
        records = db.execute("SELECT Id, CourseName, CourseQuota FROM Courses WHERE Id = ?", (rid,)).fetchall()
        print(records)
        if len(records) == 1:
            html = render_template('sign_up.html', rid=rid, records=records)
        else:
            html = "No such Course Id."
        db.close()
    else:
        print(request.form['rid'], request.form['course_name'], request.form['email'])
        db = sqlite3.connect(db_filename)
        records = db.execute("SELECT Courses.CourseQuota FROM Courses WHERE Courses.Id = ?", (rid,)).fetchall()
        num_signups = db.execute("SELECT COUNT (*) FROM SignUps WHERE Id = ?", (rid,)).fetchone()[0]
        
        if num_signups < records[0][0]:
            db.execute("INSERT INTO SignUps(Email, Id, ParticipantId) VALUES (?, ?, ?)", (request.form['email'], request.form['rid'], num_signups+1))
            db.commit()
            html = redirect(url_for('index'))
        else:
            html = render_template('course_full.html')
        db.close()
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    #app.run(debug=True)
