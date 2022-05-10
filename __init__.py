from flask import Flask
from flask_login import LoginManager
from flask_restful import Api

from data.auth import auth as auth_blueprint
from data.db_session import create_session, global_init
from data.users import User
from data.users_resource import UsersResource, UsersListResource
from data.main import main as main_blueprint


def create_app():
    app = Flask(__name__)
    api = Api(app)
    app.config['SECRET_KEY'] = 'vasyz_project_lms'
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    api.add_resource(UsersResource, "/api/v2/users/<int:user_id>")
    api.add_resource(UsersListResource, "/api/v2/users")
    global_init("db/users.db")
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        session = create_session()
        user = session.query(User).get(int(user_id))
        return user

    return app


if __name__ == '__main__':
    create_app().run()
