import sqlite3

def init_db():
    conn = sqlite3.connect('oil_stains.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS oil_stains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
