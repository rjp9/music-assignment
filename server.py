import datetime
from dbutils import DB_NAME
from flask import Flask, render_template, request, send_file
import sqlite3
import json
import logging

TOTAL_ASSIGNMENTS = 32
ANNOTATORS_PER_ASSIGNMENT = 3
DB_NAME = 'server.db'

app = Flask(__name__)
con = sqlite3.connect(DB_NAME)


# ==================
# Logging 
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler('server.log'))

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

def get_next_assignment():
    results = db_exec('SELECT * FROM events')
    return ((len(results) // ANNOTATORS_PER_ASSIGNMENT) % TOTAL_ASSIGNMENTS) + 1
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

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/api/assignment', methods=['POST'])
def handle_assignment():
    logger.error('here')
    try:
        try:
            option = request.json['option']
            email = request.json['email']
        except:
            logger.error(f'Bad request {request.data.decode()}')
            return error('Invalid email or option. Please double check your email and try again.')
        if option == 'first':
            if exists_in_db(email):
                return error('''It looks like you've already donwloaded an assignment. If you need to redownload it, select the redownload option and try again.''')
            assignment_id = get_next_assignment()
            create_event(email, option, assignment_id)
            return pdf(assignment_id)
        elif option == 'redownload':
            if not exists_in_db(email):
                return error('''It looks like you haven't downloaded an assignment for the first time. Double check your email and try again.''')
            results = db_exec('''
                SELECT assignment_id FROM events WHERE email = (?);
                ''',
                [email]
            )
            assignment_id = results[-1][0]
            return pdf(assignment_id)
        elif option == 'returning':
            if not exists_in_db(email):
                return error('''It looks like you haven't downloaded an assignment for the first time. Double check your email and try again.''')
            assignment_id = get_next_assignment()
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
