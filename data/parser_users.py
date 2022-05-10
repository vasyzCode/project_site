from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('surname', type=str, nullable=True)
parser.add_argument('name', type=str, nullable=True)
parser.add_argument('bdate', type=str, nullable=True)
parser.add_argument('email', type=str, nullable=True)
parser.add_argument('address', type=str, nullable=True)
parser.add_argument('position', type=str, nullable=True)
parser.add_argument('speciality', type=str, nullable=True)
parser.add_argument('hashed_password', type=str, nullable=True)
