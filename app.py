from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------------------
# DATABASE INIT
# ---------------------------
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            complaint TEXT,
            status TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------------------
# HOME
# ---------------------------
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect('/login')

# ---------------------------
# REGISTER
# ---------------------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("INSERT INTO users (username, password) VALUES (?,?)", (user,pwd))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# ---------------------------
# LOGIN
# ---------------------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user,pwd))
        data = cur.fetchone()

        conn.close()

        if data:
            session['user'] = user
            return redirect('/')
        else:
            return "Invalid Login ❌"

    return render_template('login.html')

# ---------------------------
# LOGOUT
# ---------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ---------------------------
# ADD COMPLAINT
# ---------------------------
@app.route('/add', methods=['GET','POST'])
def add():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        complaint = request.form['complaint']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO complaints (name, complaint, status) VALUES (?, ?, ?)",
            (name, complaint, "Pending")
        )

        conn.commit()
        conn.close()

        return redirect('/view')

    return render_template('add.html')

# ---------------------------
# VIEW COMPLAINTS
# ---------------------------
@app.route('/view')
def view():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM complaints")
    data = cur.fetchall()

    conn.close()

    return render_template('view.html', complaints=data)

# ---------------------------
# UPDATE STATUS
# ---------------------------
@app.route('/update/<int:id>')
def update(id):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("UPDATE complaints SET status='Solved' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/view')

# ---------------------------
# DELETE
# ---------------------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM complaints WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/view')

# ---------------------------
# ADMIN DASHBOARD 📊
# ---------------------------
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM complaints")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE status='Solved'")
    solved = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending = cur.fetchone()[0]

    conn.close()

    return render_template('admin.html', total=total, solved=solved, pending=pending)

# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

