from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.debug = False

@app.route('/')
def index():
    db = sqlite3.connect('queuester.db')
    results = db.execute("SELECT Queues.Id, Queues.QueueName, Queues.CurrentQueueNumber FROM Queues").fetchall()
    records = []
    for result in results:
        curnum = db.execute("SELECT COUNT (*) FROM QueueNumber WHERE Id = ?", (result[0],)).fetchone()[0]
        record = []
        record.extend(result)
        record.append(curnum)
        records.append(record)
    db.close()
    return render_template('index.html', records = records)

@app.route('/new_queue', methods = ['GET', 'POST'])
def new_queue():
    if request.method == 'POST':
        db = sqlite3.connect('queuester.db')
        db.execute("INSERT INTO Queues(QueueName, CurrentQueueNumber) VALUES (?, ?)", (request.form['queue_name'], request.form['current_queue_number']))
        db.commit()
        db.close()
        return redirect(url_for('index'))
    else:
        return render_template('new_queue.html')

@app.route('/display_queue/<string:rid>', methods = ["GET", "POST"])
def display_queue(rid):
    db = sqlite3.connect('queuester.db')
    queue_name = db.execute("SELECT Queues.QueueName FROM Queues WHERE Queues.Id = ?", (rid,)).fetchall()[0][0]       
    records = db.execute("SELECT QueueNumber, Email FROM QueueNumber WHERE Id = ?", (rid,)).fetchall()
    html = render_template('display_queue.html', queue_name=queue_name, records=records)
    return html


@app.route('/get_queue_number/<string:rid>', methods = ["GET", "POST"])
def get_queue_number(rid):
    if request.method == 'GET':
        db = sqlite3.connect('queuester.db')
        records = db.execute("SELECT Id, QueueName, CurrentQueueNumber FROM Queues WHERE Id = ?", (rid,)).fetchall()
        print(records)
        if len(records) == 1:
            html = render_template('get_queue_number.html', rid=rid, records=records)
        else:
            html = "No such Queue Id."
        db.close()
    else:
        print(request.form['rid'], request.form['queue_name'], request.form['email'])
        db = sqlite3.connect('queuester.db')
        records = db.execute("SELECT Queues.CurrentQueueNumber FROM Queues WHERE Queues.Id = ?", (rid,)).fetchall()
        curnum = db.execute("SELECT COUNT (*) FROM QueueNumber WHERE Id = ?", (rid,)).fetchone()[0]
        
        if curnum < records[0][0]:
            db.execute("INSERT INTO QueueNumber(Email, Id, QueueNumber) VALUES (?, ?, ?)", (request.form['email'], request.form['rid'], curnum+1))
            db.commit()
            html = redirect(url_for('index'))
        else:
            html = render_template('course_full.html')
        db.close()
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
