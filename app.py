from flask import Flask, render_template, request, redirect, url_for, g
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table, Col
from flask_login import LoginManager

data = SQLAlchemy()
app = Flask(__name__)

# configuration for the database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'designerds'

sql = MySQL(app)

# # login configuration
# login_manager = LoginManager()
# login_manager.init_app(app)

# PAGE RUN
if __name__ == '__main__':
    app.run(debug=True)

username = ' '
# asking for user to input the username and password
@app.route('/', methods=['GET', 'POST'])
def requesting():
    if request.method == 'POST':
        # if both fields are filled up
        if 'username' in request.form and 'password' in request.form:
            # then, check the username and password from the database
            user = request.form['username']
            password = request.form['password']

            global username
            username = (user)

            cur = sql.connection.cursor()
            code = "SELECT * FROM login_info " \
                   "WHERE username = %s AND password = %s"
            # execute the sql code
            cur.execute(code, (user, password))

            # select row that matches the username and password
            sel = cur.fetchone()

            username = sel[1]

            # if a row is returned, go to user's profile
            if sel is not None:
                if sel[1] == user and sel[2] == password:
                    return redirect(url_for('profile'))
            # otherwise, request the username and password again
            else:
                return redirect(url_for('requesting'))
    # rendering the login page
    return render_template('login.html', title='Login')


# defining the registration page
@app.route('/register', methods=['GET', 'POST'])
def reg():
    # asking for username and password to register
    if request.method == 'POST':
        user = request.form["username"]
        password = request.form["password"]
        fav_team = request.form["fav_team"]

        cur = sql.connection.cursor()
        # inserting username and password into login database
        cur.execute("INSERT INTO login_info(username, password, favorite) VALUES(%s,%s,%s)", (user, password, fav_team))

        # committing these changes into the database
        sql.connection.commit()
        cur.close()

        return redirect(url_for('requesting'))
    return render_template('register.html', title='Create Account', msg="Account was created!")


# defining the user's profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    cur1 = sql.connection.cursor()

    # # if the homepage button is clicked, redirect user to there
    # cur1.execute("select concat(nameFirst, ' ', nameLast) as Name, abs(coalesce(deathYear, 2021) - birthYear)"\
    # "as Age, concat(birthCity, ', ', birthState, ', ', birthCountry) as 'Birth Place', case when b.AB > 0 then 'Y' else 'N' end as 'Batter', case when NOT exists (select p.playerID from pitching p where p.playerID = b.playerID)"\
    # "then 'N' else 'Y' end as 'Pitcher' from pitching p1, people p, batting b where b.playerID = p.playerID and b.yearID = 2020"\
    # "and p1.yearID = b.yearID and b.name = (SELECT name FROM teams WHERE name = (SELECT favorite FROM login_info WHERE username = %s ))"\
    # "group by b.playerID", (username, ))

    # cur1.execute("select concat(nameFirst, ' ', nameLast) as Name, abs(coalesce(deathYear, 2021) - birthYear) as Age, concat(birthCity, ', ', birthState, ', ', birthCountry) as 'Birth Place', case when b.AB > 0 then 'Y' else 'N' end as 'Batter', case when NOT exists (select p.playerID from pitching p where p.playerID = b.playerID) then 'N' else 'Y' end as 'Pitcher' from pitching p1, people p, batting b where b.playerID = p.playerID and b.yearID = 2019 and p1.yearID = b.yearID and b.teamID = 'NYA' group by b.playerID")

    #roster = cur1.fetchall()

    if request.method == 'POST':
        team = request.form["change_team"]
        cur = sql.connection.cursor()

        # giving user the option to change favorite team
        cur.execute("UPDATE login_info SET favorite = %s WHERE username = %s", (team, username, ))

        # committing these changes into the database
        sql.connection.commit()
        cur.close()

        return redirect(url_for('homepage'))
    return render_template('profile.html', title='Profile')

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    print("here")
    return render_template('stats.html', title='Statistics')

# defining the homepage
@app.route('/homepage', methods=['GET', 'POST'])
def homepage():

    cur_al1_0 = sql.connection.cursor()

    cur_al1 = sql.connection.cursor()
    cur_al2 = sql.connection.cursor()
    cur_al3 = sql.connection.cursor()

    cur_nl1 = sql.connection.cursor()
    cur_nl2 = sql.connection.cursor()
    cur_nl3 = sql.connection.cursor()

    cur_al1.execute("select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'E' " \
                    "and t0.teamID = (SELECT teamID from teams WHERE yearID = 2020 AND divID = 'E' ORDER BY (W/G) DESC LIMIT 1)" \
                    "and t1.yearID = 2020 and t0.yearID = 2020 and t1.lgID = 'AL' order by GB asc")

    cur_al2.execute("select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'W' " \
                    "and t0.teamID = (SELECT teamID from teams WHERE yearID = 2020 AND divID = 'W' ORDER BY (W/G) DESC LIMIT 1)" \
                    "and t1.yearID = 2020 and t0.yearID = 2020 and t1.lgID = 'AL' order by GB asc")

    cur_al3.execute( "select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'C' " \
                     "and t0.teamID = (SELECT teamID from teams WHERE yearID = 2020 AND divID = 'C' ORDER BY (W/G) DESC LIMIT 1)" \
                     "and t1.yearID = 2020 and t0.yearID = 2020 and t1.lgID = 'AL' order by GB asc")

    cur_nl1.execute("select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'E' " \
                    "and t0.teamID = (SELECT teamID from teams WHERE yearID = 2020 AND divID = 'E' ORDER BY (W/G) DESC LIMIT 1)" \
                    "and t1.yearID = 2020 and t0.yearID = 2020 and t1.lgID = 'NL' order by GB asc")

    cur_nl2.execute("select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'W' " \
                    "and t0.teamID = (SELECT teamID from teams WHERE yearID = 2020 AND divID = 'W' ORDER BY (W/G) DESC LIMIT 1)" \
                    "and t1.yearID = 2020 and t0.yearID = 2020 and t1.lgID = 'NL' order by GB asc")

    cur_nl3.execute("select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'C' " \
                    "and t0.teamID = (SELECT teamID from teams WHERE yearID = 2020 AND divID = 'C' ORDER BY (W/G) DESC LIMIT 1)" \
                    "and t1.yearID = 2020 and t0.yearID = 2020 and t1.lgID = 'NL' order by GB asc")

    if request.method == 'POST':
        yearID = request.form["yearID"]

        cur_al1.execute("select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'E' " \
                        "and t0.teamID = (SELECT teamID from teams WHERE yearID = %s AND divID = 'E' ORDER BY (W/G) DESC LIMIT 1)" \
                        "and t1.yearID = %s and t0.yearID = %s and t1.lgID = 'AL' order by GB asc", (yearID, yearID, yearID, ))

        cur_al2.execute( "select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'W' " \
                         "and t0.teamID = (SELECT teamID from teams WHERE yearID = %s AND divID = 'W' ORDER BY (W/G) DESC LIMIT 1)" \
                         "and t1.yearID = %s and t0.yearID = %s and t1.lgID = 'AL' order by GB asc", (yearID, yearID, yearID,))

        cur_al3.execute("select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'C' " \
                        "and t0.teamID = (SELECT teamID from teams WHERE yearID = %s AND divID = 'C' ORDER BY (W/G) DESC LIMIT 1)" \
                        "and t1.yearID = %s and t0.yearID = %s and t1.lgID = 'AL' order by GB asc", (yearID, yearID, yearID,))

        cur_nl1.execute("select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'E' " \
                        "and t0.teamID = (SELECT teamID from teams WHERE yearID = %s AND divID = 'E' ORDER BY (W/G) DESC LIMIT 1)" \
                        "and t1.yearID = %s and t0.yearID = %s and t1.lgID = 'NL' order by GB asc", (yearID, yearID, yearID, ))

        cur_nl2.execute( "select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'W' " \
                         "and t0.teamID = (SELECT teamID from teams WHERE yearID = %s AND divID = 'W' ORDER BY (W/G) DESC LIMIT 1)" \
                         "and t1.yearID = %s and t0.yearID = %s and t1.lgID = 'NL' order by GB asc", (yearID, yearID, yearID,))

        cur_nl3.execute("select t1.teamID, concat(t1.W, '-', t1.l) as '', (((t0.W-t1.W)+(t1.L-t0.L))/2) as GB from teams t1 JOIN teams t0 USING (divID) where divID = 'C' " \
                        "and t0.teamID = (SELECT teamID from teams WHERE yearID = %s AND divID = 'C' ORDER BY (W/G) DESC LIMIT 1)" \
                        "and t1.yearID = %s and t0.yearID = %s and t1.lgID = 'NL' order by GB asc", (yearID, yearID, yearID,))

    data_al1 = cur_al1.fetchall()
    data_al2 = cur_al2.fetchall()
    data_al3 = cur_al3.fetchall()

    data_nl1 = cur_nl1.fetchall()
    data_nl2 = cur_nl2.fetchall()
    data_nl3 = cur_nl3.fetchall()

    return render_template('homepage.html', title='Homepage', al1 = data_al1, al2 = data_al2, al3 = data_al3,
                           nl1 = data_nl1, nl2 = data_nl2, nl3 = data_nl3)