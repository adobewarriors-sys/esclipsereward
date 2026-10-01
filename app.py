from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import time
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_bot.db'
app.config['SECRET_KEY'] = 'free_eclipse_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    completed_tasks = db.Column(db.Integer, default=0)
    last_claim_time = db.Column(db.Float, default=0.0)
    referrer_id = db.Column(db.Integer, nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/user_info', methods=['POST'])
def user_info():
    data = request.json or {}
    username = data.get('username', 'GuestUser')
    ref_by = data.get('ref_by')

    user = User.query.filter_by(username=username).first()
    if not user:
        referrer = User.query.get(ref_by) if ref_by and str(ref_by).isdigit() else None
        user = User(username=username, referrer_id=referrer.id if referrer else None)
        db.session.add(user)
        db.session.commit()

    current_time = time.time()
    eclipse_active = (current_time - user.last_claim_time) < 86400

    return jsonify({
        'id': user.id,
        'username': user.username,
        'balance': user.balance,
        'completed_tasks': user.completed_tasks,
        'eclipse_active': eclipse_active,
        'time_remaining': max(0, int(86400 - (current_time - user.last_claim_time)))
    })

@app.route('/api/complete_tasks', methods=['POST'])
def complete_tasks():
    data = request.json or {}
    user = User.query.filter_by(username=data.get('username')).first()

    if not user:
        return jsonify({'status': 'error', 'message': 'User nahi mila!'})

    current_time = time.time()
    if (current_time - user.last_claim_time) < 86400:
        return jsonify({'status': 'error', 'message': 'Eclipse pehle se ON hai! 24 ghante baad try karein.'})

    user.completed_tasks += 3
    user.last_claim_time = current_time

    earned_bonus = 0
    if user.completed_tasks >= 5:
        multiplier = user.completed_tasks // 5
        earned_bonus = multiplier * 250
        user.completed_tasks %= 5
        user.balance += earned_bonus

    distribute_referral_rewards(user, earned_bonus if earned_bonus > 0 else 100)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'balance': user.balance,
        'completed_tasks': user.completed_tasks,
        'earned': earned_bonus
    })

def distribute_referral_rewards(user, amount):
    if user.referrer_id:
        t1 = User.query.get(user.referrer_id)
        if t1:
            t1.balance += (amount * 0.10)  # Tier 1: 10%
            if t1.referrer_id:
                t2 = User.query.get(t1.referrer_id)
                if t2:
                    t2.balance += (amount * 0.05)  # Tier 2: 5%
                    if t2.referrer_id:
                        t3 = User.query.get(t2.referrer_id)
                        if t3:
                            t3.balance += (amount * 0.03)  # Tier 3: 3%

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)