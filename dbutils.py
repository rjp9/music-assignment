import sys
import sqlite3

DB_NAME = 'server.db'
con = sqlite3.connect(DB_NAME)

def db_exec(sql):
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    cur.close()

def arg_error():
    print('Available options: create clear delete')
    exit()

def run(cmd):
    if cmd == 'create':
        create_cmd = '''
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY NOT NULL,
            email TEXT NOT NULL,
            option TEXT NOT NULL,
            assignment_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
        '''
        db_exec(create_cmd)
    elif cmd == 'clear':
        clear_cmd = 'DELETE FROM events'
        db_exec(clear_cmd)
    elif cmd == 'delete':
        delete_cmd = 'DROP TABLE events'
        db_exec(delete_cmd)
    else:
        arg_error()
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        arg_error()
    run(sys.argv[1])