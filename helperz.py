
from firebase_admin import credentials, firestore, auth
import firebase_admin
import random
from uuid import uuid4



greetings = [
    'Hello World',
    'Hallo Welt',
    'Ciao Mondo',
    'Salut le Monde',
    'Hola Mundo',
]
# end of Sessions With Firebase


# function to demostrate monitoring sessions with firestore - probably will not be used as we are using Flask for session management
@firestore.transactional
def get_session_data(transaction, session_id, collection_name="session"):

    """ Looks up (or creates) the session with the given session_id.
        Creates a random session_id if none is provided. Increments
        the number of views in this session. Updates are done in a
        transaction to make sure no saved increments are overwritten.
    """
    if session_id is None:
        session_id = str(uuid4())   # Random, unique identifier
    
    doc_ref = collection_name.document(document_id=session_id)
    doc = doc_ref.get(transaction=transaction)


    if doc.exists:
        session = doc.to_dict()
    else:
        session = {
            'greeting': random.choice(greetings),
            'views': 0
        }

    session['views'] += 1   # This counts as a view
    transaction.set(doc_ref, session)
    
    session['session_id'] = session_id
    return session
