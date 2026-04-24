import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session
import sqlite3
import qrcode
import io
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from recommender import AIRecommender

load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "bananevar_secret_key_123")

def init_db():
    conn = sqlite3.connect('bananevar.db')
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT)''')
    
    # Etkinlik tablosu
    cursor.execute('''CREATE TABLE IF NOT EXISTS events 
                      (id INTEGER PRIMARY KEY, name TEXT, category TEXT, venue TEXT, date TEXT)''')
    
    # Biletler tablosu (user_id eklendi)
    cursor.execute('''CREATE TABLE IF NOT EXISTS tickets 
                      (id INTEGER PRIMARY KEY, 
                       user_id INTEGER,
                       owner_name TEXT, 
                       event_name TEXT, 
                       ticket_count INTEGER,
                       purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY(user_id) REFERENCES users(id))''')
                       
    cursor.execute("SELECT COUNT(*) FROM events")
    if cursor.fetchone()[0] == 0:
        mersin_data = [
            ('Mersin Marina Konseri', 'Müzik', 'Marina Sahne', '15.01.2026'),
            ('Yenişehir Tiyatro Günü', 'Tiyatro', 'Atatürk Kültür Merkezi', '17.01.2026'),
            ('Soli Pompeipolis Gezisi', 'Gezi', 'Mezitli', '20.01.2026'),
            ('Tarsus Şelale Kahvaltısı', 'Gastronomi', 'Tarsus', '22.01.2026'),
            ('Uluslararası Mersin Müzik Festivali', 'Müzik', 'Mersin Kültür Merkezi', '05.02.2026'),
            ('Kızkalesi Doğa Yürüyüşü', 'Gezi', 'Erdemli', '10.02.2026'),
            ('Mersin Tantuni Festivali', 'Gastronomi', 'Forum AVM Meydanı', '25.02.2026'),
            ('Açık Hava Sineması', 'Sinema', 'Mezitli Sahil', '01.03.2026')
        ]
        cursor.executemany("INSERT INTO events (name, category, venue, date) VALUES (?,?,?,?)", mersin_data)
    conn.commit()
    conn.close()

def get_events():
    conn = sqlite3.connect('bananevar.db')
    conn.row_factory = sqlite3.Row
    events_db = conn.execute("SELECT * FROM events").fetchall()
    conn.close()
    return [dict(ix) for ix in events_db]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = sqlite3.connect('bananevar.db')
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Hatalı e-posta veya şifre.")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('bananevar.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (username, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Bu kullanıcı adı veya e-posta zaten kullanımda.")
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    events = get_events()
    recommender = AIRecommender()
    ai_suggestion = recommender.get_daily_tip(events)
    return render_template('dashboard.html', events=events, ai_suggestion=ai_suggestion)

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    user_input = request.json.get('user_input', '')
    if not user_input:
        return jsonify({'error': 'Please provide an input'}), 400
        
    events = get_events()
    recommender = AIRecommender()
    suggestion = recommender.get_interactive_tip(events, user_input)
    return jsonify({'suggestion': suggestion})

@app.route('/buy_ticket', methods=['POST'])
def buy_ticket():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Lütfen giriş yapın.'}), 401
        
    data = request.json
    owner_name = data.get('owner_name')
    event_name = data.get('event_name')
    ticket_count = data.get('ticket_count', 1)
    
    if not owner_name or not event_name:
        return jsonify({'success': False, 'message': 'Eksik bilgi!'}), 400
        
    conn = sqlite3.connect('bananevar.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (user_id, owner_name, event_name, ticket_count) VALUES (?, ?, ?, ?)", 
                   (session['user_id'], owner_name, event_name, int(ticket_count)))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Biletiniz başarıyla oluşturuldu.'})

@app.route('/tickets')
def tickets():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('bananevar.db')
    conn.row_factory = sqlite3.Row
    tickets_db = conn.execute("SELECT * FROM tickets WHERE user_id = ? ORDER BY purchase_date DESC", 
                              (session['user_id'],)).fetchall()
    conn.close()
    return render_template('tickets.html', tickets=tickets_db)

@app.route('/ticket_qr/<int:ticket_id>')
def ticket_qr(ticket_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"BanaNeVar Ticket ID: {ticket_id}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/add_event', methods=['POST'])
def add_event():
    name = request.form.get('name')
    category = request.form.get('category')
    venue = request.form.get('venue')
    date = request.form.get('date')
    
    if name and category and venue and date:
        conn = sqlite3.connect('bananevar.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (name, category, venue, date) VALUES (?, ?, ?, ?)", 
                       (name, category, venue, date))
        conn.commit()
        conn.close()
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)