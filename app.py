# Flask Packages
from flask import Flask, render_template, jsonify, request, url_for, g
from flask_socketio import SocketIO, send, emit
from flask import make_response
from flask_cors import CORS
import requests

# Firebase Packages
import firebase_admin, json, os
from firebase_admin import credentials, auth, firestore
from firebase_config import db

# Other Packages
from dotenv import load_dotenv
import uuid
import re
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# Local Functions
from utils import *


load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'jhasdkjlasdfk903678yujhb67tgyjh45rtfg34wrg'
socketio = SocketIO(app, async_mode='threading')

CORS(app, supports_credentials=True)

@app.route("/")
def home():
    session_id = request.cookies.get('session_id')
    print(session_id)
    if not session_id:
        return render_template("home.html", logged_in=False)
    session_doc = db.collection('sessions').document(session_id).get()
    if session_doc.exists:        
        email = session_doc.to_dict().get('email')
        user_doc = db.collection("users").document(email).get()
        user_data = user_doc.to_dict()
        name = f"{user_data.get('first-name', '')} {user_data.get('last-name', '')}"
        return render_template("home.html", logged_in = True, name= name, email=email)
    else:
        resp = make_response(render_template('home.html', logged_in=False))
        resp.delete_cookie('session_id')
        return resp

@app.route("/verify-token", methods=["POST"])
def verify_token():
    data = request.get_json()
    id_token = data.get("idToken")
    try:
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token["email"]
        user_doc = db.collection("users").document(email).get()
        name = decoded_token["name"]

        if not user_doc.exists:
            # Step -1 : Saving User's Data @Firestore
            name_parts = name.split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            uid = decoded_token["uid"]
            username = generate_username(name, db)
            data = {
                'uid' : uid,
                'first-name' : first_name,
                'last-name' : last_name,
                'username' : username,
                'created-on' : datetime.now(ZoneInfo("Asia/Kolkata")),
            }
            db.collection('users').document(email).set(data)

        # Step-2 : Now Let's Log his session to the cloud
        session_id = str(uuid.uuid4())
        db.collection('sessions').document(session_id).set({'email' : email})

        # Step-3 : Now Let's save his session id in browser cookie
        resp = make_response(jsonify({"success": True, "email": email, "name":name})) #Sent To Frontend
        resp.set_cookie('session_id', session_id, max_age=60*60*24*90, samesite="Lax", secure=False)
        return resp

    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 401
@app.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"success": True}))
    resp.delete_cookie('session_id')
    return resp
@app.route("/set-cookie")
def cookie():
    resp = make_response(redirect(url_for('home'))) #Sent To Frontend
    resp.set_cookie('session_id', "790b1b11-1a8e-4c8c-935e-b6685ffe8cc8", max_age=60*60*24*90, samesite="Lax", secure=False)
    return resp

# Global Chat Setup

@app.route('/global-chat')
@login_required
def global_chat():
    username = g.user['username']
    name = g.user['name']
    email = g.user['email']

    # Load past messages from Firebase Firestore
    docs = db.collection("chat_messages").order_by("timestamp").stream()
    IST = timezone(timedelta(hours=5, minutes=30))

    messages = []
    for doc in docs:
        data = doc.to_dict()
        ts = data.get("timestamp",0)
        if ts:
            ts = ts.astimezone(IST)
            # Firestore Timestamp object to Python datetime
            date_str = ts.strftime("%Y-%m-%d")   # e.g., 2025-07-05
            time_str = ts.strftime("%I:%M %p") # e.g 02:32 PM
        else:
            date_str, time_str = "Unknown", "Unknown"

        messages.append({
            "username": data.get("username", "Anonymous"),
            "message": data.get("message", ""),
            "date": date_str,
            "time": time_str
        })

    return render_template("global-chat.html", logged_in = True, messages=messages, username=username, name=name, email=email)

@socketio.on('send_message')
def handle_send(data):
    username = data['username']
    message = data['message']

    # Broadcast to all clients
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    print(now)
    time_str = now.strftime("%I:%M %p")
    emit('receive_message', {'username': username, 'message': message, 'time':time_str}, broadcast=True)

    # Save to Firebase
    db.collection("chat_messages").add({
        "username": username,
        "message": message,
        "timestamp": datetime.now(ZoneInfo("Asia/Kolkata"))
    })

@app.route("/dashboard")
@login_required
def dashboard():
    username = g.user['username']
    name = g.user['name']
    email = g.user['email']

    return render_template("dashboard.html", logged_in = True, username=username, name=name, email=email)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    # app.run()