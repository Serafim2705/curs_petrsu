from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///curs3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

# class Message(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     data=db.Column(db.String(200),primary_key=False)

# class Courseworks(db.Model):
#     id = db.Column(db.Integer,primary_key=True)
#     title = db.Column(db.String(200),primary_key=False)
#     group = db.Column(db.String(200),primary_key=False)
#     departament = db.Column(db.String(200), primary_key=False)
#     student = db.Column(db.String(200), primary_key=False)
#     studentName = db.Column(db.String(200), primary_key=False)
#     tutor = db.Column(db.String(200), primary_key=False)
#     year = db.Column(db.Integer,primary_key=False)
#     link = db.Column(db.String(200), primary_key=False)
class Courseworks(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200), primary_key=False)
    #data = db.Column(db.String(200),primary_key=False)
    group = db.Column(db.String(200),primary_key=False)
    departament = db.Column(db.String(200), primary_key=False)
    student = db.Column(db.String(200), primary_key=False)
    studentName = db.Column(db.String(200), primary_key=False)
    tutor_name = db.Column(db.String(200), primary_key=False)
    tutor_status = db.Column(db.String(200), primary_key=False)
    tutor_rank = db.Column(db.String(200), primary_key=False)
    tutor_pos = db.Column(db.String(200), primary_key=False)
    year = db.Column(db.Integer,primary_key=False)
    link = db.Column(db.String(200), primary_key=False)
from flask_login import UserMixin, login_user
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name= db.Column(db.String(50), nullable=False)
    second_name= db.Column(db.String(50), nullable=False)
    third_name = db.Column(db.String(50), nullable=False)
    is_student= db.Column(db.Boolean, default=True)
    cur_group_or_dep=db.Column(db.String(50), nullable=False)

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
# db.drop_all()
db.create_all()
new_rec=Courseworks(title='Курсовая проверка!',group='22505',
                    departament='ПМиК',student='serov',studentName='C.C.Серов',
                    tutor_name="Д.Б.Чистяков",tutor_status="к. т. н.",
                    year=2022,link='storage/test/')

# db.session.add(new_rec)
# db.session.commit()
# del_table=User.__table__
# del_table.drop(db.engine)

# new_User=User(username='serov',password='123',first_name='Серафим',second_name="Серов",third_name="Сергеевич",cur_group_or_dep='22605')
#
# db.session.add(new_User)
# db.session.commit()

# _groups=Courseworks.query.group_by(Courseworks.group)
# print(_groups.count())
# for e in _groups:
#     print(e.group)
#     r=Courseworks.query.filter(Courseworks.group==e.group)
#     for e2 in r:
#         print(e2.title, e.group)

# response = Courseworks.query.filter(Courseworks.student == "serov").first()
# db.session.delete(response)
# db.session.commit()
from werkzeug.security import generate_password_hash, check_password_hash
hash=generate_password_hash("123")
print(hash)
print(check_password_hash(hash,"123"))
print(check_password_hash("pbkdf2:sha256:260000$w5AqCT9CThy9vPkj$da0d2a70bf072fe138e70fc6d422cefa23c34cc0d92b56da70473bc83d8f5a7c","123"))