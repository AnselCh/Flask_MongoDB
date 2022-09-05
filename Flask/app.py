# 初始化資料庫連線
from datetime import datetime
from typing import Collection
from flask import *
import pymongo
import certifi  # 排除ServerSelectionTimeoutError
client = pymongo.MongoClient(
    "mongodb+srv://root:<password>@cluster0.4rfp0a0.mongodb.net/?retryWrites=true&w=majority", connect=False, tlsCAFile=certifi.where())
print("連線成功")

db = client.member_system
# 初始化Flask伺服器
app = Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.secret_key = "password"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/member")
def member():
    if "nickname" in session:
        return render_template("member.html")
    else:
        return redirect("/")


@app.route("/error")  # /error?msg="錯誤訊息"
def error():
    msg = request.args.get("msg", "發生錯誤，請聯繫客服")
    return render_template("error.html", message=msg)


@app.route("/signup", methods=["POST"])
def signup():
    # 接收前端資料
    nickname = request.form["nickname"]
    email = request.form["email"]
    password = request.form["password"]
    now = datetime.now()
    # 進行資料庫互動
    collection = db.user
    # 檢查是否有相同的資料，沒有相同就會回傳none
    result = collection.find_one({
        "email": email
    })
    if result != None:
        return redirect("/error?msg=信箱已經被註冊")
    # 把資料放進資料庫
    collection.insert_one({
        "nickname": nickname,
        "email": email,
        "password": password,
        "insert_time": now
    })
    return redirect("/")


@app.route("/signin", methods=["POST"])
def signin():
    # 從前端取得資料
    email = request.form["email"]
    password = request.form["password"]
    # 連接資料庫
    collection = db.user
    # 檢查信箱密碼是否正確
    result = collection.find_one({
        "$and": [
            {"email": email},
            {"password": password}
        ]
    })
    if result == None:
        return redirect("/error?msg=信箱或密碼輸入錯誤")
    # 登入成功在Session紀錄會員資訊
    session["nickname"] = result["nickname"]
    return redirect("/member")


@app.route("/signout")
def signout():
    del session["nickname"]
    return redirect("/")


app.run(port=3000)
