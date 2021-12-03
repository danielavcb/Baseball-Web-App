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

            cur = sql.connection.cursor()
            code = "SELECT * FROM login_info " \
                   "WHERE username = %s AND password = %s"

            # execute the sql code
            cur.execute(code, (user, password))

            global username
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

    # if the homepage button is clicked, redirect user to there
    cur1.execute("select concat(nameFirst, ' ', nameLast) as Name, concat(birthCity, ', ', birthState, ', ', birthCountry) as 'Birth Place', "
                 "case when deathYear = 0 then (2021 - birthYear) else (deathYear - birthYear) end as 'Age', case when b.AB > 0 then 'Y' else 'N' "
                 "end as 'Batter', case when NOT exists (select p.playerID from pitching p where p.playerID = b.playerID) then 'N' else 'Y' end as 'Pitcher' "
                 "from pitching p1, people p, batting b where b.playerID = p.playerID and b.yearID = 2020 and p1.yearID = b.yearID and b.teamID = (SELECT teamID "
                 "FROM teams WHERE name = (SELECT favorite FROM login_info WHERE username = %s) LIMIT 1) group by b.playerID", (username, ))


    if request.method == 'POST':
        if "year_change" in request.form:
            new_year = request.form["yearID"]

            cur1.execute("select concat(nameFirst, ' ', nameLast) as Name, concat(birthCity, ', ', birthState, ', ', birthCountry) as 'Birth Place', "
                        "case when deathYear = 0 then (2021 - birthYear) else (deathYear - birthYear) end as 'Age', case when b.AB > 0 then 'Y' else 'N' "
                        "end as 'Batter', case when NOT exists (select p.playerID from pitching p where p.playerID = b.playerID) then 'N' else 'Y' end as 'Pitcher' "
                        "from pitching p1, people p, batting b where b.playerID = p.playerID and b.yearID = %s and p1.yearID = b.yearID and b.teamID = (SELECT teamID "
                        "FROM teams WHERE name = (SELECT favorite FROM login_info WHERE username = %s) LIMIT 1) group by b.playerID",
                        (new_year, username, ))

        elif "fav_team" in request.form:
            team = request.form["change_team"]

            cur3 = sql.connection.cursor()

            # giving user the option to change favorite team
            cur3.execute("UPDATE login_info SET favorite = %s WHERE username = %s", (team, username, ))

            cur1.execute("select concat(nameFirst, ' ', nameLast) as Name, concat(birthCity, ', ', birthState, ', ', birthCountry) as 'Birth Place', "
                        "case when deathYear = 0 then (2021 - birthYear) else (deathYear - birthYear) end as 'Age', case when b.AB > 0 then 'Y' else 'N' "
                        "end as 'Batter', case when NOT exists (select p.playerID from pitching p where p.playerID = b.playerID) then 'N' else 'Y' end as 'Pitcher' "
                        "from pitching p1, people p, batting b where b.playerID = p.playerID and b.yearID = 2020 and p1.yearID = b.yearID and b.teamID = (SELECT teamID "
                        "FROM teams WHERE name = (SELECT favorite FROM login_info WHERE username = %s) LIMIT 1) group by b.playerID",
                        (username,))
        else:
            return redirect(url_for('homepage'))
    # committing these changes into the database
    sql.connection.commit()
    roster = cur1.fetchall()
    return render_template('profile.html', title='Profile', roster=roster)

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    print("here")
    return render_template('stats.html', title='Statistics')

# defining the homepage
@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    cur_al1 = sql.connection.cursor()
    cur_al2 = sql.connection.cursor()
    cur_al3 = sql.connection.cursor()

    cur_nl1 = sql.connection.cursor()
    cur_nl2 = sql.connection.cursor()
    cur_nl3 = sql.connection.cursor()

    winner = sql.connection.cursor()

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

    winner.execute("select round as Round, teamIDwinner as Winner, concat(wins,'-', losses) as '', teamIDloser as Loser, concat(losses, '-', wins) as '' "
                   "from seriespost where yearID = 2020 group by round")

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
        winner.execute("select round as Round, teamIDwinner as Winner, concat(wins,'-', losses) as '', teamIDloser as Loser, concat(losses, '-', wins) as '' "
                       "from seriespost where yearID = %s group by round", (yearID, ))

    data_al1 = cur_al1.fetchall()
    data_al2 = cur_al2.fetchall()
    data_al3 = cur_al3.fetchall()

    data_nl1 = cur_nl1.fetchall()
    data_nl2 = cur_nl2.fetchall()
    data_nl3 = cur_nl3.fetchall()

    data_winner = winner.fetchall()

    return render_template('homepage.html', title='Homepage', al1 = data_al1, al2 = data_al2, al3 = data_al3,
                           nl1 = data_nl1, nl2 = data_nl2, nl3 = data_nl3, win = data_winner)