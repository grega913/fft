from flask import Flask, redirect, render_template, request, make_response, session, abort, jsonify, url_for, send_from_directory
import secrets
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import timedelta
import os
from dotenv import load_dotenv
from icecream import ic
import random
from uuid import uuid4
import stripe
from flask_cors import CORS, cross_origin
from helperz import get_session_data


load_dotenv()


app = Flask(__name__, static_folder="static")
CORS(app)
app.secret_key = os.getenv('SECRET_KEY')

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Adjust session expiration as needed
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Can be 'Strict', 'Lax', or 'None'


# Stripe settings
stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"]
}

ic(stripe_keys["secret_key"])

stripe.api_key = stripe_keys["secret_key"]

YOUR_DOMAIN = 'http://localhost:5000'
########################################

# Firebase Admin SDK setup
cred = credentials.Certificate("firebase_auth.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
sessions = db.collection('sessions')

########################################
@app.before_request
def before_request():
    # Code to execute before all routes . . here we are checking session object from flask-session
    ic(f"Check session before each route: {session}")

########################################
""" Authentication and Authorization """

# Decorator for routes that require authentication
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if 'user' not in session:
            return redirect(url_for('login'))
        
        else:
            return f(*args, **kwargs)
        
    return decorated_function


@app.route('/auth', methods=['POST'])
def authorize():
    ic("authorize")
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return "Unauthorized", 401
    token = token[7:]  # Strip off 'Bearer ' to get the actual token

    try:
        decoded_token = auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=60) # Validate token here
        ic(decoded_token)
        session['user'] = decoded_token # Add user to session
        return redirect(url_for('dashboard'))
    except:
        return "Unauthorized", 401

#####################
""" Public Routes """

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')

@app.route('/signup')
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('signup.html')

@app.route('/reset-password')
def reset_password():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('forgot_password.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    ic("privacy")
    return render_template('privacy.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the user from session
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)  # Optionally clear the session cookie
    # response.set_cookie('session_id', '', expires=0) # Optionally clear the session cookie that was made in /sess route
    return response


### my routes


##############################################

""" Private Routes (Require authorization) """

@app.route('/dashboard')
@auth_required
def dashboard():
    return render_template('dashboard.html', session = session)



# region myRoutes  . .  

#### Route for testing sessions implementation with Firebase based on https://cloud.google.com/python/docs/getting-started/session-handling-with-firestore
@app.route('/sess', methods=['GET'])
def sess():
    template = '<body>{} views for "{}"</body>'

    transaction = db.transaction()
    session = get_session_data(transaction, request.cookies.get('session_id'), collection_name=sessions)
    ic(session)

    resp = make_response(template.format(
        session['views'],
        session['greeting']
        )
    )
    resp.set_cookie('session_id', session['session_id'], httponly=True)
    return resp

@app.route('/get_session')
def get_session():
    return jsonify(dict(session))


# Stripe test
@app.route("/stripe123")
def stripe123():
    return render_template("stripe123.html")


@app.route("/stripe_config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)


@app.route("/stripe_checkout")
def stripe_checkout():
    return render_template("stripe_checkout.html")


@app.route("/stripe_checkout2")
def stripe_checkout2():
    return render_template("stripe_checkout2.html")


@app.route('/create-checkout-session', methods=['POST'])
@cross_origin(origin="*", allow_headers=["Content-Type", "Authorization"])
def create_checkout_session():

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1R17DJB4j30g5cZMjWNlbREF',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/stripe_success',
            cancel_url=YOUR_DOMAIN + '/stripe_cancel'
        )

        ic(checkout_session)

        return jsonify({"sessionId": checkout_session.id})

        

    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)
    


@app.route('/session-status', methods=['GET'])
def session_status():
  session = stripe.checkout.Session.retrieve(request.args.get('session_id'))

  return jsonify(status=session.status, customer_email=session.customer_details.email)




@app.route("/stripe_success")
def success():
    return render_template("stripe_success.html")


@app.route("/stripe_cancelled")
def cancelled():
    return render_template("stripe_cancelled.html")



@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")



    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        ic("Payment was successful.")
        # TODO: run some custom code here


        if 'user' not in session:
            ic("wee do not have user in session")
        else:
            loggedInUser = session['user']
            ic("we have loggedInUser")
            ic(loggedInUser)


    return "Success", 200


# Route to serve static files from the 'my_web_app' subdirectory
@app.route('/my_web_app/<path:filename>')
def serve_static(filename):
    return send_from_directory('static/my_web_app', filename)


# endregion




if __name__ == '__main__':
    ic(stripe_keys)

    app.run(debug=True)