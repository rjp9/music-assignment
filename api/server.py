import datetime
from dbutils import DB_NAME
from flask import Flask, render_template, request, send_file
import sqlite3 as sql
import json
import logging
from werkzeug.utils import redirect, secure_filename
import os

TOTAL_ASSIGNMENTS = 32
ANNOTATORS_PER_ASSIGNMENT = 3
DB_NAME = 'server.db'
UPLOAD_DIR = 'uploaded/'

app = Flask(__name__)


# ==================
# Logging 
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler('server.log'))

def log(msg):
    logger.debug(f'{timestamp()} {msg}')
# =================


# =================
# General stuff
def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
# =================

# ================
# DB stuff
def exec(sql_stmt, args=[]):
    with sql.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute(sql_stmt, args)
        con.commit()
        results = cur.fetchall()
        return results if results else []

def exists_in_db(email):
    results = exec('SELECT * FROM events WHERE email = (?);', [email])
    return results and len(results) != 0

def create_event(email, option, id):
    exec('''INSERT INTO events (email, option, assignment_id, timestamp) 
            VALUES (?, ?, ?, ?);''', 
            [email, option, id, timestamp()])

def get_next_assignment(email):
    all_assignments = set([i+1 for i in range(TOTAL_ASSIGNMENTS)])
    log(f'all {all_assignments}')
    results = exec('''
                        SELECT assignment_id 
                        FROM events 
                        GROUP BY assignment_id
                        HAVING COUNT(assignment_id) >= (?);''',
                        [ANNOTATORS_PER_ASSIGNMENT])
    log(f'completed {results}')
    eligible_assignments = all_assignments.difference(*results)
    if not eligible_assignments:
        return 'all assignments completed'
    log(f'incomplete {eligible_assignments}')
    results = exec('SELECT assignment_id FROM events WHERE email = (?);', [email])
    log(f'assigned to {email} {results}')
    eligible_assignments = list(eligible_assignments.difference(*results))
    log(f'remaining {eligible_assignments}')
    if not eligible_assignments:
        return 'user has completed all assignments'
    log(f'assignment {eligible_assignments[0]}')
    return eligible_assignments[0]

# =====================




# ===================
# Flask stuff
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

def pdf(assignment_id):
    filename = f'assignment{assignment_id}.pdf'
    logger.info(f'dispatching {filename}')
    return send_file(f'static/pdfs/{filename}',
                attachment_filename=f'{filename}',
                as_attachment=True)

def get_folder(email):
    folder = UPLOAD_DIR + email
    os.makedirs(folder, exist_ok=True)
    return folder


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/success')
def success_route():
    return render_template('success.html')

@app.route('/thanks')
def thanks():
    return render_template('thanks.html') 

@app.route('/submit')
def submit():
    return render_template('upload.html')

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/api/upload', methods=['POST'])
def handle_submit_request():
    log('here')
    try:
        # univ = request.form['univ']
        # years = request.form['years']
        # inst = request.form['inst']
        # diff = request.form['diff']
        # feedback = request.form['feedback']
        # log([univ, years, inst, diff, feedback])


        email = request.form['email']
        pdf = request.files['pdf']
        log(f'**processing email {email} upload')
        if pdf:
            filename = secure_filename(pdf.filename)
            if filename and filename.split('.')[-1] == 'pdf':
                folder = get_folder(email) # this could be really unsafe. oh well.
                pdf.save(f'{folder}/{timestamp()}_{filename}')
                log(request.form.to_dict())
                data = json.dumps(request.form.to_dict())
                exec('''INSERT INTO uploads (email, timestamp, data) 
                        VALUES (?, ?, ?);''', 
                        [email, timestamp(), data])
    except:
        logger.exception('error')
        return error('Something went wrong. Contact reedperkins@byu.edu for assistance.')
    return success()

@app.route('/api/download', methods=['POST'])
def handle_download_request():
    try:
        try:
            option = request.json['option']
            email = request.json['email']
            log(f'**processing {email} download')
        except:
            logger.error(f'Bad request {request.data.decode()}')
            return error('Invalid email or option. Please double check your email and try again.')
        if option == 'first':
            if exists_in_db(email):
                return error('''It looks like you've already donwloaded an assignment. If you need to redownload it, select the redownload option and try again.''')
            result = get_next_assignment(email)
            if result == 'all assignments completed':
                return error('No new assignments are available. The experiment is complete!')
            assignment_id = result
            create_event(email, option, assignment_id)
            return pdf(assignment_id)
        elif option == 'redownload':
            if not exists_in_db(email):
                return error('''It looks like you haven't downloaded an assignment for the first time yet. Double check your email and try again.''')
            results = exec('SELECT assignment_id FROM events WHERE email = (?);', [email])
            assignment_id = results[-1][0]
            return pdf(assignment_id)
        elif option == 'returning':
            if not exists_in_db(email):
                return error('''It looks like you haven't downloaded an assignment for the first time yet. Double check your email and try again.''')
            result = get_next_assignment(email)
            if result == 'all assignments completed':
                return error('No new assignments are available. The experiment is complete!')
            elif result == 'user has completed all assignments':
                return error('You have completed all assignments. Nice work!')
            assignment_id = result
            create_event(email, option, assignment_id)
            return pdf(assignment_id)
        else:
            log(f'invalid option {option}')
            return error('Invalid option.')
    except Exception as e:
        log(str(e))
        return error('Server error. Contact reedperkins@byu.edu for assistence.')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
