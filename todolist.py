from flask import Flask, render_template, request, redirect, url_for, jsonify #flask 관련 모듈
from flask_sqlalchemy import SQLAlchemy #SQLAlchemy
from datetime import datetime # 날짜/ 시간 모듈
import os # 파일/경로 관련 모듈

app = Flask(__name__) #Flask어플리케이션 생성
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'  # SQLite DB 경로설정
db = SQLAlchemy(app) #SQLAlchemy 객체 생성

# 유저 모델
class User(db.Model):
    __tablename__ = 'user'  #테이블 이름

    #ID, PW
    id = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    pw = db.Column(db.String(120), nullable=False)

# 투두리스트 모델
class listtodo(db.Model):
    __tablename__ = 'todolist'  #테이블 이름

    todo = db.Column(db.String(300), nullable=False) #할 일
    state = db.Column(db.Boolean, nullable=False)  #완료 여부
    month = db.Column(db.Integer, nullable=False)  #월
    day = db.Column(db.Integer, nullable=False)  #일
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 고유번호

# mydb.db가 있으면 안 생성 없으면 생성
with app.app_context():
    if not os.path.exists("mydb.db"):
         db.create_all()

# 홈
@app.route('/')
def defaultpage():
    return render_template("default.html")

# 로그인
@app.route('/login', methods=["GET", "POST"])                                    # 로그인 URL
def loginpage():                                                                      # 로그인 뷰
    if request.method == "POST":                                                      # POST 요청 시
        user_id = request.form.get("id")                                              # 폼에서 id 추출
        user_pw = request.form.get("pw")                                              # 폼에서 pw 추출
        check_user = User.query.filter_by(id=user_id).first()                         # 사용자 조회

        if check_user and check_user.pw == user_pw:                                   # 일치 여부 확인
            return render_template("loginsuccess.html")                               # 성공 페이지
        else:                                                                         # 실패
            return render_template("loginfail.html")                                  # 실패 페이지 렌더링
    return render_template("login.html")                                              # GET 요청 시 로그인 폼


# 회원가입
@app.route('/join', methods=["GET", "POST"])                               # 회원가입 URL
def join():                                                                     # 회원가입 뷰
    if request.method == "POST":                                                # POST 요청
        user_id = request.form.get("id")                                        # 입력 id
        user_pw = request.form.get("pw")                                        # 입력 pw
        if User.query.filter_by(id=user_id).first():                            # 중복 체크
            return "이미 존재하는 아이디입니다."                                    # 중복 시 메시지
        new_user = User(id=user_id, pw=user_pw)                                 # 새 유저 객체
        db.session.add(new_user)                                                # 세션에 추가
        db.session.commit()                                                     # 커밋
        return redirect(url_for("loginpage"))                                   # 로그인 페이지로 리다이렉트
    return render_template("join.html")                                         # GET 요청 시 가입 폼

# 투두리스트 화면
@app.route('/taskmain')                                                         # 투두리스트 메인 URL
def taskmain():                                                                 # 투두리스트 뷰
    today = datetime.today()                                                    # 오늘 날짜
    month = int(request.args.get('month', today.month))                         # 월 파라미터
    day = int(request.args.get('day', today.day))                               # 일 파라미터
    query = listtodo.query.filter_by(month=month, day=day)                      # 해당 날짜 조회
    todos = query.all()                                                         # 결과 리스트
    return render_template("taskmain.html", todos=todos, month=month, day=day)  # 템플릿 렌더링

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

#############################     todo 추가하기    ##################################
@app.route('/add', methods=['POST'])
def add_todo():
    data = request.get_json()                                                   # JSON 데이터
    todo_text = data.get('todo')                                                # 내용
    state = data.get('state', False)                                            # 상태(기본 False)
    month = data.get('month', datetime.today().month)                           # 월
    day = data.get('day', datetime.today().day)                                 # 일
    new_todo = listtodo(todo=todo_text, state=state, month=month, day=day)      # 객체 생성
    db.session.add(new_todo)                                                    # 세션에 추가
    db.session.commit()
    return jsonify({'success': True, 'id': new_todo.id})


##############################   todolist 보여주기 함수   ###########################
@app.route('/api/todolist')
def get_todolist():                                                             # 조회 함수
    month = int(request.args.get('month', datetime.today().month))              # 월 파라미터
    day = int(request.args.get('day', datetime.today().day))                    # 일 파라미터
    todos = listtodo.query.filter_by(month=month, day=day).all()                # 조회
    return jsonify([                                                            # JSON 배열 반환
        {
            'id': t.id,
            'todo': t.todo,
            'state': t.state,
            'month': t.month,
            'day': t.day
        } for t in todos
    ])


########################     checkbox 함수      #########################
@app.route('/checkbox', methods=['POST'])
def update_state():
    data = request.get_json()                                                   # JSON 데이터 가져오기
    todo_id = data.get('id')                                                    # 대상 todo의 id 가져오기
    state = data.get('state')                                                   # 해당 todo의 상태 가져오기
    todo = listtodo.query.get(todo_id)                                          # 객체 조회
    if not todo:                                                                # 없으면
        return jsonify({'success': False, 'error': 'Not found'}), 404           # 404 반환
    todo.state = state                                                          # 상태 수정
    db.session.commit()                                                         # 저장
    return jsonify({'success': True})


########################     todo 편집 함수      #########################
@app.route('/edit', methods=['POST'])
def edit_todo():
    data = request.get_json()                                                    # JSON 데이터
    todo_id = data.get('id')                                                     # 대상 id
    todo_text = data.get('todo')                                                 # 새 내용
    todo = listtodo.query.get(todo_id)                                           # 객체 조회
    if not todo:                                                                 # 없으면
        return jsonify({'success': False, 'error': 'Not found'}), 404            # 404
    todo.todo = todo_text                                                        # 내용 수정
    db.session.commit()                                                          # 저장
    return jsonify({'success': True})


########################     todo 삭제 함수      #########################
@app.route('/delete', methods=['POST'])
def delete_todo():
    data = request.get_json()                                                   # JSON 데이터 불러오기
    todo_id = data.get('id')                                                    # 대상 todo id 가져오기
    todo = listtodo.query.get(todo_id)                                          # todo id로 객체 조회
    if not todo:                                                                # 없으면
        return jsonify({'success': False, 'error': 'Not found'}), 404           # 404
    db.session.delete(todo)                                                     # 삭제
    db.session.commit()                                                         # 저장
    return jsonify({'success': True})


# 서버 실행
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)
