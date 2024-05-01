from flask import Flask, render_template, request, redirect, session, url_for, send_file, make_response, \
    render_template_string
# from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required
from flask_login import LoginManager
from flask_login import UserMixin, login_user, logout_user
import enum
from flask_login import current_user
from Models import Courseworks, User
from db import db
import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
# from bs4 import BeautifulSoup
import pdfkit
import re
import json


app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///curs_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

dep_list = ["ИМО", "ПМиК", "МА", "ГиТ", "ТВиАД", "ТМОМИ"]
tutor_pos_list = ["преподаватель", "ст. преподаватель", "доцент", "профессор", "заведующий кафедрой", "другая"]

with open("prefs.json", "r") as file:
    upload_deadlines = json.load(file)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['password'])

        user = User.query.filter_by(username=request.form['username']).first()

        if user is None or not check_password_hash(user.password, request.form['password']):
            return 'неверный логин или пароль'

        login_user(user)

        return redirect(url_for('index'))
    return '''
           <form action = "" method = "post">
              <p>Логин<input type = "text" name = "username"/></p>
              <p>Пароль<input type = "text" name = "password"/></p>
              <p><input type = "submit" value = "Login"/></p>
           </form>
           '''


@app.route('/login/exit')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.query.get(int(user_id))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Message %r' % self.id


from flask import flash


@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    # TODO определять студент или препод

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    current_year = get_current_year()
    if (request.method == 'POST'):
        conditions = []
        AND_conditions = []
        OR_conditions1 = []
        OR_conditions2 = []
        print(request.form)
        from sqlalchemy import or_, and_
        if (request.form['name'] != ''):
            AND_conditions.append(Courseworks.studentName == request.form['name'])
        if (request.form['adviser-name'] != ''):
            AND_conditions.append(Courseworks.tutor_name == request.form['adviser-name'])

        if (request.form['department'] != ''):
            AND_conditions.append(Courseworks.departament == request.form['department'])

        flatten = False

        if (request.form['years'] != ''):
            years = request.form.getlist('years')
            print(years)
            if len(years) > 1:
                OR_conditions1 = [Courseworks.year == year1 for year1 in years]
            else:
                AND_conditions.append(Courseworks.year == request.form['years'])

        if (request.form['groups'] != ''):
            grps = request.form.getlist('groups')
            print(grps)
            if len(grps) > 1:
                OR_conditions2 = [Courseworks.group == grp for grp in grps]
            else:
                AND_conditions.append(Courseworks.group == request.form['groups'])

        if OR_conditions1:
            conditions = or_(*OR_conditions1), and_(*AND_conditions)
        else:
            conditions = AND_conditions
        if OR_conditions2:
            conditions = or_(*OR_conditions2), and_(*conditions)
        else:
            conditions = conditions

        if (request.form['group-method'] == 'flatten'):
            flatten = True
        # ('sort-method', 'by-student-name'), ('sort-order', 'ascending')
        if (request.form['sort-method'] == 'by-student-name'):
            if (request.form['sort-order'] == 'ascending'):
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.departament,
                                                                          Courseworks.group, Courseworks.student,
                                                                          Courseworks.studentName).all()
            else:
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.departament,
                                                                          Courseworks.group, Courseworks.student,
                                                                          Courseworks.studentName.desc()).all()
        elif (request.form['sort-method'] == 'by-adviser-name'):
            if (request.form['sort-order'] == 'ascending'):
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.departament,
                                                                          Courseworks.group, Courseworks.student,
                                                                          Courseworks.tutor_name).all()
            else:
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.departament,
                                                                          Courseworks.group, Courseworks.student,
                                                                          Courseworks.tutor_name.desc()).all()
        else:
            if (request.form['sort-order'] == 'ascending'):
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year, Courseworks.date_reg,
                                                                          Courseworks.departament,
                                                                          Courseworks.student,
                                                                          Courseworks.group).all()
            else:
                response = Courseworks.query.filter(*conditions).order_by(Courseworks.year.desc(),
                                                                          Courseworks.date_reg.desc(),
                                                                          Courseworks.departament,
                                                                          Courseworks.student,
                                                                          Courseworks.group).all()
        counter = 0

        # TODO переделать структуру
        answer = {}
        count_dict = {}
        detail_level = 1
        button_id = request.form.get('button')
        if not flatten or button_id == 'Отчет':
            for e in response:
                counter += 1
                # print(str(counter) + " " + str(e.year) + " " + e.departament + " " + e.group + " " + e.title + " " + e.studentName + " " + e.tutor_name + " " + e.student)
                year = answer.get(e.year)
                if year:
                    dep = answer[e.year].get(e.departament)
                    if dep:
                        groups = answer[e.year][e.departament].get(e.group)
                        if groups:
                            answer[e.year][e.departament][e.group].append(
                                {"title": e.title, "name": e.studentName, "tutor": e.tutor_name, "student": e.student,
                                 "in_time": e.in_time})
                        else:
                            answer[e.year][e.departament][e.group] = [{"title": e.title, "name": e.studentName,
                                                                       "tutor": e.tutor_name, "student": e.student,
                                                                       "in_time": e.in_time}]
                    else:
                        answer[e.year][e.departament] = {e.group: [{"title": e.title, "name": e.studentName,
                                                                    "tutor": e.tutor_name, "student": e.student,
                                                                    "in_time": e.in_time}]}
                else:
                    answer[e.year] = {
                        e.departament: {e.group: [{"title": e.title, "name": e.studentName,
                                                   "tutor": e.tutor_name, "student": e.student, "in_time": e.in_time}]}}
                # TODO проверить
                # if year:
                #     dep = answer.setdefault(e.year, {}).setdefault(e.departament, {})
                #     groups = dep.setdefault(e.group, [])
                #     groups.append(
                #         {"title": e.title, "name": e.studentName, "tutor": e.tutor_name, "student": e.student})
                # else:
                #     answer[e.year] = {
                #         e.departament: {e.group: [
                #             {"title": e.title, "name": e.studentName, "tutor": e.tutor_name, "student": e.student}]}
                #     }

            print(answer)
            for e in answer.keys():
                print(e)
            print('-----')

            for _year in answer.keys():
                recs_per_year = 0
                count_dict[_year] = {}
                for _dep in answer[_year].keys():
                    recs_per_dep = 0
                    count_dict[_year][_dep] = {}
                    for _group in answer[_year][_dep].keys():
                        recs_per_group = len(answer[_year][_dep][_group])
                        print(recs_per_group)
                        # answer[_year][_dep][_group]['count'] = recs_per_group
                        count_dict[_year][_dep][_group] = recs_per_group
                        recs_per_dep += recs_per_group
                    count_dict[_year][_dep]['count'] = recs_per_dep
                    recs_per_year += recs_per_dep
                count_dict[_year]['count'] = recs_per_year

            print(count_dict)
        else:
            curs = {}
            for e in response:
                curs[str(e.group)[2:3]] = 1
            print(curs)

            if "6" in curs.keys() and len(curs.keys()) == 1:
                detail_level = 3
            elif "4" in curs.keys() and len(curs.keys()) == 1:
                detail_level = 2
            answer = response

        if button_id == 'Отчет':
            path_wkhtmltopdf = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
            html = render_template("report_pdf_template1.html", data=answer, file_exists=file_exists,
                                   count_data=count_dict)
            # print(html)
            if not os.path.exists(f"temp/{current_user.username}"):
                os.makedirs(f"temp/{current_user.username}")
            output_file = f'temp/{current_user.username}/output.pdf'

            a = pdfkit.from_string(html, output_file, configuration=pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf))
            print(a)
            return send_file(output_file)

        # print('нажата', button_id)
        #
        # print("Сейчас " + str(current_year))

        return render_template("curs_show.html", data=answer, count_data=count_dict, flatten=flatten,
                               curr_year=current_year, anchor='start_table', file_exists=file_exists,
                               detail_level=detail_level)

    else:

        return render_template("curs_show.html", curr_year=current_year)


@app.route('/')
def anchor():
    return redirect(url_for('index', _anchor='start_table'))


@app.route('/download/<username>/<year>/<filename>')
@login_required
def download(filename, username, year):
    file_path = F'./reports_storage/{year}/{username}/{filename}'
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=False)
    return "Файл не найден"


def file_exists(filename, username, year):
    file_path = F'./reports_storage/{year}/{username}/{filename}'
    # print('проверяем файл')
    return os.path.isfile(file_path)


def get_current_year():
    cur_year = datetime.datetime.now().year
    # print("Сейчас месяц", datetime.datetime.now().month)
    if datetime.datetime.now().month < 8:  # todo месяц переменной в файле настроек
        cur_year -= 1
    return cur_year


@app.route('/register/<int:year>', methods=['POST', 'GET'])
@login_required
def reg_for_year(year):
    print(year)
    if not year:
        return "Неверный год", 400
    is_new_work = False
    cur_work = Courseworks.query.filter(Courseworks.student == current_user.username,
                                        Courseworks.year == year).first()
    if not cur_work:
        if get_current_year() != year:
            return f"Работа за {year}г. не найдена", 404
        else:
            is_new_work = True
    if request.method == 'GET':
        if is_new_work:
            return render_template("register_work_form_new.html", stud_name=current_user.first_name,
                                   group=current_user.cur_group_or_dep, actual_year=True,
                                   year=get_current_year(), message=None)
        # print(cur_work.title, cur_work.student, cur_work.tutor_status, cur_work.tutor_rank)
        return render_template("register_work_form.html", stud_name=current_user.first_name,
                               work_data=cur_work, actual_year=cur_work.year == get_current_year(),
                               message=None)
    if request.method == 'POST':
        data = request.form

        print(data)
        message = None
        # pattern = r'^[a-zA-Z0-9]+$'
        pattern = r'^[АЁ-ЯЁ].^[АЁ-ЯЁ].^[АЁ-ЯЁ]+^[аё-яё]'

        tutor_name = data.get('adviser-name')
        if not tutor_name:
            message = 'Не указаны ФИО руководителя!'
        # if not re.match(pattern, tutor_name):
        #     message = "ФИО руководителя не соответствует шаблону И.О.Фамилия"
        #     print("неверный паттерн")
        tutor_pos = data.get('adviser-position')
        if tutor_pos not in tutor_pos_list:
            message = 'Неверная должность руководителя!'
        tutor_status = data.get('adviser-status')
        tutor_rank = data.get('adviser-rank')
        if tutor_rank and tutor_rank not in ['доцент', "без звания", "профессор", "", " "]:
            message = "Некорректное звание руководителя"
        department = data.get('department')
        if department not in dep_list:
            message = "Неверная кафедра "
        title = data.get('title')
        if not title or title == " ":
            message = 'Не указана тема курсовой!'

        if message:  # обработка ошибок
            if is_new_work:
                return render_template("register_work_form_new.html", stud_name=current_user.first_name,
                                       group=current_user.cur_group_or_dep, actual_year=True,
                                       year=get_current_year(), message=message)

            return render_template("register_work_form.html", stud_name=current_user.first_name,
                                   work_data=cur_work, actual_year=cur_work.year == get_current_year(),
                                   message=message)
        if is_new_work:
            new_work = Courseworks(student=current_user.username, studentName=current_user.first_name,
                                   year=year, title=title, tutor_name=tutor_name, group=current_user.cur_group_or_dep,
                                   tutor_pos=tutor_pos, tutor_status=tutor_status, tutor_rank=tutor_rank,
                                   departament=department, date_reg=datetime.datetime.now())
            db.session.add(new_work)
            db.session.commit()

            return render_template("register_work_form.html", stud_name=current_user.first_name,
                                   work_data=new_work, actual_year=True,
                                   message="Работа успешно загружена!")
        else:
            cur_work.title = title
            cur_work.tutor_name = tutor_name
            cur_work.tutor_pos = tutor_pos
            cur_work.tutor_status = tutor_status
            cur_work.tutor_rank = tutor_rank
            cur_work.departament = department

            db.session.add(cur_work)
            db.session.commit()

            return render_template("register_work_form.html", stud_name=current_user.first_name,
                                   work_data=cur_work, actual_year=cur_work.year == get_current_year(),
                                   message="Данные успешно обновлены!")


@app.route('/delete/<int:year>', methods=['POST'])
@login_required
def delete_for_year(year):
    print('попытка удаления', current_user.username, year)
    print(request.form)
    if not year:
        return "неверный год", 400
    # cur_work = Courseworks.query.filter(Courseworks.student == current_user.username,
    #                                     Courseworks.year == year).first()
    if request.form['for-doc'] == 'int-report':
        work_name = 'report'
    elif request.form['for-doc'] == 'int-slides':
        work_name = 'slides'
    elif request.form['for-doc'] == 'fin-preport':
        work_name = 'practic_report'
    elif request.form['for-doc'] == 'fin-report':
        work_name = 'final_report'
    elif request.form['for-doc'] == 'fin-slides':
        work_name = 'final_slides'
    elif request.form['for-doc'] == 'fin-antiplagiat':
        work_name = 'antiplagiat'
    elif request.form['for-doc'] == 'fin-sup-review':
        work_name = 'review'
    elif request.form['for-doc'] == 'fin-review':
        work_name = 'final_review'
    else:
        return 'неверный тип отчета', 400
    print(work_name)
    if file_exists(F"{work_name}.pdf", current_user.username, year):
        os.remove(F'reports_storage/{year}/{current_user.username}/{work_name}.pdf')
        # return "файл успешно удален",200
        return redirect(F'/upload/{year}')
    return 'файл не существует', 404


@app.route('/upload/<int:year>', methods=['POST', 'GET'])
@login_required
def load_for_year(year):
    print(year)
    if not year:
        return "Неверный год", 400
    cur_work = Courseworks.query.filter(Courseworks.student == current_user.username,
                                        Courseworks.year == year).first()
    if not cur_work:
        return "Работа за указанный год не найдена", 404
    if not cur_work.year or not cur_work.title or not cur_work.departament or not cur_work.group:
        return "Данные по работе неполные или были повреждены, требуется зарегистрировать работу повторно или " \
               "обратиться к администратору", 404
    if request.method == 'GET':
        return render_template("load_form.html", stud_name=current_user.first_name, file_exists=file_exists,
                               word_data=cur_work, course=cur_work.group[2:3], message=None)

    if request.method == "POST":
        pdf_file = request.files['doc-file']
        # request.files['pdf']
        pdf_content = pdf_file.read()
        print(request.form['for-doc'])
        work_name = ''

        if request.form['for-doc'] == 'int-report':
            work_name = 'report'
            update_bit = 0
        elif request.form['for-doc'] == 'int-slides':
            work_name = 'slides'
            update_bit = 1
        elif request.form['for-doc'] == 'fin-preport' and str(cur_work.group[2:3]) in ['4', '6']:
            work_name = 'practic_report'
            update_bit = 2
        elif request.form['for-doc'] == 'fin-report':
            work_name = 'final_report'
            update_bit = 3
        elif request.form['for-doc'] == 'fin-slides':
            work_name = 'final_slides'
            update_bit = 4
        elif request.form['for-doc'] == 'fin-antiplagiat' and str(cur_work.group[2:3]) in ['4', '6']:
            work_name = 'antiplagiat'
            update_bit = 5
        elif request.form['for-doc'] == 'fin-sup-review' and str(cur_work.group[2:3]) in ['4', '6']:
            work_name = 'review'
            update_bit = 6
        elif request.form['for-doc'] == 'fin-review' and str(cur_work.group[2:3]) == '6':
            work_name = 'final_review'
            update_bit = 7
        else:
            return 'неверный тип отчета', 400
        os.makedirs(F'reports_storage/{year}/{current_user.username}', exist_ok=True)
        with open(F'reports_storage/{year}/{current_user.username}/{work_name}.pdf', 'wb') as f:
            f.write(pdf_content)
        # return 'записали'

        # prev_in_time=cur_work.in_time
        cur_curs = cur_work.group[2:3]
        date_format = "%d.%m.%y"  # Формат даты
        prev_in_time = cur_work.in_time
        if not prev_in_time:
            prev_in_time = "00000000"
        if update_bit in [0, 1]:
            deadline_str = upload_deadlines["interim_reports_date"][cur_curs]
        else:
            deadline_str = upload_deadlines["final_reports_date"][cur_curs]
        print(deadline_str)
        print(deadline_str[3:5])
        deadline_year = cur_work.year if int(deadline_str[3:5]) > 7 else cur_work.year + 1
        deadline_str += f".{str(deadline_year)[2:4]}"
        print(deadline_str)
        deadline_date_target = datetime.datetime.strptime(deadline_str, date_format)
        print(f"now: {datetime.datetime.now()}, deadline: {deadline_date_target}")
        if deadline_date_target > datetime.datetime.now():
            prev_in_time = prev_in_time[:update_bit] + '1' + prev_in_time[update_bit + 1:]

            cur_work.in_time = prev_in_time
        else:

            prev_in_time = prev_in_time[:update_bit] + '0' + prev_in_time[update_bit + 1:]
            cur_work.in_time = prev_in_time

        db.session.add(cur_work)
        db.session.commit()

        return render_template("load_form.html", stud_name=current_user.first_name, file_exists=file_exists,
                               word_data=cur_work, course=cur_work.group[2:3], message=work_name)


@app.route('/register', methods=['GET'])
@login_required
def reg_get_years():
    if request.method == 'GET':

        if current_user.cur_group_or_dep in ['ИМО', "ПМиК"]:  # todo проверка на препода
            pass

        available_years = Courseworks.query.filter(Courseworks.student == current_user.username) \
            .group_by(Courseworks.year).order_by(Courseworks.year.desc()).all()
        print("Для пользователя " + current_user.username + " есть записи за след. года:")

        av_years = []
        for e in available_years:
            av_years.append(e.year)

        cur_year = get_current_year()
        print("Начало семестра в ", cur_year)

        if cur_year not in av_years:
            available_years.insert(0, Courseworks(year=cur_year))
            print('нет работ за текущий год, добавляем год в список')

        print('окончательный список доступных дат для регистрации работ:')
        for e in available_years:
            print(e.year)
        return render_template("register_work.html", stud_name=current_user.first_name, available_years=available_years)


@app.route('/new_topic', methods=['POST', 'GET'])
@login_required
def reg_topic():
    return render_template("new_topic.html")


@app.route('/list_unreg', methods=['POST', 'GET'])
@login_required
def report_unreg():
    return "здесь будем загружать pdf со студентами, не загрузившими работы"


# 1- 3, 5 курс: Пр. отчет,Пр. ЭП, *Отчет,*ЭП
# 4 курс: Пр. отчет,	Пр. ЭП,	Отчет по практике НИР,	Текст ВКР,	Презент. ВКР,	Проверка на плагиат,	Отзыв руковод.
# 6 курс: Пр. отчет,	Пр. ЭП,	Отчет по практике НИР, Текст ВКР, Презент.ВКР,Проверка на плагиат,Отзыв руковод., Рецензия


@app.route('/upload', methods=['GET'])
@login_required
def load():
    # TODO определять студент или препод ( для преподов пока что заглушка?)
    available_years = Courseworks.query.filter(Courseworks.student == current_user.username) \
        .group_by(Courseworks.year).order_by(Courseworks.year.desc()).all()
    print("Для пользователя " + current_user.username + " есть записи за след. года")
    for e in available_years:
        print(e.year)
    if (request.method == 'GET'):
        # chose_year = session.get('year')
        return render_template("load.html",
                               stud_name=current_user.first_name,
                               available_years=available_years)


if __name__ == "__main__":
    app.run(debug=True)
