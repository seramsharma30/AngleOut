import firebase_admin
from firebase_admin import credentials, firestore
import json, os

def initialize_firebase():
    try:
        # Initialize Firebase with your credentials
        cred_dict = json.loads(os.getenv("FIREBASE_KEY"))
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        return None
