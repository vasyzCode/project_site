from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .db_session import create_session, global_init
from .users import User
from datetime import datetime

main = Blueprint('main', __name__)
global_init("db/users.db")


@main.route('/')  # основная страница
def index():
    session = create_session()
    users = session.query(User).all()
    return render_template('../templates/index.html', users_count=len(users))


@main.route('/profile')  # профиль
@login_required
def profile():
    values = {'id_user': current_user.id, 'name_user': current_user.name, 'surname_user': current_user.surname,
              'bdate_user': f"{current_user.bdate.day}.{current_user.bdate.month}.{current_user.bdate.year}",
              'position_user': current_user.position, 'speciality_user': current_user.speciality,
              'address_user': current_user.address, 'email_user': current_user.email,
              'confirmed': current_user.is_confirm}
    return render_template('../templates/profile.html', **values)


@main.route('/profile', methods=["POST"])  # редактирование профиля
@login_required
def profile_post():
    session = create_session()
    user = session.query(User).get(current_user.id)
    user.name = request.form.get("name")
    user.surname = request.form.get("surname")
    user.bdate = datetime.strptime(request.form.get("bdate"),
                                   '%d.%m.%Y')
    user.position = request.form.get("position")
    user.speciality = request.form.get("speciality")
    user.address = request.form.get("address")
    user.email = request.form.get("email")
    session.commit()
    return redirect(url_for('main.profile'))


@main.route('/profile/<int:user_id>')  # профиль по id
@login_required
def profile_by_id(user_id):
    if current_user.id == user_id:
        return redirect(url_for('main.profile'))
    session = create_session()
    user = session.query(User).get(user_id)
    values = {'id_user': user.id, 'name_user': user.name, 'surname_user': user.surname,
              'bdate_user': f"{user.bdate.day}.{user.bdate.month}.{user.bdate.year}", 'position_user': user.position,
              'speciality_user': user.speciality, 'address_user': user.address, 'email_user': user.email}
    return render_template('../templates/profile.html', **values)


@main.route('/search', methods=["POST"])  # поиск пользоваателей
@login_required
def search_post():
    session = create_session()
    users = session.query(User).filter(User.name.ilike("%" + request.form.get('request') + "%") | User.surname
                                       .ilike("%" + request.form.get('request') + "%")).all()
    users_lst = [[user.id, user.name, user.surname, user.speciality] for user in users]
    return render_template('../templates/search.html', users=users_lst, count=len(users_lst))


@main.route('/all_users')  # поиск пользоваателей
@login_required
def all_users():
    session = create_session()
    users = session.query(User).all()
    users_lst = [[user.id, user.name, user.surname, user.speciality] for user in users]
    return render_template('../templates/all_users.html', users=users_lst, count=len(users_lst))
