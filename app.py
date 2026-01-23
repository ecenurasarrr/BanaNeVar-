from flask import Flask, render_template
import sqlite3
from recommender import LocalRecommender # Yapay zeka yerine yerel motoru çağırıyoruz

app = Flask(__name__)

# Veritabanı Başlatma ve Mersin Verileri
def init_db():
    conn = sqlite3.connect('bananevar.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS events 
                      (id INTEGER PRIMARY KEY, name TEXT, category TEXT, venue TEXT, date TEXT)''')
    
    cursor.execute("SELECT COUNT(*) FROM events")
    if cursor.fetchone()[0] == 0:
        mersin_data = [
            ('Mersin Marina Konseri', 'Müzik', 'Marina Sahne', '15.01.2026'),
            ('Yenişehir Tiyatro Günü', 'Tiyatro', 'Atatürk Kültür Merkezi', '17.01.2026'),
            ('Soli Pompeipolis Gezisi', 'Gezi', 'Mezitli', '20.01.2026'),
            ('Tarsus Şelale Kahvaltısı', 'Gastronomi', 'Tarsus', '22.01.2026')
        ]
        cursor.executemany("INSERT INTO events (name, category, venue, date) VALUES (?,?,?,?)", mersin_data)
    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    conn = sqlite3.connect('bananevar.db')
    conn.row_factory = sqlite3.Row
    events = conn.execute("SELECT * FROM events").fetchall()
    
    # Yerel öneri motorunu kullanarak tavsiye oluştur
    recommender = LocalRecommender()
    ai_suggestion = recommender.get_daily_tip(events[0]['name'], events[1]['name'])
    
    conn.close()
    return render_template('dashboard.html', events=events, ai_suggestion=ai_suggestion)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)