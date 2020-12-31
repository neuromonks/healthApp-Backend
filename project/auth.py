# auth.py

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Patient, Doctor
from . import db
import json

auth = Blueprint('auth', __name__)

def response(status = False, message = '', result = []):
    json_dict = dict()
    json_dict['success'] = status
    json_dict['message'] = message
    json_dict['result'] = result

    return json_dict

@auth.route('/login', methods=['POST'])
def login_post():
    try:
        result = []
        data = json.loads(request.data)
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        # check if user actually exists
        # take the user supplied password, hash it, and compare it to the hashed password in database
        if not user:
            return jsonify(response(message='Invalid User ID. Please Sign Up'))

        if not check_password_hash(user.password, password):
            return jsonify(response(message = 'Please check your login details and try again.')) # if user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        result = [{i.name: getattr(user, i.name) for i in user.__table__.columns if i.name != 'password'}]

        return jsonify(response(True,'Login Successful',result))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.'))

@auth.route('/signup', methods=['POST'])
def signup_post():
    try:
        data = json.loads(request.data)

        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        user_type = data.get('user_type')
        mobile = data.get('mobile')
        dob = data.get('dob')


        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            return jsonify(response(message = 'Email address already exists'))

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        new_user = User(email=email, name=name,
                        password=generate_password_hash(password, method='sha256'),
                        user_type = user_type, mobile=mobile, dob = dob)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        #add user data based on user_type
        if user_type=='patient':
            new_patient = Patient(user=new_user,name = new_user.name, mobile = new_user.mobile)
            db.session.add(new_patient)
            db.session.commit()

        if user_type=='doctor':
            new_doctor = Doctor(user=new_user,name = new_user.name, mobile = new_user.mobile)
            db.session.add(new_doctor)
            db.session.commit()


        return jsonify(response(True,'User added successfully'))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.'))

@auth.route('/update_profile', methods=['PUT'])
def update_profile_put():
    try:
        result = []

        data = json.loads(request.data)
        email = data.get('email')
        user = User.query.filter_by(email=email).first()

        user_type = user.user_type
        if user_type in ['patient', 'doctor']:
            row_obj = eval(f'user.{user.user_type}')

            for i in row_obj.__table__.columns:
                if i.name in [*data['update']]:
                    row_obj.__setattr__(i.name, data['update'][i.name])
                    user.__setattr__(i.name, data['update'][i.name])

        result.append({i.name: getattr(row_obj, i.name) for i in row_obj.__table__.columns if i.name not in ['id','user_id']})
        db.session.commit()

        return jsonify(response(True,'Updated successfully!!',result))
    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.'))

@auth.route('/profile', methods=['GET'])
def profile_get():
    try:
        data = json.loads(request.data)
        email = data.get('email')
        result = []

        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if not user:
            return jsonify(response(message='User not found'))

        if user.user_type in ['patient', 'doctor']:
            row_obj = eval(f'user.{user.user_type}')
            result.append({i.name: getattr(row_obj, i.name) for i in row_obj.__table__.columns if i.name not in ['id','user_id']})

        return jsonify(response(True,result=result))
    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.'))

@auth.route('/inactive_user', methods=['GET','POST'])
def inactive_user_get():
    try:
        inactive_user_list = User.query.filter_by(is_active=False).all()
        if request.method == 'GET':
            result = []

            for user in inactive_user_list:
                result.append({i.name: getattr(user, i.name) for i in user.__table__.columns if i.name not in ['id','password']})

            return jsonify(response(True, result=result))

        if request.method == 'POST':
            data = json.loads(request.data)
            for idx,user in enumerate(inactive_user_list):
                if user.email in data['activate']:
                    inactive_user_list[idx].is_active = True

            db.session.commit()

            return jsonify(response(True,'Updated successfully!!'))


    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.'))
