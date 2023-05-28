from flask import Flask, render_template, g, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "mysecretkey"


def connect_db():
    sql = sqlite3.connect(
        'D:\Programming\Flask_udemy\FOOD_TRACKER\databases\data.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite3_db'):
        g.sqlite_db.close()


@app.route("/", methods=['GET', 'POST'])
def home():
    db = get_db()
    if request.method == 'POST':
        # asumming the date is in YYYY-MM-DD Format , yes i've checked it
        date = request.form.get('new-day')
        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')
        db.execute('insert into log_date(entry_date) values (?)',
                   [database_date])
        db.commit()
    cur = db.execute(
        'select entry_date from log_date order by entry_date desc '
    )
    results = cur.fetchall()

    # setelah mendapatkan hasil, kita rapihkan formatnya menjadi yg kita inginkan.
    pretty_results = []

    for i in results:
        single_date = {}
        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
        single_date['entry_date'] = datetime.strftime(d, '%d %B %Y')
        pretty_results.append(single_date)
    return render_template('home.html', dates=pretty_results)


# date is going to be the standard format 20230519 or the database_date
# @app.route('/view', defaults={'date': None})
@app.route('/view/<int:date>', methods=['GET', 'POST'])
def view(date):
    if request.method == 'POST':
        return f"<h1>Your request is {request.form.get('food-select')}</h1>"
    db = get_db()
    cur = db.execute(
        'SELECT entry_date FROM log_date WHERE entry_date = ?', [date])
    result = cur.fetchone()

    d = datetime.strptime(str(result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%d %B %Y')

    food_cursor = db.execute("select id, name from food order by name")
    food_results = food_cursor.fetchall()

    return render_template('day.html', dates=pretty_date, food_results=food_results)


@app.route("/food", methods=['GET', 'POST'])
def food():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('food-name')
        protein = int(request.form.get('protein'))
        carbohydrates = int(request.form.get('carbohydrates'))
        fat = int(request.form.get('fat'))

        calories = protein * 4 + carbohydrates * 4 + fat * 9

        db.execute(
            'insert into food (name, protein, carbohydrates, fat, calories) values (?,?,?,?,?)', [name, protein, carbohydrates, fat, calories])
        db.commit()

    cur = db.execute(
        ' select name, protein, carbohydrates, fat, calories from food')
    results = cur.fetchall()
    return render_template('add_food.html', results=results)


if __name__ == "__main__":
    app.run()
