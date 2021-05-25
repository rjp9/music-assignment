from flask import Flask, render_template, request, send_file

app = Flask(__name__)
visited = set()
current_assignment = 1
total_assignments = 40

@app.route('/')
def hello_world():
    return render_template('index.html')

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
    return send_file('static/pdfs/assignment.pdf',
                     attachment_filename='assignment.pdf',
                     as_attachment=True)

@app.route('/downloadNewAssignment', methods=['GET'])
def download_new_assignment():

    ## logic...

    return send_file('static/pdfs/assignment.pdf',
                     attachment_filename='assignment.pdf',
                     as_attachment=True)