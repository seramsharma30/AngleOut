import json, os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred_dict = json.loads(os.getenv("FIREBASE_KEY"))
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

def init_firebase_db():
    """
    Initialize Firebase databse and check if collection exists
    """

    try:
        # Check if keyword_tracker collection exists
        collections = db.collections()
        collection_names = [collection.id for collection in collections]

        if 'keyword_tracker' not in collection_names:
            # Create keyword_tracker collection
            db.collection('keyword_tracker').document().set({
                'site_url': 'init',
                'user_gmail' : 'init',
                'keyword': 'init'
            })
            print("Keyword tracker collection created")
        else:
            print("Keyword tracker collection already exists")
        
        # Initialize content_hub collection if not exists
        if 'content_hub' not in collection_names:
            db.collection('content_hub').document().set({
                'site_url': 'init',
                'user_gmail' : 'init',
                'PRIORITY': 'init',
                'NAME': 'init',
                'BRIEF': 'init',
                'PRIMARY KEYWORD': 'init',
                'FUNNEL STAGE': 'init',
                'STATUS': 'init',
                'LIVE URL': 'init',
                'LAST UPDATED': 'init'
            })
            print("Content hub collection created")
        else:
            print("Content hub collection already exists")

        return db
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        return None


def get_keyword_tracker(user_gmail, site_url):

    """
    Get keyword tracker records for a specific user and site
    """
    try:
        # Query the collection
        query = db.collection('keyword_tracker').where('user_gmail', '==', user_gmail).where('site_url', '==', site_url)
        # query = db.collection('keyword_tracker').filter('user_gmail', '==', user_gmail).filter('site_url', '==', site_url)

        docs = query.stream()
        
        # Convert to list of dictionaries
        records = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id  # Add document ID
            records.append(data)
            
        return records
    except Exception as e:
        print(f"Error fetching keyword tracker records: {str(e)}")
        return []

def add_keyword_tracker(site_url, user_gmail, keyword):
    """
    Add a new keyword tracker record
    """
    try:
        # Add new document
        doc_ref = db.collection('keyword_tracker').document()
        doc_ref.set({
            'site_url': site_url,
            'user_gmail': user_gmail,
            'keyword': keyword
        })
        return True
    except Exception as e:
        print(f"Error adding keyword tracker record: {str(e)}")
        return False
    






def get_content_hub_data(user_gmail, site_url):
    """
    Get content hub data for a specific user and site
    """
    try:
        query = db.collection('content_hub').where('user_gmail', '==', user_gmail).where('site_url', '==', site_url)
        docs = query.stream()
        records = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id  # Add document ID
            records.append(data)
        return records
    except Exception as e:
        return f"Error fetching content hub data: {str(e)}"
    

def add_content_hub_data(user_gmail, site_url, PRIORITY, NAME, BRIEF,
                         PRIMARY_KEYWORD, FUNNEL_STAGE, STATUS, LIVE_URL, LAST_UPDATED):
    """
    Add content hub data for a specific user and site
    """
    try:
        doc_ref = db.collection('content_hub').document()
        doc_ref.set({
            'site_url': site_url,
            'user_gmail': user_gmail,
            'PRIORITY': PRIORITY,
            'NAME': NAME,
            'BRIEF': BRIEF,
            'PRIMARY KEYWORD': PRIMARY_KEYWORD,
            'FUNNEL STAGE': FUNNEL_STAGE,
            'STATUS': STATUS,
            'LIVE URL': LIVE_URL,
            'LAST UPDATED': LAST_UPDATED
        })
        return True
    except Exception as e:
        return f"Error adding content hub data: {str(e)}"

def delete_content_hub_data(doc_id, email):
    try:
        doc_ref = db.collection('content_hub').document(doc_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict()['user_gmail'] == email:
            doc_ref.delete()
            return True
        else:
            return False
    except Exception as e:
        return f"Error deleting content hub data: {str(e)}"
    
def update_content_hub_data(user_gmail, site_url, PRIORITY, NAME, BRIEF,
                         PRIMARY_KEYWORD, FUNNEL_STAGE, STATUS, LIVE_URL, LAST_UPDATED, doc_id):
    """
    Update content hub data for a specific user and site
    """
    try:
        doc_ref = db.collection('content_hub').document(doc_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict()['user_gmail'] == user_gmail:
            doc_ref.update({
                'site_url': site_url,
                'user_gmail': user_gmail,
                'PRIORITY': PRIORITY,
                'NAME': NAME,
                'BRIEF': BRIEF,
                'PRIMARY KEYWORD': PRIMARY_KEYWORD,
                'FUNNEL STAGE': FUNNEL_STAGE,
                'STATUS': STATUS,
                'LIVE URL': LIVE_URL,
                'LAST UPDATED': LAST_UPDATED
            })
            return True
        else:
            return False
    except Exception as e:
        return f"Error updating content hub data: {str(e)}"
