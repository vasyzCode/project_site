from flask_restful import abort, Resource
from flask import jsonify
from .users import User
from .db_session import create_session, global_init
from .parser_users import parser
from datetime import datetime

global_init("db/users.db")


def abort_if_users_not_found(user_id):
    session = create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"Users {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_users_not_found(user_id)
        session = create_session()
        users = session.query(User).get(user_id)
        return jsonify({'users': users.to_dict(
            only=('id', 'name', 'surname', 'bdate', 'email', 'address', 'position', 'hashed_password'))})

    def delete(self, user_id):
        abort_if_users_not_found(user_id)
        session = create_session()
        users = session.query(User).get(user_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        abort_if_users_not_found(user_id)
        session = create_session()
        args = parser.parse_args()
        user = session.query(User).get(user_id)
        user.surname = args['surname'] if args['surname'] is not None else user.surname
        user.name = args['name'] if args['name'] is not None else user.name
        user.bdate = datetime.strptime(args['bdate'], '%d-%m-%Y') if args['bdate'] is not None else user.bdate
        user.email = args['email'] if args['email'] is not None else user.email
        user.address = args['address'] if args['address'] is not None else user.address
        user.position = args['position'] if args['position'] is not None else user.position
        user.speciality = args['speciality'] if args['speciality'] is not None else user.speciality
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'name', 'surname')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        if not args['email']:
            abort(400, message=f"No email sent")
        try:
            bdate = datetime.strptime(args['bdate'],
                                      '%d-%m-%Y')
            if not [user for user in session.query(User).filter(User.email == args['email'])]:
                user = User(
                    surname=args['surname'],
                    name=args['name'],
                    bdate=bdate,
                    email=args['email'],
                    address=args['address'],
                    position=args['position'],
                    speciality=args['speciality'],

                )
                session.add(user)
                session.commit()
                return jsonify({'success': 'OK'})
            else:
                return abort(400, message="Email already exists")
        except ValueError:
            abort(400, message=f"Does not match format 'date-month-year'")
