import datetime
from dbutils import DB_NAME
from flask import Flask, render_template, request, send_file
import sqlite3
import json
import logging
from werkzeug.utils import secure_filename
import os

TOTAL_ASSIGNMENTS = 32
ANNOTATORS_PER_ASSIGNMENT = 3
DB_NAME = 'server.db'
UPLOAD_DIR = 'uploaded/'

app = Flask(__name__)
con = sqlite3.connect(DB_NAME)


# ==================
# Logging 
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler('server.log'))
# =================


# =================
# General stuff
def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S%p')
# =================



# ================
# DB stuff
def db_exec(sql, args=[]):
    cur = con.cursor()
    cur.execute(sql, args)
    con.commit()
    results = cur.fetchall()
    return results if results else []

def exists_in_db(email):
    results = db_exec('SELECT * FROM events WHERE email = (?);', [email])
    return results and len(results) != 0

def create_event(email, option, id):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S%p')
    db_exec('''
        INSERT INTO events (email, option, assignment_id, timestamp) VALUES (?, ?, ?, ?);
        ''', 
        [email, option, id, timestamp]
    )

def get_next_assignment(email):
    all_assignments = set([i+1 for i in range(TOTAL_ASSIGNMENTS)])
    logger.info(f'all {all_assignments}')
    results = db_exec('''
                        SELECT assignment_id 
                        FROM events 
                        GROUP BY assignment_id
                        HAVING COUNT(assignment_id) >= (?);''',
                        [ANNOTATORS_PER_ASSIGNMENT])
    logger.info(f'completed {results}')
    eligible_assignments = all_assignments.difference(*results)
    if not eligible_assignments:
        return 'all assignments completed'
    logger.info(f'incomplete {eligible_assignments}')
    results = db_exec('SELECT assignment_id FROM events WHERE email = (?);', [email])
    logger.info(f'assigned to {email} {results}')
    eligible_assignments = list(eligible_assignments.difference(*results))
    logger.info(f'remaining {eligible_assignments}')
    if not eligible_assignments:
        return 'user has completed all assignments'
    logger.info(f'assignment {eligible_assignments[0]}')
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

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/api/upload', methods=['GET', 'POST'])
def handle_upload_request():
    try:
        email = request.form['email']
        pdf = request.files['pdf']
        if pdf:
            filename = secure_filename(pdf.filename)
            if filename and filename.split('.')[-1] == 'pdf':
                folder = get_folder(email) # this could be really unsafe. oh well.
                pdf.save(f'{folder}/{timestamp()}_{filename}')
    except Exception as e:
        logger.exception(e)
        return error('Something went wrong. Contact reedperkins@byu.edu for assistance.')
    return success();

@app.route('/api/download', methods=['POST'])
def handle_download_request():
    try:
        try:
            # print(request.data.decode())
            # data = json.loads(request.data.decode())
            # print(data)
            option = request.json['option']
            email = request.json['email']
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
            results = db_exec('SELECT assignment_id FROM events WHERE email = (?);', [email])
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
            logger.error(f'invalid option {option}')
            return error('Invalid option.')
    except Exception as e:
        logger.exception(e)
        return error('Server error. Contact reedperkins@byu.edu for assistence.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
