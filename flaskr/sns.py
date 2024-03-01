from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import Flask
from flask import url_for, send_from_directory
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import os
from flask import session

from .auth import login_required
from .db import get_db

bp = Blueprint("sns", __name__)
app = Flask(__name__, instance_relative_config=True)

# アップロードされたファイルを保存するディレクトリ
UPLOAD_FOLDER = 'flaskr/static/images'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS = {'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

file_ = ""
# ファイルの拡張子が許可されているかチェック
def allowed_file(filename):
    if  '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        return filename.rsplit('.', 1)[1].lower()
           

@bp.route("/", methods=("GET", "POST"))
def index():
    
    db = get_db()
    user_id = session.get("user_id")



    if user_id is None:
        g.user = None
        return render_template("sns/index.html", post=None)
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )

    post = (
    get_db()
    .execute(
        "SELECT u.id, username, details"
        " FROM  user u "
        " WHERE u.id = ?",
        (user_id,),
    )
    .fetchone()
    )

    
    path = 'static/images/'+ str(user_id) +'.png'

    return render_template("sns/index.html", post=post, path=path)

def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/profile", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":

        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("sns.index"))

    return render_template("sns/profile.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("sns.index"))

    return render_template("sns/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("sns.index"))

@bp.route("/profile_create", methods=("GET", "POST"))
@login_required
def profile_create():
    if request.method == "POST":

            # ファイルがリクエスト内にない場合
        if 'image' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['image']
        # ユーザーがファイルを選択せずに送信した場合、ブラウザは
        # 空のファイル名を送信する
        if file.filename == '':
            flash('ファイルが選択されていません')
            return redirect(request.url)
        file_ = allowed_file(file.filename)
        if file and file_:
            # filename = secure_filename(file.filename)
            # ファイルを保存
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(g.user["id"])+"."+file_))
            
        

        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE user SET username = ?, details = ? WHERE id = ?", (title, body, g.user["id"])
            )
            db.commit()
        return redirect(url_for("sns.index"))

    else:
        return render_template('sns/profile.html')

       
@bp.route('/chat', methods=['GET', 'POST'])
def chat():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
        return render_template("auth/friends.html", post=None)
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )

    if request.method == 'POST':
        # Get the recipient user id from the request
        receiver_id = request.form["receiver_id"]
        
        # Get the message content from the request
        message_content = request.form["message_content"]
        
        # Save the message to the database
        db = get_db()
        db.execute(
            "INSERT INTO message (sender_id, receiver_id, message_content) VALUES (?, ?, ?)",
            (g.user["id"], receiver_id, message_content),
        )
        db.commit()


        message = (
            get_db()
            .execute(
                "SELECT receiver_id, message_content"
                " FROM message"
                " WHERE receiver_id = ?",
                (int(receiver_id),),
            )
            .fetchone()
        )
       

        if message:
            receiver_id = message["receiver_id"]
            message_content = message["message_content"]
        else:
            receiver_id = None
            message_content = None

        
        # Redirect to the chat page
        return render_template("sns/chat.html", rec_id=receiver_id, msg_content=message_content)
    else:
        message = (
            get_db()
            .execute(
                "SELECT receiver_id, sender_id, message_content"
                " FROM message"
                " WHERE receiver_id = ?",
                (int(g.user['id']),),
            )
            .fetchone()
        )
        if message:
            receiver_id = message["receiver_id"]
            sender_id = message["sender_id"]
            message_content = message["message_content"]
        else:
            receiver_id = None
            sender_id = None
            message_content = None
        
        db = get_db()

        friend_1 = db.execute("SELECT my_id FROM friendship").fetchall()
        friend_2 = db.execute("SELECT friend_id FROM friendship").fetchall()
        

        index_of = [index for index, row in enumerate(friend_1) if row["my_id"] == int(user_id)]
       
        # 友達のIDが5である要素のインデックス番号に対応する友達のIDを取得する
        my_friend = []
        for index in index_of:
            my_friend.append(friend_2[index]["friend_id"])
        
        if g.user['id'] == receiver_id and ( sender_id in my_friend ):
             return render_template("sns/chat.html", msg_content=message_content)

    # Redirect to the chat page
        return render_template("sns/chat.html", rec_id=None, msg_content=None)
