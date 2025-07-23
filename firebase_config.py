import os, json, firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()
cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDENTIALS")))
firebase_admin.initialize_app(cred)
db = firestore.client()