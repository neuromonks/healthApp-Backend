# models.py

from flask_login import UserMixin
from . import db

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100),nullable=False)
    name = db.Column(db.Text,nullable=False)
    user_type = db.Column(db.String(10),nullable=False) #admin, patient, doctor
    mobile = db.Column(db.String(15),nullable=False)
    dob = db.Column(db.String(10),nullable=False)
    is_active = db.Column(db.Boolean, unique=False, default=False, nullable=False)
    # patient = db.relationship('Patient',backref='user',cascade="all,delete", uselist=False)
    # doctor = db.relationship('Doctor',backref='user',cascade="all,delete",uselist=False)
    gender = db.Column(db.String(6),nullable=False, default = '')
    address = db.Column(db.Text, default='')
    agreement_check = db.Column(db.Boolean, unique=False, default=False, nullable=False)
    hospital_id = db.Column(db.Integer,nullable = True)
    # hospital_name = db.relationship('Hospital',backref='user',cascade="all,delete",uselist=True) 


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, default='')
    address = db.Column(db.Text, default='')
    website = db.Column(db.Text, default='')



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
