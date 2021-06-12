import datetime
from dbutils import DB_NAME
from flask import Flask, render_template, request, send_file
import sqlite3
import json
import logging
import re

logging.basicConfig(
    filename='server.log', 
   #  encoding='utf-8', 
    level=logging.DEBUG,
    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'
)

app = Flask(__name__)

DB_NAME = 'server.db'
con = sqlite3.connect(DB_NAME)

def db_exec(sql, args=[]):
    cur = con.cursor()
    cur.execute(sql, args)
    con.commit()
    cur.close()

def error(msg):
    return json.dumps({
        'status': 'error',
        'message': msg
    })

def success(msg="ok"):
    return json.dumps({
        'status': 'success',
        'message': msg
    })

def exists_in_db(email):
    select_stmt = '''
    SELECT * FROM events WHERE email = (?);
    '''
    results = db_exec(select_stmt, [email])
    return results and len(results) != 0

def get_next_assignment():
    select_stmt = '''SELECT * FROM events'''
    results = db_exec(select_stmt)
    if not results:
        return 1
    else:
        if len(results) % 3 == 0:
            return int(results[-1][3]) + 1
        return int(results[-1][3])

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/api/assignment', methods=['POST'])
def handle_assignment():
    data = json.loads(request.data.decode())
    option = data['option']
    email = data['email']
    # return error('oh no'), 403

    # if option == 'first':
    #     if exists_in_db('email'):
    #         return error('''It looks like you've already donwloaded an assignment. If you need to redownloaded it, select the redownload option and try again.''')
    #     assignment_id = get_next_assignment()
    #     timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S%p')
    #     insert_stmt = '''
    #         INSERT INTO events (email, option, assignment_id, timestamp) VALUES (?, ?, ?, ?)
    #     '''
    #     db_exec(insert_stmt, [email, option, assignment_id, timestamp])
    #     return send_file('static/pdfs/assignment1.pdf',
    #                 attachment_filename='assignment.pdf',
    #                 as_attachment=True)


    # print(option, email)
    # return success()
    return send_file('static/pdfs/assignment1.pdf',
                    attachment_filename='assignment.pdf',
                    as_attachment=True)


# @app.route('/api/assignment', methods=['POST'])
# def handle_assignment():
 
#     try:
#         option = request.json['option']
#         email = request.json['email']
#     except Exception as e:
#         logging.error(f'missing/invalid request options data: {request.json}')
#         return error('missing/invalid request options')

#     if option == 'first':
#         if exists_in_db(email):
#             logging.error(f'email {email} already in db')
#             return error('''It looks like you've already donwloaded an assignment. If you need to redownloaded it, select the redownload option and try again.''')
        
#         assignment_id = get_next_assignment()
#         timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S%p')
#         insert_stmt = '''
#             INSERT INTO events (email, option, assignment_id, timestamp) VALUES (?, ?, ?, ?)
#         '''
#         db_exec(insert_stmt, [email, option, assignment_id, timestamp])
#         return send_file(f'static/pdfs/assignment1.pdf', mimetype='application/pdf')
#         # return first assignment not assigned three times
#     elif option == 'redownload':
#         # check if email already exists in db
#         # if not, ask to check 'first' option
#         # otherwise return last assignment linked to this email
#         pass
#     elif option == 'returning':
#         # check if email already exists in db
#         # if not, ask to check 'first' option
#         # otherwise return first assignment not assigned three times and not assigned to this email
#         pass
#     else:
#         return error('invalid option')

#     return success()


@app.route('/', methods=['POST'])
def process_data():
    print(request.form['netid'])
    netid = request.form['netid']
    global current_assignment
    if netid not in visited:
        visited.add(netid)
    if (len(visited) - 1) % 3 == 0:
        current_assignment = (current_assignment + 1) % total_assignments

    return send_file(f'static/pdfs/assignment{current_assignment}.pdf',
                     attachment_filename=f'assignment{current_assignment}.pdf',
                     as_attachment=True)

@app.route('/downloadAssignment', methods=['GET'])
def download_assignment():
    return send_file('static/pdfs/assignment1.pdf',
                     attachment_filename='assignment.pdf',
                     as_attachment=True)

@app.route('/downloadNewAssignment', methods=['GET'])
def download_new_assignment():

    ## logic...

    return send_file('static/pdfs/assignment.pdf',
                     attachment_filename='assignment.pdf',
                     as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
