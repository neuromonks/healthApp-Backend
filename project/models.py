# models.py

from flask_login import UserMixin
from . import db

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.Text, nullable=False)
    user_type = db.Column(db.String(10), nullable=False) #admin, patient, doctor
    mobile = db.Column(db.String(15), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, unique=False, default=False, nullable=False)
    # patient = db.relationship('Patient',backref='user',cascade="all,delete", uselist=False)
    # doctor = db.relationship('Doctor',backref='user',cascade="all,delete",uselist=False)
    gender = db.Column(db.String(6), nullable=False, default='')
    address = db.Column(db.Text, default='')
    agreement_check = db.Column(db.Boolean, unique=False, default=False, nullable=False)
    hospital_id = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    # hospital_name = db.relationship('Hospital',backref='user',cascade="all,delete",uselist=True)


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, default='')
    address = db.Column(db.Text, default='')
    website = db.Column(db.Text, default='')


class PatientWeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=True) #FK
    month = db.Column(db.String(6), nullable=True) #MMYYYY
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)


class MUSTForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    patient_id = db.Column(db.Integer, nullable=True)
    nutrient_intake = db.Column(db.Boolean, nullable=True)
    bmi = db.Column(db.Float, nullable=True)
    bmi_score = db.Column(db.Float, nullable=True)
    weight_change_percentage = db.Column(db.Float, nullable=True)
    weight_change_score = db.Column(db.Float, nullable=True)
    finalScore = db.Column(db.Float, nullable=True)

class MNAForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    patient_id = db.Column(db.Integer, nullable=True)
    questionA = db.Column(db.Float, nullable=True)
    questionB = db.Column(db.Float, nullable=True)
    questionC = db.Column(db.Float, nullable=True)
    questionD = db.Column(db.Float, nullable=True)
    questionE = db.Column(db.Float, nullable=True)
    questionF = db.Column(db.Float, nullable=True)
    questionG = db.Column(db.Float, nullable=True)
    questionH = db.Column(db.Float, nullable=True)
    questionI = db.Column(db.Float, nullable=True)
    questionJ = db.Column(db.Float, nullable=True)
    questionK = db.Column(db.Float, nullable=True)
    questionK1 = db.Column(db.Float, nullable=True)
    questionK2 = db.Column(db.Float, nullable=True)
    questionK3 = db.Column(db.Float, nullable=True)
    questionL = db.Column(db.Float, nullable=True)
    questionM = db.Column(db.Float, nullable=True)
    questionN = db.Column(db.Float, nullable=True)
    questionO = db.Column(db.Float, nullable=True)
    questionP = db.Column(db.Float, nullable=True)
    assessmentScore = db.Column(db.Float, nullable=True)
    screeningScore = db.Column(db.Float, nullable=True)
    finalScore = db.Column(db.Float, nullable=True)


class NRSForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    patient_id = db.Column(db.Integer, nullable=True)
    disease = db.Column(db.Float, nullable=True)
    nutritionStatus = db.Column(db.Float, nullable=True)
    bmiIndicator = db.Column(db.Float, nullable=True)
    weightChange = db.Column(db.Float, nullable=True)
    dieteryIntakeLost = db.Column(db.Float, nullable=True)
    illFlag = db.Column(db.Float, nullable=True)
    finalResult = db.Column(db.String, nullable=True)
    finalScore = db.Column(db.Float, nullable=True)

class MNST20Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    patient_id = db.Column(db.Integer, nullable=True)
    bmi = db.Column(db.Float, nullable=True)
    nutritionHealth = db.Column(db.Float, nullable=True)
    nutritionStatus = db.Column(db.Float, nullable=True)
    disease = db.Column(db.Float, nullable=True)
    mobility = db.Column(db.Float, nullable=True)
    modeOfFeeding = db.Column(db.Float, nullable=True)
    healthStatus = db.Column(db.String, nullable=True)
    finalResult = db.Column(db.String, nullable=True)
    finalScore = db.Column(db.Float, nullable=True)

# class Patient(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     name = db.Column(db.Text, default='')
#     mobile = db.Column(db.String(15),nullable=False, default ='')
#     gender = db.Column(db.String(6),nullable=False, default = '')
#     age = db.Column(db.Integer ,nullable=False, default='')
#     address = db.Column(db.Text, default='')
#     agreement_check = db.Column(db.Boolean, unique=False, default=False, nullable=False)
#
# class Doctor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     hospital = db.Column(db.Text, db.ForeignKey('hospital.name'), nullable = False)
#     name = db.Column(db.Text, default='')
#     mobile = db.Column(db.String(15),nullable=False, default ='')
#     gender = db.Column(db.String(6),nullable=False, default = '')
#     age = db.Column(db.Integer ,nullable=False, default='')
#     address = db.Column(db.Text, default='')
    # agreement_check = db.Column(db.Boolean, unique=False, default=False, nullable=False)
