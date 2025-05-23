import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    try:
        # Initialize Firebase with your credentials
        cred = credentials.Certificate('fb.json')
        firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        return None