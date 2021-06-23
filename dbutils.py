import sys
import sqlite3

DB_NAME = 'server.db'

def exec(sql):
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        cur.close()

def arg_error():
    print('Available options: create clear delete')
    exit()

def run(cmd):
    if cmd == 'create':
        exec('''
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY NOT NULL,
            email TEXT NOT NULL,
            option TEXT NOT NULL,
            assignment_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')

        exec('''
            CREATE TABLE IF NOT EXISTS uploads (
                upload_id INTEGER PRIMARY KEY NOT NULL,
                email TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL
            )
        ''')
    elif cmd == 'clear':
        exec('DELETE FROM events')
        exec('DELETE FROM uploads')
    elif cmd == 'delete':
        exec('DROP TABLE events')
        exec('DROP TABLE uploads')
    else:
        arg_error()
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        arg_error()
    run(sys.argv[1])