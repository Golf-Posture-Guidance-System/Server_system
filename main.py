import flask
import mysql.connector
import sys
import json

app = flask.Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def chat():
    msg_received = flask.request.get_json()
    msg_subject = msg_received["subject"]

    if msg_subject == "register":
        return register(msg_received)
    elif msg_subject == "login":
        return login(msg_received)
    else:
        return "Invalid request."

def register(msg_received):
    id = msg_received["userid"]
    password = msg_received["userpwd"]
    username = msg_received["username"]
    email = msg_received["useremail"]

    select_query = "SELECT * FROM users where name = " + "'" + id + "'"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()
    if len(records) != 0:
        return "Another user used the username. Please chose another username."

    insert_query = "INSERT INTO users (id, psw, name, email) VALUES (%s, MD5(%s), %s, %s)"
    insert_values = (id, password, username, email)
    try:
        db_cursor.execute(insert_query, insert_values)
        chat_db.commit()
        return "success"
    except Exception as e:
        print("Error while inserting the new record :", repr(e))
        return "failure"

def login(msg_received):
    username = msg_received["userid"]
    password = msg_received["userpwd"]
    select_query = "SELECT name FROM users where id = " + "'" + username + "' and psw = " + "MD5('" + password + "')"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()

    if len(records) == 0:
        return "failure"
    else:
        return "success"
try:
    chat_db = mysql.connector.connect(host="golfdb.chx469ppubzv.ap-northeast-2.rds.amazonaws.com",
                                      user="jaewon", passwd="jl42474247", database="Golfuser")
except:
    sys.exit("Error connecting to the database. Please check your inputs.")
db_cursor = chat_db.cursor()

app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
