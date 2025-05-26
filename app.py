from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)

# 유저 클래스
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    pw = db.Column(db.String(120), nullable=False)

# 카테고리 클래스
class Category(db.Model):
    __tablename__ = 'category'
    category_num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    totaltodo = db.Column(db.Integer)

# 투두리스트 클래스
class ListTodo(db.Model):
    __tablename__ = 'todolist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    todo = db.Column(db.String(300), nullable=False)
    state = db.Column(db.Boolean, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    category_num = db.Column(db.Integer, db.ForeignKey('category.category_num'), nullable=True)
    category = db.relationship('Category', backref=db.backref('todos', lazy=True))

# DB 및 초기 데이터 생성
with app.app_context():
    db.create_all()
    # 카테고리 데이터가 없으면 추가
    if Category.query.count() == 0:
        categories = [
            Category(name="마음", totaltodo=0),
            Category(name="건강", totaltodo=0),
            Category(name="일", totaltodo=0)
        ]
        db.session.add_all(categories)
        db.session.commit()
    # 투두 데이터가 없으면 추가
    if ListTodo.query.count() == 0:
        mind_category = Category.query.filter_by(name="마음").first()
        for t in range(1, 30):
            todo = ListTodo(
                todo="물 주기" + str(t),
                month=5,
                day=t,
                state=(t % 2 != 0),
                category_num=mind_category.category_num
            )
            db.session.add(todo)
        db.session.commit()

# 홈화면
@app.route('/')
def defaultpage():
    return render_template("default.html")

# 로그인 화면
@app.route('/login', methods=["GET", "POST"])
def loginpage():
    if request.method == "POST":
        user_id = request.form.get("id")
        user_pw = request.form.get("pw")
        check_user = User.query.filter_by(id=user_id).first()
        if check_user and check_user.pw == user_pw:
            return render_template("loginsuccess.html")
        else:
            return render_template("loginfail.html")
    return render_template("login.html")

# 회원가입
@app.route('/join', methods=["GET", "POST"])
def join():
    if request.method == "POST":
        user_id = request.form.get("id")
        user_pw = request.form.get("pw")
        if User.query.filter_by(id=user_id).first():
            return "이미 존재하는 아이디입니다."
        new_user = User(id=user_id, pw=user_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("loginpage"))
    return render_template("join.html")

# 달력있는 투두리스트 본 페이지 (날짜/카테고리별 필터)
@app.route('/taskmain')
def taskmain():
    today = datetime.today()
    month = int(request.args.get('month', today.month))
    day = int(request.args.get('day', today.day))
    category_name = request.args.get('category', None)
    categories = Category.query.all()
    query = ListTodo.query.filter_by(month=month, day=day)
    if category_name:
        category_obj = Category.query.filter_by(name=category_name).first()
        if category_obj:
            query = query.filter_by(category_num=category_obj.category_num)
    todos = query.all()
    return render_template("taskmain.html", todos=todos, categories=categories, month=month, day=day, category_name=category_name)

@app.route('/api/todolist')
def get_todolist():
    month = int(request.args.get('month', datetime.today().month))
    day = int(request.args.get('day', datetime.today().day))
    category_name = request.args.get('category')
    query = ListTodo.query.filter_by(month=month, day=day)
    if category_name:
        category_obj = Category.query.filter_by(name=category_name).first()
        if category_obj:
            query = query.filter_by(category_num=category_obj.category_num)
    todos = query.all()
    return jsonify([
        {
            "todo": t.todo,
            "state": t.state,
            "category": t.category.name if t.category else None
        } for t in todos
    ])

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)
