from flask_mail import Mail
from werkzeug.utils import secure_filename
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

# ==============================
# Configuration
# ==============================
UPLOAD_FOLDER = 'static/profile_pics/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sports_db'

mysql = MySQL(app)

# ==============================
# Home Page
# ==============================
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, sport_name, description FROM sports")
    sports = cur.fetchall()
    cur.close()
    return render_template('index.html', sports=sports)

# ==============================
# Admin Login
# ==============================
@app.route('/adminlogin', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM admin WHERE username=%s AND password=%s', (username, password))
        admin = cur.fetchone()
        cur.close()
        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'
    return render_template('admin_login.html', error=error)

# ==============================
# Admin Dashboard (Overview)
# ==============================
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    # Get counts for dashboard cards
    cur.execute("SELECT COUNT(*) FROM coaches")
    total_coaches = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM participants")
    total_participants = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM sports")
    total_sports = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM participant_sport_requests WHERE status='pending'")
    pending_requests = cur.fetchone()[0]
    
    # Get recent sports requests with more details
    cur.execute("""
        SELECT 
            psr.id, 
            p.full_name, 
            p.vu_id,
            s.sport_name, 
            psr.status,
            psr.request_date,
            c.coach_name
        FROM participant_sport_requests psr
        JOIN participants p ON psr.participant_id = p.id
        JOIN sports s ON psr.sport_id = s.id
        LEFT JOIN coaches c ON psr.coach_id = c.id
        ORDER BY psr.request_date DESC LIMIT 5
    """)
    recent_activity = cur.fetchall()
    cur.close()
    
    return render_template('admin/admin_dashboard.html', 
                           total_coaches=total_coaches, 
                           total_participants=total_participants, 
                           total_sports=total_sports,
                           pending_requests=pending_requests,
                           recent_activity=recent_activity)


# ==============================
# Sports Management
# ==============================

@app.route('/admin/sports')
def admin_sports():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, sport_name, description FROM sports ORDER BY sport_name ASC")
    sports = cur.fetchall()
    cur.close()
    
    return render_template('admin/sports.html', sports=sports)


@app.route('/admin/sport/add', methods=['POST'])
def admin_sport_add():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    sport_name = request.form.get('sport_name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not sport_name:
        flash('Sport name is required', 'danger')
        return redirect(url_for('admin_sports'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO sports (sport_name, description) 
            VALUES (%s, %s)
        """, (sport_name, description))
        mysql.connection.commit()
        cur.close()
        flash('Sport added successfully', 'success')
    except Exception as e:
        flash('Error adding sport (possibly duplicate name)', 'danger')
    
    return redirect(url_for('admin_sports'))


@app.route('/admin/sport/edit/<int:sport_id>', methods=['POST'])
def admin_sport_edit(sport_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    sport_name = request.form.get('sport_name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not sport_name:
        flash('Sport name is required', 'danger')
        return redirect(url_for('admin_sports'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE sports 
            SET sport_name = %s, description = %s 
            WHERE id = %s
        """, (sport_name, description, sport_id))
        mysql.connection.commit()
        cur.close()
        flash('Sport updated successfully', 'success')
    except Exception as e:
        flash('Error updating sport (possibly duplicate name)', 'danger')
    
    return redirect(url_for('admin_sports'))


@app.route('/admin/sport/delete/<int:sport_id>', methods=['POST'])
def admin_sport_delete(sport_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM sports WHERE id = %s", (sport_id,))
        mysql.connection.commit()
        cur.close()
        flash('Sport deleted successfully', 'success')
    except Exception as e:
        flash('Cannot delete sport — it may be in use by coaches or requests', 'danger')
    
    return redirect(url_for('admin_sports'))


@app.route('/admin/coaches')
def admin_coaches():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id, 
            coach_name, 
            email, 
            profile_picture, 
            bio, 
            specialization, 
            sports_expertise, 
            team_management, 
            availability, 
            status,
            created_at
        FROM coaches 
        ORDER BY id DESC
    """)
    coaches = cur.fetchall()
    cur.close()
    
    return render_template('admin/coaches.html', coaches=coaches)

# Add this route (preferably with CSRF protection in production)
@app.route('/admin/coach/update-status/<int:coach_id>', methods=['POST'])
def update_coach_status(coach_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'active', 'suspended']:
        flash('Invalid status value', 'danger')
        return redirect(url_for('admin_coaches'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE coaches 
            SET status = %s 
            WHERE id = %s
        """, (new_status, coach_id))
        mysql.connection.commit()
        cur.close()
        
        flash(f'Coach status updated to {new_status.capitalize()}', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Error updating status', 'danger')
        print(e)  # log in production
        
    return redirect(url_for('admin_coaches'))


@app.route('/admin/participants')
def admin_participants():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id, 
            vu_id, 
            full_name, 
            email, 
            profile_picture, 
            bio, 
            sports_preferences, 
            past_participation, 
            achievements, 
            status,
            created_at
        FROM participants 
        ORDER BY id DESC
    """)
    participants = cur.fetchall()
    cur.close()
    
    return render_template('admin/participants.html', participants=participants)


@app.route('/admin/participant/update-status/<int:participant_id>', methods=['POST'])
def admin_update_participant_status(participant_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'active', 'suspended']:
        flash('Invalid status', 'danger')
        return redirect(url_for('admin_participants'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE participants 
            SET status = %s 
            WHERE id = %s
        """, (new_status, participant_id))
        mysql.connection.commit()
        cur.close()
        
        flash(f'Participant status updated to {new_status.capitalize()}', 'success')
    except Exception as e:
        flash('Error updating status', 'danger')
        # log error in production
    
    return redirect(url_for('admin_participants'))


# ==============================
# Logout
# ==============================
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# ==============================
# Coach Registration
# ==============================
@app.route('/coach/register', methods=['GET', 'POST'])
def coach_register():
    cur = mysql.connection.cursor()
    # Fetch sports that do NOT have a coach assigned
    cur.execute("""
        SELECT id, sport_name 
        FROM sports 
        WHERE id NOT IN (SELECT sport_id FROM coach_sports)
    """)
    sports = cur.fetchall()

    if request.method == 'POST':
        coach_name = request.form['coach_name']
        email = request.form['email']
        password = request.form['password']
        bio = request.form['bio']
        sport_id = request.form['sport_id']

        # Profile picture handling
        file = request.files.get('profile_picture')
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        cur.execute("""
            INSERT INTO coaches (coach_name, email, password, bio, profile_picture)
            VALUES (%s, %s, %s, %s, %s)
        """, (coach_name, email, password, bio, filename))
        mysql.connection.commit()

        coach_id = cur.lastrowid
        cur.execute("INSERT INTO coach_sports (coach_id, sport_id) VALUES (%s, %s)", (coach_id, sport_id))
        mysql.connection.commit()

        cur.close()
        flash('Registration successful. Waiting for admin approval.', 'success')
        return redirect(url_for('coach_login'))

    cur.close()
    return render_template('coach_register.html', sports=sports)

# ==============================
# Coach Login
# ==============================
@app.route('/coach/login', methods=['GET', 'POST'])
def coach_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, coach_name, status 
            FROM coaches 
            WHERE email=%s AND password=%s
        """, (email, password))
        coach = cur.fetchone()
        cur.close()

        if coach:
            if coach[2] != 'active':
                flash('Your account is not active yet.', 'error')
                return redirect(url_for('coach_login'))

            session['coach_id'] = coach[0]
            session['coach_name'] = coach[1]
            return redirect(url_for('coach_dashboard'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('coach_login.html')

@app.route('/coach/dashboard', methods=['GET'])
def coach_dashboard():
    if 'coach_id' not in session:
        return redirect(url_for('coach_login'))

    cur = mysql.connection.cursor()

    # Get all sports assigned to this coach
    cur.execute("""
        SELECT s.id, s.sport_name
        FROM coach_sports cs
        JOIN sports s ON cs.sport_id = s.id
        WHERE cs.coach_id = %s
    """, (session['coach_id'],))
    sports = cur.fetchall()

    # Registration Status Table: participants related to this coach's sports
    cur.execute("""
        SELECT DISTINCT p.id, p.full_name, p.vu_id, p.email, p.status
        FROM participants p
        JOIN participant_sport_requests ps ON p.id = ps.participant_id
        JOIN coach_sports cs ON ps.sport_id = cs.sport_id
        WHERE cs.coach_id = %s
        ORDER BY p.full_name
    """, (session['coach_id'],))
    participants = cur.fetchall()

    # Sports Approval Table: all participant requests for coach's sports
    sport_requests = {}
    for sport in sports:
        cur.execute("""
            SELECT ps.id, p.full_name, p.vu_id, p.email, ps.status
            FROM participant_sport_requests ps
            JOIN participants p ON ps.participant_id = p.id
            WHERE ps.sport_id = %s
            ORDER BY ps.request_date DESC
        """, (sport[0],))
        sport_requests[sport[0]] = cur.fetchall()

    cur.close()

    return render_template(
        'coach/coach_dashboard.html',
        coach_name=session['coach_name'],
        sports=sports,
        participants=participants,
        sport_requests=sport_requests
    )



@app.route('/coach/update-participant-registration/<int:participant_id>', methods=['POST'])
def admin_update_participant_registration(participant_id):
    if 'coach_id' not in session:
        return redirect(url_for('coach_login'))

    status = request.form['status']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE participants
        SET status=%s
        WHERE id=%s
    """, (status, participant_id))
    mysql.connection.commit()
    cur.close()

    flash('Participant registration status updated successfully.', 'success')
    return redirect(url_for('coach_dashboard'))


 
# ================================
# COACH PROFILE UPDATE
# ================================
@app.route('/coach/profile', methods=['GET', 'POST'])
def coach_profile():
    if 'coach_id' not in session:
        return redirect(url_for('coach_login'))

    coach_id = session['coach_id']
    cur = mysql.connection.cursor()
    
    # Fetch current coach data
    cur.execute("SELECT * FROM coaches WHERE id=%s", (coach_id,))
    coach = cur.fetchone()

    if request.method == 'POST':
        coach_name = request.form['coach_name']
        email = request.form['email']
        password = request.form['password']  # optional
        specialization = request.form['specialization']
        bio = request.form['bio']
        sports_expertise = request.form['sports_expertise']
        team_management = request.form['team_management']
        availability = request.form['availability']

        # Handle profile picture upload
        file = request.files.get('profile_picture')
        db_path = coach[2]  # default current picture
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # make unique filename
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            upload_folder = 'static/uploads/'
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, unique_filename))
            db_path = f"uploads/{unique_filename}"

        # Update query
        if password.strip():  # only update password if entered
            cur.execute("""
                UPDATE coaches SET 
                coach_name=%s, email=%s, password=%s, specialization=%s, bio=%s, 
                sports_expertise=%s, team_management=%s, availability=%s, profile_picture=%s
                WHERE id=%s
            """, (coach_name, email, password, specialization, bio, sports_expertise, team_management, availability, db_path, coach_id))
        else:
            cur.execute("""
                UPDATE coaches SET 
                coach_name=%s, email=%s, specialization=%s, bio=%s, 
                sports_expertise=%s, team_management=%s, availability=%s, profile_picture=%s
                WHERE id=%s
            """, (coach_name, email, specialization, bio, sports_expertise, team_management, availability, db_path, coach_id))

        mysql.connection.commit()
        cur.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('coach_profile'))

    cur.close()
    return render_template('coach/coach_profile.html', coach=coach)



# ==============================
# Coach Logout
# ==============================
@app.route('/coach/logout')
def coach_logout():
    session.pop('coach_id', None)
    session.pop('coach_name', None)
    return redirect(url_for('index'))


# ================================
# PARTICIPANT REGISTER
# ================================
@app.route('/participant/register', methods=['GET', 'POST'])
def participant_register():
    cur = mysql.connection.cursor()
    # Fetch sports for selection
    cur.execute("SELECT id, sport_name FROM sports")
    sports = cur.fetchall()

    if request.method == 'POST':
        vu_id = request.form['vu_id']
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        selected_sports = request.form.getlist('sport_ids')  # max 2

        if len(selected_sports) > 2:
            flash('You can select maximum 2 sports', 'error')
            return redirect(url_for('participant_register'))

        cur.execute(
            "INSERT INTO participants (vu_id, full_name, email, password) VALUES (%s,%s,%s,%s)",
            (vu_id, full_name, email, password)
        )
        mysql.connection.commit()
        participant_id = cur.lastrowid

        for sport_id in selected_sports:
            cur.execute(
                "INSERT INTO participant_sport_requests (participant_id, sport_id) VALUES (%s,%s)",
                (participant_id, sport_id)
            )
        mysql.connection.commit()
        cur.close()
        flash('Registration successful. Waiting for coach approval.', 'success')
        return redirect(url_for('participant_login'))

    cur.close()
    return render_template('participant_register.html', sports=sports)

# ================================
# PARTICIPANT LOGIN
# ================================
@app.route('/participant/login', methods=['GET', 'POST'])
def participant_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id, full_name, status FROM participants WHERE email=%s AND password=%s",
            (email, password)
        )
        participant = cur.fetchone()
        cur.close()

        if participant:
            if participant[2] != 'active':
                flash('Your account is not active yet.', 'error')
                return redirect(url_for('participant_login'))

            session['participant_id'] = participant[0]
            session['participant_name'] = participant[1]
            return redirect(url_for('participant_dashboard'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('participant_login.html')

@app.route('/participant/dashboard')
def participant_dashboard():
    if 'participant_id' not in session:
        return redirect(url_for('participant_login'))

    participant_id = session['participant_id']
    cur = mysql.connection.cursor()

    # Fetch participant registration info
    cur.execute("""
        SELECT full_name, vu_id, email, status, bio
        FROM participants
        WHERE id=%s
    """, (participant_id,))
    participant_info = cur.fetchone()

    # Fetch only approved sports and their coach
    cur.execute("""
        SELECT s.sport_name, c.coach_name
        FROM participant_sport_requests psr
        JOIN sports s ON psr.sport_id = s.id
        JOIN coaches c ON psr.coach_id = c.id
        WHERE psr.participant_id=%s AND psr.status='approved'
        ORDER BY s.sport_name
    """, (participant_id,))
    approved_sports = cur.fetchall()  # List of tuples: [(sport_name, coach_name), ...]

    cur.close()

    return render_template(
        'participant/participant_dashboard.html',
        participant_info=participant_info,
        approved_sports=approved_sports
    )

# ================================
# PARTICIPANT PROFILE UPDATE
# ================================
@app.route('/participant/profile', methods=['GET', 'POST'])
def participant_profile():
    if 'participant_id' not in session:
        return redirect(url_for('participant_login'))

    participant_id = session['participant_id']
    cur = mysql.connection.cursor()

    # Fetch current participant data
    cur.execute("SELECT * FROM participants WHERE id=%s", (participant_id,))
    participant = cur.fetchone()

    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']  # optional
        bio = request.form['bio']
        sports_preferences = request.form['sports_preferences']
        past_participation = request.form['past_participation']
        achievements = request.form['achievements']

        # Handle profile picture upload
        file = request.files.get('profile_picture')
        db_path = participant[5]  # default current picture
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            upload_folder = 'static/uploads/'
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, unique_filename))
            db_path = f"uploads/{unique_filename}"

        # Update query
        if password.strip():  # only update password if entered
            cur.execute("""
                UPDATE participants SET
                full_name=%s, email=%s, password=%s, bio=%s,
                sports_preferences=%s, past_participation=%s, achievements=%s,
                profile_picture=%s
                WHERE id=%s
            """, (full_name, email, password, bio, sports_preferences, past_participation, achievements, db_path, participant_id))
        else:
            cur.execute("""
                UPDATE participants SET
                full_name=%s, email=%s, bio=%s,
                sports_preferences=%s, past_participation=%s, achievements=%s,
                profile_picture=%s
                WHERE id=%s
            """, (full_name, email, bio, sports_preferences, past_participation, achievements, db_path, participant_id))

        mysql.connection.commit()
        cur.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('participant_profile'))

    cur.close()
    return render_template('participant/participant_profile.html', participant=participant)



# ================================
# PARTICIPANT LOGOUT
# ================================
@app.route('/participant/logout')
def participant_logout():
    session.pop('participant_id', None)
    session.pop('participant_name', None)
    return redirect(url_for('index'))



# ==============================
# Run App
# ==============================
if __name__ == '__main__':
    app.run(debug=True)
