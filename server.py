#!/usr/bin/env python2.7

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



DATABASEURI = "postgresql://zel2109:testpass4111@104.196.18.7/w4111"


engine = create_engine(DATABASEURI)


engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")


engine.execute("""INSERT INTO test(name) VALUES ('morningside heights');""")



# another table for another page
engine.execute("""DROP TABLE IF EXISTS usertest;""")
engine.execute("""CREATE TABLE IF NOT EXISTS usertest (
  id serial,
  name text
);""")


engine.execute("""INSERT INTO usertest(name) VALUES ('@ReallyCoolKids'),('annaqin'),('zionlin'),('happylion'),('HakunaMatata');""")


@app.before_request
def before_request():
  
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  
  try:
    g.conn.close()
  except Exception as e:
    pass



@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """


  print request.args


 # display the location parking space available 
  # result is a dictionary called names 
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

 # context = dict(data = names)

###get the newly added location to db test, display associated parking info 

  cursor = g.conn.execute("SELECT * FROM listing WHERE location = (SELECT name FROM test WHERE id >= ALL(SELECT id FROM test))")
  
  listof = []
  for result in cursor:
    listof.append(result[0])  # can also be accessed using result[0]
    listof.append(result[1])
    listof.append(result[2])
    listof.append(result[3])
  cursor.close()

  context = dict(data = listof)

  return render_template("index.html", **context)


## this other page is about user info 
@app.route('/another')
def another():
  
  
 # add yourself to the user list
  # result is a dictionary called users
  cursor = g.conn.execute("SELECT name FROM usertest")
  driver = []
  for result in cursor:
    driver.append(result[0])  # display selected column
  cursor.close()

  context2 = dict(userinfo = driver)


  return render_template("another.html", **context2)


@app.route('/searchPlace', methods=['POST'])
def searchPlace():
  name = request.form['name']
  print name
  cmd = 'INSERT INTO test(name) VALUES (:name1)';
  g.conn.execute(text(cmd), name1 = name);
  return redirect('/')


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print name
  cmd = 'INSERT INTO usertest(name) VALUES (:name1)';
  g.conn.execute(text(cmd), name1 = name);
  return redirect('/')



@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
 name = request.form['name']
 print name 
 g.conn.execute("DELETE FROM usertest WHERE name= '%s'" %(name))
 return redirect('/')


###############



@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
