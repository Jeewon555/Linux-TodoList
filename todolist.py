from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)

# 유저 모델
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    pw = db.Column(db.String(120), nullable=False)

# 투두리스트 모델
class listtodo(db.Model):
    __tablename__ = 'todolist'
    todo = db.Column(db.String(300), nullable=False)
    state = db.Column(db.Boolean, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 새 id 필드

# DB가 없으면 생성 및 더미 데이터 삽입
with app.app_context():
    if not os.path.exists("mydb.db"):
         db.create_all()

# 홈
@app.route('/')
def defaultpage():
    return render_template("default.html")

# 로그인
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

# 투두리스트 화면
@app.route('/taskmain')
def taskmain():
    today = datetime.today()
    month = int(request.args.get('month', today.month))
    day = int(request.args.get('day', today.day))
    query = listtodo.query.filter_by(month=month, day=day)
    todos = query.all()
    return render_template("taskmain.html", todos=todos, month=month, day=day)

# #있는 디비 가져오는 Load용
# @app.route('/api/todolist')
# def get_todolist():
#     month = int(request.args.get('month', datetime.today().month))
#     day = int(request.args.get('day', datetime.today().day))
#     todos = listtodo.query.filter_by(month=month, day=day).all()
#     return jsonify([
#         {
#             "todo": t.todo,
#             "state": t.state,
#             "id" : t.id
#         } for t in todos
#     ])

# ---------------------------
# 1. 추가 (Create)
# ---------------------------
@app.route('/add', methods=['POST'])
def add_todo():
    data = request.get_json()
    todo_text = data.get('todo')
    state = data.get('state', False)
    month = data.get('month', datetime.today().month)
    day = data.get('day', datetime.today().day)
    new_todo = listtodo(
        todo=todo_text,
        state=state,
        month=month,
        day=day
    )
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'success': True, 'id': new_todo.id})

# ---------------------------
# 2. 조회 (Read)
# ---------------------------
@app.route('/api/todolist')
def get_todolist():
    # 쿼리 파라미터로 필터링 예시
    month = int(request.args.get('month', datetime.today().month))
    day = int(request.args.get('day', datetime.today().day))
    todos = listtodo.query.filter_by(month=month, day=day).all()
    return jsonify([
        {
            'id': t.id,
            'todo': t.todo,
            'state': t.state,
            'month': t.month,
            'day': t.day
        } for t in todos
    ])

# ---------------------------
# 3. 상태(체크박스) 수정 (Update)
# ---------------------------
@app.route('/checkbox', methods=['POST'])
def update_state():
    data = request.get_json()
    todo_id = data.get('id')
    state = data.get('state')
    todo = listtodo.query.get(todo_id)
    if not todo:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    todo.state = state
    db.session.commit()
    return jsonify({'success': True})

# ---------------------------
# 4. 할 일 내용 수정 (Update)
# ---------------------------
@app.route('/edit', methods=['POST'])
def edit_todo():
    data = request.get_json()
    todo_id = data.get('id')
    todo_text = data.get('todo')
    todo = listtodo.query.get(todo_id)
    if not todo:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    todo.todo = todo_text
    db.session.commit()
    return jsonify({'success': True})

# ---------------------------
# 5. 삭제 (Delete)
# ---------------------------
@app.route('/delete', methods=['POST'])
def delete_todo():
    data = request.get_json()
    todo_id = data.get('id')
    todo = listtodo.query.get(todo_id)
    if not todo:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'success': True})


# 서버 실행
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)
