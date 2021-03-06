# auth.py

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Hospital, PatientWeight, MNAForm, MUSTForm, MNST20Form, NRSForm # Patient, Doctor,
from . import db
from . import mail
import json
from sqlalchemy import func
import datetime
import pickle
import numpy as np
from os.path import join, dirname, realpath
from flask_mail import  Message
import random

auth = Blueprint('auth', __name__)

# MNST20 - Predictor
# dt_mnst20 = 'models/dt_msnt20_all.sav'
dt_mnst20 = 'models/dt_msnt20_total_score.sav'
mnst20_predictor = pickle.load(open(join(dirname(realpath(__file__)),dt_mnst20), 'rb'))
mnst20_class = ['Low Risk', 'Medium Risk', 'High Risk']

# MUST - Predictor
# dt_must = 'models/dt_must_all.sav'
dt_must = 'models/dt_must_total_score.sav'
must_predictor = pickle.load(open(join(dirname(realpath(__file__)),dt_must), 'rb'))
must_class = ['Low Risk', 'Medium Risk', 'High Risk']

# MNA - Predictor
# dt_mna = 'models/dt_mna_all.sav'
dt_mna = 'models/dt_mna_total_score.sav'
mna_predictor = pickle.load(open(join(dirname(realpath(__file__)),dt_mna), 'rb'))
mna_class = ['Normal', 'Malnourished', 'At Risk']

# NRS - Predictor
# dt_nrs = 'models/dt_nrs_all.sav'
dt_nrs = 'models/dt_nrs_total_score.sav'
nrs_predictor = pickle.load(open(join(dirname(realpath(__file__)),dt_nrs), 'rb'))
nrs_class = ['Normal','At risk']



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
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

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
        height = data.get('height',None)
        weight = data.get('weight',None)

        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            return jsonify(response(message = 'Email address already exists'))

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        new_user = User(email=email, name=name,
                        password=generate_password_hash(password, method='sha256'),
                        user_type = user_type, mobile=mobile, dob = dob,
                        gender = gender, address = address, hospital_id = hospital_id,
                        agreement_check = agreement_check,height = height,
                        weight = weight)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify(response(True,'User added successfully'))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

@auth.route('/update_profile', methods=['PUT'])
def update_profile_put():
    try:
        result = []

        data = json.loads(request.data)
        email = data.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify(response(False,'User not found'))
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
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

@auth.route('/profile', methods=['GET'])
def profile_get():
    try:
        data = json.loads(request.data)
        email = data.get('email')
        result = []
        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if not user:
            return jsonify(response(message='User not found'))

        result = [{i.name: getattr(user, i.name) for i in user.__table__.columns if i.name != 'password'}]
        result[0]['hospital_name'] = ''
        if user.hospital_id:
            result[0]['hospital_name'] = Hospital.query.filter_by(id=user.hospital_id).first().name

        return jsonify(response(True,result=result))
    except Exception as e:
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

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
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

@auth.route('/user_list', methods=['GET'])
def user_list_get():
    try:
        user_type = request.args.get('user_type','')
        hospital_id = request.args.get('hospital_id','')
        if user_type in ['patient','doctor','admin']:

            user_list = User.query.filter_by(user_type=user_type).all() if not hospital_id else User.query.filter_by(user_type=user_type,hospital_id = hospital_id).all()
            result = []
            for idx, user in enumerate(user_list):
                result.append({i.name: getattr(user, i.name) for i in user.__table__.columns if i.name not in ['password']})

                result[idx]['hospital_name'] = ''
                if user.hospital_id:
                    result[idx]['hospital_name'] = Hospital.query.filter_by(id=user.hospital_id).first().name

            return jsonify(response(True,'',result))
        else:
            return jsonify(response(False,'Invalid User Type provided.'))


    except Exception as e:
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

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
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

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
            data = json.loads(request.data)
            id = data.get('id','')
            result = []
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
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

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
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

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
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

@auth.route('/patient_weight',methods=['GET','POST'])
def patient_weight():
    try:
        if request.method =='GET':
            patient_id = request.args.get('patient_id','')
            # app.logger.debug(patient_id)
        else:
            data = json.loads(request.data)
            patient_id = data.get('patient_id',None)

        result = []
        if not bool(User.query.filter_by(id = patient_id, user_type='patient').first()):
            return jsonify(response(False,'Patient does not exists'))

        if request.method =='GET':

            patient_details = PatientWeight.query.filter_by(patient_id = patient_id).all()
            for patient in patient_details:
                result.append({i.name: getattr(patient, i.name) for i in patient.__table__.columns})

            return jsonify(response(True,result=result))

        if request.method == 'POST':

            month = data.get('month','')
            height = data.get('height','')
            weight = data.get('weight','')

            patient_details = PatientWeight.query.filter_by(patient_id = patient_id, month = month).first()
            if bool(patient_details):
                for i in patient_details.__table__.columns:
                    if i.name in [*data]:
                        patient_details.__setattr__(i.name, data[i.name])
                db.session.commit()

                return jsonify(response(True,'Details added successfully'))



            patient_details = PatientWeight(patient_id = patient_id, month = month,
                                            height = height, weight = weight)

            db.session.add(patient_details)
            db.session.commit()

            return jsonify(response(True,'Details added successfully'))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

@auth.route('/form/must',methods=['GET','POST'])
def must_form():
    try:

        if request.method =='GET':
            patient_id = request.args.get('patient_id','')
        else:
            data = json.loads(request.data)
            patient_id = data.get('patient_id',None)
        result = []

        if not bool(User.query.filter_by(id=patient_id, user_type='patient').first()):
            return jsonify(response(False, 'Patient does not exists'))

        if request.method == 'GET':
            patient_details = MUSTForm.query.filter_by(patient_id=patient_id).all()
            for patient in patient_details:
                result.append({i.name: getattr(patient, i.name) for i in patient.__table__.columns})

            return jsonify(response(True, result=result))

        if request.method == 'POST':
            must = MUSTForm()
            for i in must.__table__.columns:
                if i.name in [*data]:
                    must.__setattr__(i.name, data[i.name])
            db.session.add(must)
            db.session.commit()

            return jsonify(response(True,'Details added successfully'))

    except Exception as e:
        return jsonify(response(False,'Some unknown error occurred. Please try again after sometime.',[{"traceback":str(e)}]))

@auth.route('/form/mna',methods=['GET','POST'])
def mna_form():
    try:
        if request.method =='GET':
            patient_id = request.args.get('patient_id','')
        else:
            data = json.loads(request.data)
            patient_id = data.get('patient_id',None)
        result = []

        if not bool(User.query.filter_by(id=patient_id, user_type='patient').first()):
            return jsonify(response(False, 'Patient does not exists'))

        if request.method == 'GET':
            patient_details = MNAForm.query.filter_by(patient_id=patient_id).all()
            for patient in patient_details:
                result.append({i.name: getattr(patient, i.name) for i in patient.__table__.columns})

            return jsonify(response(True, result=result))

        if request.method == 'POST':
            mna = MNAForm()
            for i in mna.__table__.columns:
                if i.name in [*data]:
                    mna.__setattr__(i.name, data[i.name])
            db.session.add(mna)
            db.session.commit()

            return jsonify(response(True, 'Details added successfully'))

    except Exception as e:
        return jsonify(
            response(False, 'Some unknown error occurred. Please try again after sometime.', {"traceback": str(e)}))

@auth.route('/form/nrs',methods=['GET','POST'])
def nrs_form():
    try:
        if request.method =='GET':
            patient_id = request.args.get('patient_id','')
        else:
            data = json.loads(request.data)
            patient_id = data.get('patient_id',None)
        result = []

        if not bool(User.query.filter_by(id=patient_id, user_type='patient').first()):
            return jsonify(response(False, 'Patient does not exists'))

        if request.method == 'GET':
            patient_details = NRSForm.query.filter_by(patient_id=patient_id).all()
            for patient in patient_details:
                result.append({i.name: getattr(patient, i.name) for i in patient.__table__.columns})

            return jsonify(response(True, result=result))

        if request.method == 'POST':
            mna = NRSForm()
            user = User.query.filter_by(id=patient_id).first()
            if 'disease_name' in data:
                user.__setattr__('disease_name', data['disease_name'])
            # db.session("UPDATE user SET disease_name = "+ data['disease_name'] + " WHERE id = " + patient_id).execute()
            for i in mna.__table__.columns:
                if i.name in [*data]:
                    print(i.name)
                    if i.name=='disease_name':
                        print('shubham')


                    else:
                        mna.__setattr__(i.name, data[i.name])
            db.session.add(mna)
            db.session.commit()

            return jsonify(response(True, 'Details added successfully'))

    except Exception as e:
        return jsonify(
            response(False, 'Some unknown error occurred. Please try again after sometime.', {"traceback": str(e)}))

@auth.route('/form/mnst',methods=['GET','POST'])
def mnst_form():
    try:
        if request.method =='GET':
            patient_id = request.args.get('patient_id','')
        else:
            data = json.loads(request.data)
            patient_id = data.get('patient_id',None)
        result = []

        if not bool(User.query.filter_by(id=patient_id, user_type='patient').first()):
            return jsonify(response(False, 'Patient does not exists'))

        if request.method == 'GET':
            patient_details = MNST20Form.query.filter_by(patient_id=patient_id).all()
            for patient in patient_details:
                result.append({i.name: getattr(patient, i.name) for i in patient.__table__.columns})

            return jsonify(response(True, result=result))

        if request.method == 'POST':
            mna = MNST20Form()
            for i in mna.__table__.columns:
                if i.name in [*data]:
                    mna.__setattr__(i.name, data[i.name])
            db.session.add(mna)
            db.session.commit()

            return jsonify(response(True, 'Details added successfully'))

    except Exception as e:
        return jsonify(
            response(False, 'Some unknown error occurred. Please try again after sometime.', {"traceback": str(e)}))

@auth.route('/form/data',methods=['GET'])
def form_data():
    try:
        result = {}

        patient_id = request.args.get('patient_id','')
        date = request.args.get('date','')

        if not bool(User.query.filter_by(id=patient_id, user_type='patient').first()):
            return jsonify(response(False, 'Patient does not exists'))

        if not date:
            return jsonify(response(False, 'Date not provided'))

        date = [int(i) for i in date.split('-')]

        must = MUSTForm.query.filter(patient_id == patient_id,
                                     func.DATE(MUSTForm.timestamp) == datetime.date(date[0], date[1], date[2])).order_by(MUSTForm.id.desc()).all()
        mna = MNAForm.query.filter(patient_id == patient_id,
                                     func.DATE(MNAForm.timestamp) == datetime.date(date[0], date[1], date[2])).order_by(MNAForm.id.desc()).all()
        nrs = NRSForm.query.filter(patient_id == patient_id,
                                     func.DATE(NRSForm.timestamp) == datetime.date(date[0], date[1], date[2])).order_by(NRSForm.id.desc()).all()
        mnst20 = MNST20Form.query.filter(patient_id == patient_id,
                                     func.DATE(NRSForm.timestamp) == datetime.date(date[0], date[1], date[2])).order_by(MNST20Form.id.desc()).all()
        result['must']= [{i.name: getattr(x, i.name) for i in x.__table__.columns} for x in must] if must else []
        result['mna']= [{i.name: getattr(x, i.name) for i in x.__table__.columns} for x in mna] if mna else []
        result['nrs']= [{i.name: getattr(x, i.name) for i in x.__table__.columns} for x in nrs] if nrs else []
        result['mnst20']= [{i.name: getattr(x, i.name) for i in x.__table__.columns} for x in mnst20] if nrs else []

        return jsonify(response(True, result=result))

    except Exception as e:
        return jsonify(
            response(False, 'Some unknown error occurred. Please try again after sometime.', {"traceback": str(e)}))

@auth.route('/form/prediction',methods=['POST'])
def form_predict():
    try:
        result = []
        form_name = request.args.get('form_name','')
        form_data = json.loads(request.data)

        print(form_name)
        print(form_data)

        if form_name == 'mnst20':
            model_input = form_data['total_score']
            prediction = mnst20_class[mnst20_predictor.predict(np.array(float(model_input)).reshape(1, -1))[0]]

            # model_input = [float(v) for v in form_data.values()]
            # prediction = mnst20_class[mnst20_predictor.predict(np.array(model_input).reshape(1, -1))[0]]
            result.append({'prediction':prediction})

        if form_name == 'must':
            model_input = form_data['total_score']
            prediction = must_class[must_predictor.predict(np.array(float(model_input)).reshape(1, -1))[0]]

            # model_input = [float(v) for v in form_data.values()]
            # prediction = must_class[must_predictor.predict(np.array(model_input).reshape(1, -1))[0]]
            result.append({'prediction':prediction})

        if form_name == 'mna':
            model_input = form_data['total_score']
            prediction = mna_class[mna_predictor.predict(np.array(float(model_input)).reshape(1, -1))[0]]

            # model_input = [float(v) for v in form_data.values()]
            # prediction = mna_class[mna_predictor.predict(np.array(model_input).reshape(1, -1))[0]]
            result.append({'prediction':prediction})

        if form_name == 'nrs':
            model_input = form_data['total_score']
            prediction = nrs_class[nrs_predictor.predict(np.array(float(model_input)).reshape(1, -1))[0]]

            # model_input = [float(v) for v in form_data.values()]
            # prediction = nrs_class[nrs_predictor.predict(np.array(model_input).reshape(1, -1))[0]]
            result.append({'prediction':prediction})

        return jsonify(response(True, result=result))

    except Exception as e:
        return jsonify(
            response(False, 'Some unknown error occurred. Please try again after sometime.', {"traceback": str(e)}))


@auth.route('/user/comorbity-stat',methods=['GET'])
def comorbityStat():
    try:
        comorbityData = []
        maleFemaleData = []
        doctorCount = []
        patientCount = []
        result = db.session.execute('select disease_name, COUNT(*) from user GROUP BY disease_name')
        for row in result:
            comorbityData.append([row[0],row[1]])
        result = db.session.execute('select gender, COUNT(*) from user GROUP BY gender')
        for row in result:
            maleFemaleData.append([row[0], row[1]])
        result = db.session.execute('select  COUNT(*) from user WHERE "user_type" = "doctor"')

        for row in result:
            doctorCount.append(row[0])
        result = db.session.execute('select  COUNT(*) from user WHERE "user_type" = "patient"')
        for row in result:
            patientCount.append(row[0])

        json_dict = dict()
        json_dict['success'] = True
        json_dict['message'] = 'Success'
        json_dict['result'] = {
            'comorbityData' : comorbityData,
            'maleFemaleRation':maleFemaleData,
            "patientCount":patientCount,
            "doctorCount":doctorCount
        }
        return jsonify(json_dict)


    except Exception as e:
        return jsonify(
            response(False, 'Some unknown error occurred. Please try again after sometime.', {"traceback": str(e)}))

@auth.route('/user/forgotPassord',methods=['GET'])
def forgot_password():
    try:
        comorbityData = []
        maleFemaleData = []
        hospitalWiseData = []
        doctorWiseDara = []
        patient_email= request.args.get('email', '')
        user = User.query.filter_by(email=patient_email).first()

        if not user:
            return jsonify(response(False, 'User not found'))

        otp = random.randint(1111,9999)

        user.__setattr__('otp', otp)
        msg = Message(subject="Hello",
                      sender=user.name,
                      recipients=[user.email],  # replace with your email for testing
                      body="Please Use OTP: "+str(otp)+" for password reset. \n Team Health App")
        mail.send(msg)

        db.session.commit()

        json_dict = dict()
        json_dict['success'] = True
        json_dict['message'] = 'Mail Send Successfully'
        json_dict['result'] = { "otp": otp}
        return jsonify(json_dict)


    except Exception as e:
        return jsonify(
            response(False, 'Some unknown error occurred. Please try again after sometime.', {"traceback": str(e)}))

@auth.route('/user/changePassord',methods=['POST'])
def update_password():
    try:
        data = json.loads(request.data)
        user = User.query.filter_by(email=data['email']).first()

        if not user:
            return jsonify(response(False, 'User not found'))

        print(str(user.otp),data['otp'],str(user.otp) != str(data['otp']))
        if str(user.otp) != str(data['otp']):
            return jsonify(response(False, 'Wrong OTP'))

        user.__setattr__('password', generate_password_hash(data['password']))
        db.session.commit()



        json_dict = dict()
        json_dict['success'] = True
        json_dict['message'] = 'Password Changed Successfully'
        json_dict['result'] = { }
        return jsonify(json_dict)


    except Exception as e:
        return jsonify(
            response(False, 'Some unknown error occurred. Please try again after sometime.', {"traceback": str(e)}))
