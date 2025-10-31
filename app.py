from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import random
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

# Simple admin credentials for prototype
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'

DATA_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

# Helpers
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# Mock fleet data generator
def generate_fleet_summary():
    fleet = []
    for i in range(1, 11):
        vehicle_no = f"MH{random.randint(1,99)}-V{100+i}"
        uptime = round(random.uniform(85, 99), 2)
        predicted_risk = random.choice(['Low', 'Medium', 'High'])
        last_alert = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        fleet.append({
            'vehicle_no': vehicle_no,
            'uptime': uptime,
            'predicted_risk': predicted_risk,
            'last_alert': last_alert,
            'condition': random.choice(['Good', 'Needs Inspection', 'Critical'])
        })
    return fleet

@app.route('/')
def index():
    return redirect(url_for('portal_selection'))

@app.route('/portal-selection')
def portal_selection():
    return render_template('portal_selection.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid admin credentials')
    return render_template('admin_login.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        name = request.form.get('name')
        vehicle_no = request.form.get('vehicle_no')
        users = load_users()
        user = users.get(vehicle_no)
        if user and user.get('name') == name:
            session['role'] = 'user'
            session['vehicle_no'] = vehicle_no
            session['name'] = name
            return redirect(url_for('user_portal'))
        else:
            return render_template('user_login.html', error='User not found. Please register or check details.')
    return render_template('user_login.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('reg_name')
    vehicle_no = request.form.get('reg_vehicle')
    if not name or not vehicle_no:
        return redirect(url_for('login'))
    users = load_users()
    users[vehicle_no] = {'name': name, 'vehicle_no': vehicle_no, 'registered_at': datetime.now().isoformat()}
    save_users(users)
    return render_template('login.html', info='Registration successful. Please login as User.')

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    fleet = generate_fleet_summary()
    # aggregate metrics
    active_vehicles = len(fleet)
    predicted_issues = sum(1 for v in fleet if v['predicted_risk'] in ['Medium','High'])
    avg_uptime = round(sum(v['uptime'] for v in fleet)/len(fleet),2)
    recent_alerts = [v for v in fleet][:5]
    return render_template('admin_dashboard.html', fleet=fleet, active_vehicles=active_vehicles,
                           predicted_issues=predicted_issues, avg_uptime=avg_uptime, recent_alerts=recent_alerts)

@app.route('/scheduling')
def scheduling():
    # Scheduling page available to both admin and users in prototype
    if not session.get('role'):
        return redirect(url_for('login'))
    return render_template('scheduling.html')


@app.route('/chat')
def chat_page():
    if not session.get('role'):
        return redirect(url_for('login'))
    return render_template('chat.html')


@app.route('/rca')
def rca_insights():
    # Simple RCA insights page (admin only in prototype)
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    fleet = generate_fleet_summary()
    active_vehicles = len(fleet)
    predicted_issues = sum(1 for v in fleet if v['predicted_risk'] in ['Medium','High'])
    avg_uptime = round(sum(v['uptime'] for v in fleet)/len(fleet),2)

    # Example RCA cards (mocked)
    rca_cards = [
        {'title':'Brake System','percent':15,'total':100,'trend':'15.2%','badge_class':'danger','common':['Brake pad wear','Rotor warping','Hydraulic leak']},
        {'title':'Engine Control Unit','percent':8,'total':100,'trend':'8.7%','badge_class':'warning','common':['Software glitches','Sensor drift']},
        {'title':'Battery System','percent':12,'total':100,'trend':'12.4%','badge_class':'danger','common':['Capacity degradation','Charging failure']},
        {'title':'Cooling System','percent':5,'total':100,'trend':'5.1%','badge_class':'success','common':['Thermostat','Radiator clog']}
    ]

    capa_reports = [
        {'title':'Brake System Enhancement','team':'Manufacturing Team A','status':'in-progress','status_class':'warning','priority':'high','due':'2024-02-15'},
        {'title':'ECU Firmware Update','team':'Software Team B','status':'open','status_class':'primary','priority':'medium','due':'2024-03-01'},
        {'title':'Battery Thermal Management','team':'HV Team C','status':'resolved','status_class':'success','priority':'high','due':'2024-01-10'}
    ]

    # Chart data for months Jan-Jun
    labels = ['Jan','Feb','Mar','Apr','May','Jun']
    chart = {
        'labels': labels,
        'datasets': [
            {'label':'Brake System','data':[12,14,16,15,18,17],'borderColor':'#e74a3b','backgroundColor':'rgba(231,74,59,0.08)','fill':False},
            {'label':'Engine ECU','data':[8,7,6,5,4,3],'borderColor':'#4e73df','backgroundColor':'rgba(78,115,223,0.08)','fill':False},
            {'label':'Battery System','data':[10,11,12,11,10,9],'borderColor':'#f6c23e','backgroundColor':'rgba(246,194,62,0.08)','fill':False}
        ]
    }

    quick = {'active_vehicles': active_vehicles, 'predicted_issues': predicted_issues, 'avg_uptime': avg_uptime}

    return render_template('rca_insights.html', rca_cards=rca_cards, capa_reports=capa_reports, chart=chart, quick=quick)


@app.route('/vehicles')
def vehicle_monitoring():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    fleet = generate_fleet_summary()
    # enrich fleet with some sample fields
    for i, v in enumerate(fleet):
        v['vehicle_type'] = random.choice(['SUV Premium','Sedan Executive','Hatchback Basic','Truck'])
        v['location'] = random.choice(['Mumbai','Delhi','Bangalore','Chennai'])
        v['model'] = random.choice(['SUV Premium','Sedan LX','Hatchback X'])
        v['active_issues'] = random.randint(0,3)

    selected = fleet[0] if fleet else {'vehicle_no':'N/A','model':'N/A','location':'N/A','active_issues':0}

    # Mock telemetry data
    telemetry = {
        'timestamps': [(datetime.now()).strftime('%H:%M') for _ in range(8)],
        'temperature': [random.randint(70,95) for _ in range(8)],
        'oil': [random.randint(30,60) for _ in range(8)],
        'vibration': [round(random.uniform(1.0,3.5),1) for _ in range(8)]
    }

    return render_template('vehicle_monitoring.html', fleet=fleet, selected=selected, telemetry=telemetry)

@app.route('/user')
def user_portal():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    # Mock user-specific info
    vehicle_no = session.get('vehicle_no')
    name = session.get('name')
    maintenance = {
        'vehicle_no': vehicle_no,
        'last_service': (datetime.now()).strftime('%Y-%m-%d'),
        'next_expected_service_km': 5000,
        'health_score': random.randint(60, 98)
    }
    expected_delivery = (datetime.now()).strftime('%Y-%m-%d')
    return render_template('user_portal.html', maintenance=maintenance, name=name, expected_delivery=expected_delivery)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json or {}
    message = data.get('message','').lower()
    if not message:
        return jsonify({'reply':'Please describe the issue.'})
    
    # Rule-based responses
    if any(k in message for k in ['noise','squeak','squeaking','knock']):
        reply = 'Sounds like a suspension or engine mount issue. Check wheel bearings and mounts. If uncertain, schedule a service.'
    elif any(k in message for k in ['overheat','temperature','hot']):
        reply = 'Engine temperature high — stop driving and check coolant level. Visit service center if it continues.'
    elif any(k in message for k in ['battery','start','won\'t start','not start']):
        reply = 'Battery or starter issue likely. Try jump-starting or check battery health. Schedule service if problem persists.'
    elif any(k in message for k in ['oil','leak','smoke']):
        reply = 'Possible oil leak or serious issue. Avoid driving long distances and schedule immediate service.'
    else:
        reply = 'Could be minor — try basic checks (tyre pressure, fluid levels). If symptoms persist, schedule service.'
    
    reply += '\n\nFor more detailed information, please contact the administrator.'
    
    return jsonify({'reply': reply})

@app.route('/api/generate_token', methods=['POST'])
def generate_token():
    if not session.get('role'):
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json or {}
    query = data.get('query', '')
    
    # Generate a unique token
    token = str(uuid.uuid4())[:8].upper()
    
    # Get user information from session
    name = session.get('name', 'Guest')
    vehicle_no = session.get('vehicle_no', 'Unknown')
    
    # Mock vehicle type (in real app, this would come from database)
    vehicle_type = 'Sedan'  # This should be fetched from your database
    
    return jsonify({
        'token': token,
        'name': name,
        'vehicleNo': vehicle_no,
        'vehicleType': vehicle_type,
        'query': query
    })

@app.route('/api/schedule', methods=['POST'])
def api_schedule():
    data = request.json or {}
    vehicle_no = data.get('vehicle_no')
    date = data.get('date')
    service_center = data.get('center','Nearest Center')
    # In prototype we just echo back
    return jsonify({'status':'ok', 'message': f'Service scheduled for {vehicle_no} on {date} at {service_center}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
