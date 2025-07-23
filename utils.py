
# Flask Things
from flask import request, redirect, url_for, make_response, g

# Firebase things
from firebase_config import db

# Other Packages
import random
import string
from functools import wraps
from dotenv import load_dotenv

# Loading env file
load_dotenv()

# 🔐 Load Firebase Admin SDK (downloaded JSON key file)
# cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDENTIALS")))
# firebase_admin.initialize_app(cred)
# db = firestore.client()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get('session_id')
        if not session_id:
            return redirect(url_for('home'))

        session_doc = db.collection('sessions').document(session_id).get()
        if not session_doc.exists:
            resp = make_response(redirect(url_for('home')))
            resp.delete_cookie('session_id')
            return resp

        email = session_doc.to_dict().get('email')
        user_doc = db.collection("users").document(email).get()
        if not user_doc.exists:
            return redirect(url_for('home'))

        user_data = user_doc.to_dict()
        g.user = {
            'name': f"{user_data.get('first-name', '')} {user_data.get('last-name', '')}",
            'email': email,
            'username' : user_data.get('username')
        }
        return f(*args, **kwargs)
    return decorated_function



def is_username_taken(username, db):
    docs = db.collection("users").where("username", "==", username).limit(1).stream()
    return any(True for _ in docs)

def generate_username(name, db):
    # Name cleanup: remove extra spaces and make kebab-case
    clean_name = "-".join(name.strip().split()).lower()  # e.g. "John    Doe Khan" → "john-doe-khan"
    username = clean_name

    # Check for duplicates
    while is_username_taken(username, db):
        # Add 3-digit random number and 1 random lowercase letter
        rand_digits = f"{random.randint(100, 999)}"
        rand_letter = random.choice(string.ascii_lowercase)
        username = f"{clean_name}-{rand_digits}{rand_letter}"

    return username
