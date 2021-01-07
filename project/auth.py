# auth.py

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Hospital # Patient, Doctor,
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

        #Append Hospital Name from Hospital table
        result[0]['hospital_name'] = ''
        if user.hospital_id:
            result[0]['hospital_name'] = Hospital.query.filter_by(id=user.hospital_id).first().name

        return jsonify(response(True,'Login Successful',result))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))

@auth.route('/signup', methods=['POST'])
def signup_post():
    try:
        data = json.loads(request.data)

        email = data.get('email','')
        name = data.get('name','')
        password = data.get('password','')
        user_type = data.get('user_type','')
        mobile = data.get('mobile','')
        dob = data.get('dob','')
        gender = data.get('gender','')
        address = data.get('address','')
        hospital_id = data.get('hospital_id','')
        agreement_check = data.get('agreement_check',False)
        is_active = data.get('is_active',False)

        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            return jsonify(response(message = 'Email address already exists'))

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        new_user = User(email=email, name=name,
                        password=generate_password_hash(password, method='sha256'),
                        user_type = user_type, mobile=mobile, dob = dob,
                        gender = gender, address = address, hospital_id = hospital_id,
                        agreement_check = agreement_check)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify(response(True,'User added successfully'))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))

@auth.route('/update_profile', methods=['PUT'])
def update_profile_put():
    try:
        result = []

        data = json.loads(request.data)
        email = data.get('email')
        user = User.query.filter_by(email=email).first()

        # user_type = user.user_type
        # if user_type in ['patient', 'doctor']:
        #     row_obj = eval(f'user.{user.user_type}')

        for i in user.__table__.columns:
            if i.name in [*data['update']]:
                user.__setattr__(i.name, data['update'][i.name])

        result.append({i.name: getattr(user, i.name) for i in user.__table__.columns if i.name not in ['id','password']})
        db.session.commit()

        return jsonify(response(True,'Updated successfully!!',result))
    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))

@auth.route('/profile', methods=['GET'])
def profile_get():
    try:
        data = json.loads(request.data)
        email = data.get('email')
        result = []
        import pdb; pdb.set_trace()
        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if not user:
            return jsonify(response(message='User not found'))

        result = [{i.name: getattr(user, i.name) for i in user.__table__.columns if i.name != 'password'}]
        result[0]['hospital_name'] = ''
        if user.hospital_id:
            result[0]['hospital_name'] = Hospital.query.filter_by(id=user.hospital_id).first().name

        return jsonify(response(True,result=result))
    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))

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

            return jsonify(response(True,'User Activated Successfully!'))


    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))

@auth.route('/user_list', methods=['GET'])
def user_list_get():
    try:
        user_type = request.args.get('user_type','')
        if user_type in ['patient','doctor','admin']:
            user_list = User.query.filter_by(user_type=user_type).all()
            result = []
            for idx, user in enumerate(user_list):
                result.append({i.name: getattr(user, i.name) for i in user.__table__.columns if i.name not in ['id','password']})

                result[idx]['hospital_name'] = ''
                if user.hospital_id:
                    result[idx]['hospital_name'] = Hospital.query.filter_by(id=user.hospital_id).first().name

            return jsonify(response(True,'',result))
        else:
            return jsonify(response(False,'Invalid User Type provided.'))


    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))

@auth.route('/delete_user',methods=['POST','DELETE'])
def user_delete():
    try:
        data = json.loads(request.data)
        result = []
        email = data.get('email',None)
        if email:
            user = User.query.filter_by(email=email).first()
            db.session.delete(user)
            db.session.commit()
            return jsonify(response(True,'User deleted successfully',result))

        return jsonify(response(False,'User deost not exists'))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))

@auth.route('/hospital',methods=['GET',"POST","PUT"])
def hospital_data():
    try:
        if request.method =='GET':
            result = []
            hospital_list = Hospital.query.all()
            for hospital in hospital_list:
                result.append({i.name: getattr(hospital, i.name) for i in hospital.__table__.columns})

            return jsonify(response(True,'',result))

        if request.method == 'POST':
            data = json.loads(request.data)
            name = data.get('name','')
            address = data.get('address','')
            website = data.get('website','')

            new_hospital = Hospital(name=name, address = address, website = website)

            db.session.add(new_hospital)
            db.session.commit()

            return jsonify(response(True,'Hospital added successfully'))

        if request.method == 'PUT': #TODO: Fix CORS error
            if id:
                hospital = Hospital.query.filter_by(id=id).first()
                for i in hospital.__table__.columns:
                    if i.name in [*data['update']]:
                        hospital.__setattr__(i.name, data['update'][i.name])

                result.append({i.name: getattr(hospital, i.name) for i in hospital.__table__.columns })
                db.session.commit()

                return jsonify(response(True,'Hospital updated successfully',result))

            return jsonify(response(False, 'Hospital ID does not exists.'))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))

@auth.route('/update_hospital',methods=['POST'])
def hospital_update():
    try:

        data = json.loads(request.data)
        result = []
        id = data.get('id',None)
        if id:
            hospital = Hospital.query.filter_by(id=id).first()
            for i in hospital.__table__.columns:
                if i.name in [*data['update']]:
                    hospital.__setattr__(i.name, data['update'][i.name])

            result.append({i.name: getattr(hospital, i.name) for i in hospital.__table__.columns })
            db.session.commit()

            return jsonify(response(True,'Hospital updated successfully',result))

        return jsonify(response(False, 'Hospital ID does not exists.'))


    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))


@auth.route('/delete_hospital',methods=['POST','DELETE'])
def hospital_delete():
    try:
        data = json.loads(request.data)
        result = []
        id = data.get('id',None)
        if id:
            hospital = Hospital.query.filter_by(id=id).first()
            user_list = User.query.filter_by(hospital_id=id).all()
            if user_list:
                for idx in range(len(user_list)):
                    user_list[idx].__setattr__('hospital_id', '')

            db.session.delete(hospital)
            db.session.commit()

            return jsonify(response(True,'Hospital deleted successfully',result))

        return jsonify(response(False, 'Hospital ID does not exists.'))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occured. Please try again after sometime.',{"traceback":str(e)}))
