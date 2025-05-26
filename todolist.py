from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)

# 유저 클래스 (디비랑 연결됨)
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    pw = db.Column(db.String(120), nullable=False)

# 투두리스트 클래스
class listtodo(db.Model):
    __tablename__='todolist'
    category = db.Column(db.String(50), nullable=True)
    todo = db.Column(db.String(300), nullable=False, primary_key=True)
    state = db.Column(db.Boolean)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

    # 데이터가 없을 때만 초기 더미 데이터 삽입
    if not listtodo.query.first():
        for i in range(1, 30):
            todo = listtodo(category="마음", todo=f"아무거나 {i}", state=False, month=5, day=i)
            db.session.add(todo)
        db.session.commit()


# 카테고리 클래스
class category(db.Model):
    __tablename__='category'
    name = db.Column(db.String(50), nullable=False)
    category_num = db.Column(db.Integer, primary_key=True)
    totaltodo = db.Column(db.Integer)

category_n = category(name="마음", category_num=2, totaltodo=4)

# 디비 만드는 코드
with app.app_context():
    db.create_all()

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
    # 오늘 날짜 기본값
    today = datetime.today()
    month = int(request.args.get('month', today.month))
    day = int(request.args.get('day', today.day))
    category_name = request.args.get('category', None)
    # 카테고리 목록
    categories = category.query.all()
    # 필터링 쿼리
    query = listtodo.query.filter_by(month=month, day=day)
    if category_name:
        query = query.filter_by(category=category_name)
    todos = query.all()
    return render_template("temptaskpage.html", todos=todos, categories=categories, month=month, day=day, category_name=category_name)

@app.route('/api/todolist')
def get_todolist():
    month = int(request.args.get('month', datetime.today().month))
    day = int(request.args.get('day', datetime.today().day))
    category_name = request.args.get('category')

    query = listtodo.query.filter_by(month=month, day=day)
    if category_name:
        query = query.filter_by(category=category_name)

    todos = query.all()
    return {
        "todos": [
            {
                "todo": t.todo,
                "state": t.state,
                "category": t.category
            } for t in todos
        ]
    }

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)
