from flask import Blueprint, render_template, redirect, url_for, request, flash
from .db_session import create_session, global_init
from .users import User
from datetime import datetime, timedelta
from flask_login import login_user, logout_user
import jwt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

jwt_sicret_code = 'encode_tokens_lms_vasyz'
global_init("db/users.db")
auth = Blueprint('auth', __name__)


def send_email(toaddr, header, body):
    fromaddr = "site_recovery@mail.ru"
    mypass = "xYm6TpJR3ubGrwhQCNq0"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = header
    msg.attach(MIMEText(body, 'html'))
    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(fromaddr, mypass)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


@auth.route('/login')  # форма входа
def login():
    return render_template('../templates/login.html', confirmed=bool(request.form.get('confirm_email')))


@auth.route('/signup')  # форма регистрации
def signup():
    month_list = ['Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
                  'Декабрь']
    return render_template('../templates/signup.html', month_list=month_list)


@auth.route('/logout')  # выход из аккаунта
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/login', methods=['POST'])  # вход в аккаунт
def login_post():
    session = create_session()
    email = request.form.get('email')
    password = request.form.get('password')
    remember_user = True if request.form.get('remember') else False
    user = session.query(User).filter_by(email=email).first()
    if not user or not user.check_password(password):
        flash('Неверная почта/пароль.')
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember_user)
    return redirect(url_for('main.profile'))


@auth.route('/signup', methods=['POST'])  # регистрация аккаунта
def signup_post():
    session = create_session()
    name = request.form.get("name")
    surname = request.form.get("surname")
    bdate = datetime.strptime(f'{request.form.get("bday")}-{request.form.get("bmonth")}-{request.form.get("byear")}',
                              '%d-%m-%Y')
    position = request.form.get("position")
    speciality = request.form.get("speciality")
    address = request.form.get("address")
    email = request.form.get("email")
    password = request.form.get("password")
    phrase = request.form.get("phrase")
    user = session.query(User).filter_by(email=email).first()
    if user:
        flash('Электронный адрес уже существует')
        return redirect(url_for('auth.signup'))
    user_new = User(
        name=name,
        surname=surname,
        bdate=bdate,
        position=position,
        speciality=speciality,
        address=address,
        email=email
    )
    user_new.set_password(password)
    user_new.set_pharse(phrase)
    session.add(user_new)
    session.commit()
    dt = datetime.now() + timedelta(days=365)
    encoded_token = jwt.encode({'user_id': user_new.id, 'email': user_new.email, 'exp': dt, 'need_phrase': False},
                               jwt_sicret_code,
                               algorithm='HS256')
    url = f"{request.host_url}/confirm_email?token={encoded_token}"
    header = f"Подтверждение Email для {email}"
    body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
<center class="b-mail__wrapper_mr_css_attr" style="width: 100%;table-layout: fixed;">
    <table class="b-mail_mr_css_attr" align="center"
           style="border-spacing: 0;border-collapse: collapse;color: #364364;width: 100%;max-width: 580px;">
        <tbody>
        <tr style="text-align: left;" align="left">

            <td style="vertical-align: top;text-align: left;padding: 0;" align="left" valign="top">

                <table class="b-mail-grid_mr_css_attr b-mail-grid_align_center_mr_css_attr b-mail-grid_valign_bottom_mr_css_attr"
                       style="border-spacing: 0;border-collapse: collapse;color: #364364;width: 100%;">

                    <tbody>
                    <tr style="text-align: left;" align="left">

                        <td class="b-mail-grid__row_mr_css_attr"
                            style="vertical-align: top;text-align: center;font-size: 0;padding: 0;" align="center"
                            valign="top">


                            <div class="b-mail-header_mr_css_attr b-mail-header__wrapper_mr_css_attr"
                                 style="margin: 0 24px;padding: 0;">

                                <div class="b-mail-grid__column_mr_css_attr b-mail-header__logo-wrapper_mr_css_attr"
                                     style="text-align: center;float: left;max-width: 168px;vertical-align: bottom;display: inline-block;width: 100%;margin: 36px 0;padding: 0;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                                     align="center">

                                    <div class="b-mail-header__logo_mr_css_attr l-align_left_mr_css_attr"
                                         style="height: 48px;margin: 0;padding: 0;">

                                        <a href="https://www.reg.ru/?rtm_source=e-mail&amp;rtm_medium=e-mail&amp;rtm_campaign=UserPasswdRemindMultiple"
                                           target="_blank" rel=" noopener noreferrer"></a></div>
                                </div>
                                <div class="b-mail-grid__column_mr_css_attr b-mail-header__content-wrapper_mr_css_attr"
                                     style="text-align: center;float: right;width: auto !important;vertical-align: bottom;display: inline-block;margin: 0;padding: 0;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                                     align="center">

                                    <div class="l-align_right_mr_css_attr" lang="l-align_right"
                                         style="text-align: right;margin: 0;padding: 0;" align="right">

                                        <p class="b-mail-header__content_mr_css_attr"
                                           style="margin: 36px 0;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">

                                        </p>
                                        <div class="b-mail-button_mr_css_attr"
                                             style="color: #FFFFFF;text-align: center;text-decoration: none;margin: 0;padding: 0;font: bold 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                                             align="center">

                                            <div class="b-mail-button__wrapper_mr_css_attr l-align_right_mr_css_attr b-mail-header__login-button_mr_css_attr"
                                                 style="text-align: right;margin: 48px 0 36px;padding: 0;"
                                                 align="right">


                                                <a href="https://www.reg.ru/user/?rtm_source=e-mail&amp;rtm_medium=e-mail&amp;rtm_campaign=UserPasswdRemindMultiple"
                                                   class="l-color_link-blue_mr_css_attr b-mail-button_mr_css_attr b-mail-button_font_big_mr_css_attr"
                                                   target="_blank"
                                                   style="color: #1D9EF9 !important;text-align: center;text-decoration: none;font: bold 20px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                                                   rel=" noopener noreferrer">


                                                </a>


                                            </div>

                                        </div>

                                        <p></p>

                                    </div>

                                </div>

                            </div>


                        </td>

                    </tr>

                    </tbody>
                </table>

            </td>

        </tr>

        <tr style="text-align: left;" align="left">

            <td class="b-mail__content-wrapper_mr_css_attr"
                style="vertical-align: top;text-align: left;background-color: #DFE4EC;padding: 12px;" align="left"
                bgcolor="#DFE4EC" valign="top">

                <table width="100%" style="border-spacing: 0;border-collapse: collapse;color: #364364;">

                    <tbody>
                    <tr style="text-align: left;" align="left">

                        <td class="b-mail__content_mr_css_attr"
                            style="vertical-align: top;text-align: left;background-color: #FFFFFF;padding: 25px 35px;"
                            align="left" bgcolor="#FFFFFF" valign="top">


                            <img class="b-mail-pixel_mr_css_attr"
                                 src="https://proxy.imgsmail.ru?e=1652400525&amp;email=vladyar334%40mail.ru&amp;flags=0&amp;h=YmmlsyTqpxnrVlJuah8Hfw&amp;is_https=1&amp;url173=d3d3LnJlZy5ydS9taXNjL3RyYWNrX2VtYWlsP2hhc2g9JmVtYWlsX2lkPQ~~"
                                 alt="" width="1" height="1" style="display: block;width: 1px;height: 1px;border: 0;">


                            <p class="b-mail-text_mr_css_attr b-mail-text_mode_content-title_mr_css_attr"
                               style="letter-spacing: -0.02em;margin: 0 0 18px;font: bold 32px/36px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">

                                Подтверждение Email

                            </p>

                            <p class="b-mail-text_mr_css_attr"
                               style="margin: 12px 0 6px;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">

                                Для&nbsp;подтверждения вашей почты на &nbsp;сайте <a
                                    class="b-link_mr_css_attr l-color_link-blue_mr_css_attr"
                                    href="{request.host_url}"
                                    style="color: #069DFA;text-decoration: underline;font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;"
                                    target="_blank" rel=" noopener noreferrer">{request.host_url}</a> вам надо&nbsp;пройти по
                                следующей ссылке и&nbsp;следовать дальнейшим инструкциям:

                            </p>
                            <p class="b-mail-text_mr_css_attr"
                               style="margin: 12px 0 6px;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">
                                Для&nbsp;логина {email}: <a
                                    class="b-link_mr_css_attr l-color_link-blue_mr_css_attr"
                                    href="{url}"
                                    style="color: #069DFA;text-decoration: underline;font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;"
                                    target="_blank" rel=" noopener noreferrer">{url}</a>

                            </p>
                            <p class="b-mail-text_mr_css_attr"
                               style="margin: 12px 0 6px;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">
                                Эта ссылка будет действительна в&nbsp;течение одного года.</p></td>
                    </tr>
                    </tbody>
                </table>
            </td>
        </tr>
        <tr style="text-align: left;" align="left">
            <td style="vertical-align: top;text-align: left;padding: 0;" align="left" valign="top"><p
                    class="b-mail-text_mr_css_attr b-mail-text_size_tiny_mr_css_attr b-mail-text_mode_indent-top_mr_css_attr l-align_center_mr_css_attr"
                    style="text-align: center;margin: 24px 0 6px;font: 12px/18px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                    align="center">Это письмо содержит важную информацию. Оно обязательно и&nbsp;не требует отписки.</p>
                <table class="b-mail_mr_css_attr"
                       style="border-spacing: 0;border-collapse: collapse;color: #364364;width: 100%;max-width: 580px;"></table>
            </td>
        </tr>
        </tbody>
    </table>
</center>
</body>
</html>"""
    send_email(email, header, body)
    flash('На Ваш электронный адрес было отправлено письмо с ссылкой для подтверждения аккаунта.')
    return redirect(url_for('auth.login', confirm_email=False))


@auth.route('/change_password')  # новый пароль\фраза
def change_password():
    token = request.args.get('token')
    try:
        need_phrase = jwt.decode(token, jwt_sicret_code, algorithms=['HS256'])['need_phrase']
        return render_template('../templates/change_password.html', token=token, need_phrase=need_phrase)
    except jwt.exceptions.ExpiredSignatureError:
        flash("Время действия токена истекло")
        return redirect(url_for('auth.reset_password'))
    except jwt.InvalidTokenError:
        flash('Неверный токен. ')
        return redirect(url_for('auth.reset_password'))


@auth.route('/change_password', methods=['POST'])  # новый пароль\фраза
def change_password_post():
    session = create_session()
    token = request.form.get('token')
    password = request.form.get('new_password')
    new_password = request.form.get('new_password_confirm')
    phrase = request.form.get("phrase")
    try:
        decode_token = jwt.decode(token, jwt_sicret_code, algorithms=['HS256'])
        if password != new_password:
            flash('Разные пароли')
            return redirect(url_for('auth.change_password'))
        user = session.query(User).filter_by(email=decode_token['email']).first()
        user.set_password(new_password)
        if phrase:
            user.set_pharse(phrase)
        session.commit()
        return redirect(url_for('auth.login'))
    except jwt.ExpiredSignatureError:
        flash('Время истекло, попробуйте еще раз.')
        return redirect(url_for('auth.reset_password'))
    except jwt.InvalidTokenError:
        flash('Неверный токен. ')
        return redirect(url_for('auth.reset_password'))


@auth.route('/reset_password')  # восстановление пароля по фразе
def reset_password():
    return render_template('../templates/reset_password.html')


@auth.route('/reset_password', methods=['POST'])  # восстановление пароля по фразе
def reset_password_post():
    session = create_session()
    email = request.form.get("email")
    phrase = request.form.get("phrase")
    user = session.query(User).filter_by(email=email).first()
    if not user:
        flash('Аккаунт с данной почтой не найден.')
        return redirect(url_for('auth.reset_password'))
    elif not user.check_pharse(phrase):
        flash("Неверная секретная фраза.")
        return render_template('../templates/reset_password.html', phrase=True)
    dt = datetime.now() + timedelta(minutes=10)
    encoded_token = jwt.encode({'user_id': user.id, 'email': user.email, 'exp': dt, 'need_phrase': False},
                               jwt_sicret_code,
                               algorithm='HS256')
    return redirect(f"{url_for('auth.change_password')}?token={encoded_token}")


@auth.route('/recovery_email')  # восстановление пароля по почте
def recovery_email():
    return render_template('../templates/recovery_email.html')


@auth.route('/recovery_email', methods=['POST'])  # восстановление пароля по почте
def recovery_email_post():
    session = create_session()
    email = request.form.get("email")
    user = session.query(User).filter_by(email=email).first()
    if not user:
        flash('Аккаунт с данной почтой не найден.')
    dt = datetime.now() + timedelta(minutes=10)
    encoded_token = jwt.encode({'user_id': user.id, 'email': user.email, 'exp': dt, 'need_phrase': True},
                               jwt_sicret_code,
                               algorithm='HS256')
    url = f"{request.host_url}/change_password?token={encoded_token}"
    header = f"Напоминание регистрационных данных для {email}"
    body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
<center class="b-mail__wrapper_mr_css_attr" style="width: 100%;table-layout: fixed;">
    <table class="b-mail_mr_css_attr" align="center"
           style="border-spacing: 0;border-collapse: collapse;color: #364364;width: 100%;max-width: 580px;">
        <tbody>
        <tr style="text-align: left;" align="left">

            <td style="vertical-align: top;text-align: left;padding: 0;" align="left" valign="top">

                <table class="b-mail-grid_mr_css_attr b-mail-grid_align_center_mr_css_attr b-mail-grid_valign_bottom_mr_css_attr"
                       style="border-spacing: 0;border-collapse: collapse;color: #364364;width: 100%;">

                    <tbody>
                    <tr style="text-align: left;" align="left">

                        <td class="b-mail-grid__row_mr_css_attr"
                            style="vertical-align: top;text-align: center;font-size: 0;padding: 0;" align="center"
                            valign="top">


                            <div class="b-mail-header_mr_css_attr b-mail-header__wrapper_mr_css_attr"
                                 style="margin: 0 24px;padding: 0;">

                                <div class="b-mail-grid__column_mr_css_attr b-mail-header__logo-wrapper_mr_css_attr"
                                     style="text-align: center;float: left;max-width: 168px;vertical-align: bottom;display: inline-block;width: 100%;margin: 36px 0;padding: 0;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                                     align="center">

                                    <div class="b-mail-header__logo_mr_css_attr l-align_left_mr_css_attr"
                                         style="height: 48px;margin: 0;padding: 0;">

                                        <a href="https://www.reg.ru/?rtm_source=e-mail&amp;rtm_medium=e-mail&amp;rtm_campaign=UserPasswdRemindMultiple"
                                           target="_blank" rel=" noopener noreferrer"></a></div>
                                </div>
                                <div class="b-mail-grid__column_mr_css_attr b-mail-header__content-wrapper_mr_css_attr"
                                     style="text-align: center;float: right;width: auto !important;vertical-align: bottom;display: inline-block;margin: 0;padding: 0;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                                     align="center">

                                    <div class="l-align_right_mr_css_attr" lang="l-align_right"
                                         style="text-align: right;margin: 0;padding: 0;" align="right">

                                        <p class="b-mail-header__content_mr_css_attr"
                                           style="margin: 36px 0;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">

                                        </p>
                                        <div class="b-mail-button_mr_css_attr"
                                             style="color: #FFFFFF;text-align: center;text-decoration: none;margin: 0;padding: 0;font: bold 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                                             align="center">

                                            <div class="b-mail-button__wrapper_mr_css_attr l-align_right_mr_css_attr b-mail-header__login-button_mr_css_attr"
                                                 style="text-align: right;margin: 48px 0 36px;padding: 0;"
                                                 align="right">


                                                <a href="https://www.reg.ru/user/?rtm_source=e-mail&amp;rtm_medium=e-mail&amp;rtm_campaign=UserPasswdRemindMultiple"
                                                   class="l-color_link-blue_mr_css_attr b-mail-button_mr_css_attr b-mail-button_font_big_mr_css_attr"
                                                   target="_blank"
                                                   style="color: #1D9EF9 !important;text-align: center;text-decoration: none;font: bold 20px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                                                   rel=" noopener noreferrer">


                                                </a>


                                            </div>

                                        </div>

                                        <p></p>

                                    </div>

                                </div>

                            </div>


                        </td>

                    </tr>

                    </tbody>
                </table>

            </td>

        </tr>

        <tr style="text-align: left;" align="left">

            <td class="b-mail__content-wrapper_mr_css_attr"
                style="vertical-align: top;text-align: left;background-color: #DFE4EC;padding: 12px;" align="left"
                bgcolor="#DFE4EC" valign="top">

                <table width="100%" style="border-spacing: 0;border-collapse: collapse;color: #364364;">

                    <tbody>
                    <tr style="text-align: left;" align="left">

                        <td class="b-mail__content_mr_css_attr"
                            style="vertical-align: top;text-align: left;background-color: #FFFFFF;padding: 25px 35px;"
                            align="left" bgcolor="#FFFFFF" valign="top">


                            <img class="b-mail-pixel_mr_css_attr"
                                 src="https://proxy.imgsmail.ru?e=1652400525&amp;email=vladyar334%40mail.ru&amp;flags=0&amp;h=YmmlsyTqpxnrVlJuah8Hfw&amp;is_https=1&amp;url173=d3d3LnJlZy5ydS9taXNjL3RyYWNrX2VtYWlsP2hhc2g9JmVtYWlsX2lkPQ~~"
                                 alt="" width="1" height="1" style="display: block;width: 1px;height: 1px;border: 0;">


                            <p class="b-mail-text_mr_css_attr b-mail-text_mode_content-title_mr_css_attr"
                               style="letter-spacing: -0.02em;margin: 0 0 18px;font: bold 32px/36px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">

                                Восстановление пароля

                            </p>

                            <p class="b-mail-text_mr_css_attr"
                               style="margin: 12px 0 6px;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">

                                Для&nbsp;восстановления вашего пароля на&nbsp;сайте <a
                                    class="b-link_mr_css_attr l-color_link-blue_mr_css_attr"
                                    href="{request.host_url}"
                                    style="color: #069DFA;text-decoration: underline;font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;"
                                    target="_blank" rel=" noopener noreferrer">{request.host_url}</a> вам надо&nbsp;пройти по
                                следующей ссылке и&nbsp;следовать дальнейшим инструкциям:

                            </p>
                            <p class="b-mail-text_mr_css_attr"
                               style="margin: 12px 0 6px;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">
                                Для&nbsp;логина {email}: <a
                                    class="b-link_mr_css_attr l-color_link-blue_mr_css_attr"
                                    href="{url}"
                                    style="color: #069DFA;text-decoration: underline;font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;"
                                    target="_blank" rel=" noopener noreferrer">{url}</a>

                            </p>
                            <p class="b-mail-text_mr_css_attr"
                               style="margin: 12px 0 6px;font: 15px/24px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;">
                                Эта ссылка будет действительна в&nbsp;течение одного часа.</p></td>
                    </tr>
                    </tbody>
                </table>
            </td>
        </tr>
        <tr style="text-align: left;" align="left">
            <td style="vertical-align: top;text-align: left;padding: 0;" align="left" valign="top"><p
                    class="b-mail-text_mr_css_attr b-mail-text_size_tiny_mr_css_attr b-mail-text_mode_indent-top_mr_css_attr l-align_center_mr_css_attr"
                    style="text-align: center;margin: 24px 0 6px;font: 12px/18px Arial, 'Helvetica Neue', Helvetica, FreeSans, sans-serif;"
                    align="center">Это письмо содержит важную информацию. Оно обязательно и&nbsp;не требует отписки.</p>
                <table class="b-mail_mr_css_attr"
                       style="border-spacing: 0;border-collapse: collapse;color: #364364;width: 100%;max-width: 580px;"></table>
            </td>
        </tr>
        </tbody>
    </table>
</center>
</body>
</html>"""
    send_email(email, header, body)
    flash("Ссылка для восстановления пароля была отправлена на почту.")
    return render_template('../templates/recovery_email.html')


@auth.route('/confirm_email')  # подтверждение почты
def confirm_email():
    session = create_session()
    token = request.args.get("token")
    try:
        user_id = jwt.decode(token, jwt_sicret_code, algorithms=['HS256'])['user_id']
        user = session.query(User).get(user_id)
        user.is_confirm = True
        session.commit()
        flash("Email успешно подтвержден!")
        return redirect(url_for('auth.login'))
    except jwt.ExpiredSignatureError:
        flash('Время истекло, попробуйте еще раз.')
        return redirect(url_for('auth.login'))
    except jwt.InvalidTokenError:
        flash('Неверный токен. ')
        return redirect(url_for('auth.login'))
