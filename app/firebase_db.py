import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('fb.json')
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