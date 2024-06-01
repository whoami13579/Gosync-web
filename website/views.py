from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from .models import Role, User, Forum, Post, Report, Comment
from . import db
from datetime import datetime

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html", user=current_user, forums=Forum.query.filter_by().all())


@views.route("/forum/<forum_id>")
def forum(forum_id):
    return render_template("forum.html", user=current_user, forum=Forum.query.filter_by(forum_id=forum_id).first())


@views.route("/forum/<forum_id>/new-post", methods=["GET", "POST"])
@login_required
def new_post(forum_id):
    if request.method == "POST":
        title = request.form.get("title")
        tags = request.form.get("tags")
        content = request.form.get("content")
        start = request.form.get("start")
        end = request.form.get("end")
        meeting_point = request.form.get("meeting_point")
        destination = request.form.get("destination")
        max_participants = int(request.form.get("max_participants"))

        date_format = "%Y-%m-%d"
        start = datetime.strptime(start, date_format).date()
        end = datetime.strptime(end, date_format).date()

        post = Post(title, tags, content, start, end, meeting_point, destination, max_participants, current_user.get_id(), forum_id)
        post.author = current_user
        post.forum = Forum.query.filter_by(forum_id=forum_id).first()
        db.session.add(post)
        db.session.commit()

        flash("New Post Created", category="success")
        return redirect(url_for("views.forum", forum_id=forum_id))

    return render_template("new_post.html", user=current_user)


@views.route("/forum/<forum_id>/join")
@login_required
def join_forum(forum_id):
    forum = Forum.query.filter_by(forum_id=forum_id).first()
    forum.users.append(current_user)

    db.session.commit()
    flash("Join", category="success")

    return redirect(url_for("views.forum", forum_id=forum_id))


@views.route("/forum/<forum_id>/leave")
@login_required
def leave_forum(forum_id):
    forum = Forum.query.filter_by(forum_id=forum_id).first()
    forum.users.remove(current_user)

    db.session.commit()
    flash("Leave", category="success")

    return redirect(url_for("views.forum", forum_id=forum_id))


@views.route("/new-forum", methods=["GET", "POST"])
@login_required
def new_forum():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if Forum.query.filter_by(name=name).first():
            flash("Forum already exists", category="error")
            return redirect(url_for("views.new_forum"))

        forum = Forum(name, description, current_user.get_id())
        forum.users.append(current_user)

        db.session.add(forum)
        db.session.commit()

        flash("New Forum Created", category="success")
        return redirect(url_for("views.home"))

    return render_template("new_forum.html", user=current_user)


@views.route("/forum/<forum_id>/delete")
@login_required
def delete_forum(forum_id):
    forum = Forum.query.filter_by(forum_id=forum_id).first()

    if forum.user_id == current_user.get_id() or current_user.get_id() == 2:
        db.session.delete(forum)
        db.session.commit()

        flash("Forum Deleted", category="success")
        return redirect(url_for("views.home"))


    flash("You can't delete this forum.", category="error")
    return redirect(url_for("views.homne"))


@views.route("/forum/<forum_id>/<post_id>/delete")
@login_required
def delete_post(forum_id, post_id):
    post = Post.query.filter_by(forum_id=post_id).first()

    if post.author.user_id == current_user.get_id() or current_user.get_id() == 2:
        db.session.delete(post)
        db.session.commit()

        flash("Post Deleted", category="success")
        return redirect(url_for("views.home"))


    flash("You can't delete this forum.", category="error")
    return redirect(url_for("views.homne"))

@views.route("/my-forums")
@login_required
def my_forums():
    return render_template("my_forums.html", user=current_user, forums=current_user.forums)
    

@views.route("/forum/<forum_id>/<post_id>", methods=["GET", "POST"])
@login_required
def view_post(forum_id, post_id):
    if request.method == "POST":
        text = request.form.get("text")

        comment = Comment(text, current_user.get_id(), post_id)
        comment.user = current_user
        comment.post = Post.query.filter_by(post_id=post_id).first()

        db.session.add(comment)
        db.session.commit()

    return render_template("post.html", user=current_user, post=Post.query.filter_by(post_id=post_id).first())


@views.route("/forum/<forum_id>/<post_id>/like")
@login_required
def like_post(forum_id, post_id):
    post = Post.query.filter_by(post_id=post_id).first()
    if current_user in post.likes:
        post.likes.remove(current_user)
        
        db.session.commit()

        return redirect(url_for("views.view_post", forum_id=forum_id, post_id=post_id))
    else:
        if len(post.likes) < post.max_participants:
            post.likes.append(current_user)

            db.session.commit()
        else:
            flash("You can't join.", category="error")

        return redirect(url_for("views.view_post", forum_id=forum_id, post_id=post_id))


@views.route("/forum/<forum_id>/<post_id>/report", methods=["GET", "POST"])
@login_required
def report_post(forum_id, post_id):
    post = Post.query.filter_by(post_id=post_id).first()
    
    if Report.query.filter_by(user_id=current_user.get_id()).first():
        flash("You have already reported this post.", category="error")

        return redirect(url_for("views.view_post", forum_id=forum_id, post_id=post_id))

    if request.method == "POST":
        if Report.query.filter_by(user_id=current_user.get_id()).first():
            flash("You have already reported this post.", category="error")

            return redirect(url_for("views.view_post", forum_id=forum_id, post_id=post_id))

        reason = request.form.get("reason")

        post.report = True
        
        report = Report(reason, current_user.get_id(), post_id)
        report.post = Post.query.filter_by(post_id=post_id).first()

        db.session.add(report)
        db.session.commit()

        flash("Report created.", category="success")

        return redirect(url_for("views.view_post", forum_id=forum_id, post_id=post_id))


    return render_template("report.html", user=current_user)


@views.route("/reported-posts")
@login_required
def reported_forums():
    if current_user.role_id != 2:
        flash("You don't have access to this page.", category="error")
        
        return redirect(url_for("views.home", user=current_user))

    return render_template("reported_posts.html", user=current_user, posts=Post.query.filter_by(report=True))


@views.route("/reported-posts/<post_id>")
@login_required
def view_reported_post(post_id):
    if current_user.role_id != 2:
        flash("You don't have access to this page.", category="error")
        
        return redirect(url_for("views.home", user=current_user))

    return render_template("reported_post.html", user=current_user, post=Post.query.filter_by(post_id=post_id).first())


@views.route("/reported-posts/<post_id>/ok")
@login_required
def view_post_ok(post_id):
    if current_user.role_id != 2:
        flash("You don't have access to this page.", category="error")
        
        return redirect(url_for("views.home", user=current_user))

    post = Post.query.filter_by(post_id=post_id).first()
    post.report = False

    db.session.query(Report).filter_by(post_id=post_id).delete()
    db.session.commit()

    return redirect(url_for("views.reported_forums", user=current_user))


@views.route("/reported-posts/<post_id>/delete")
@login_required
def view_post_delete(post_id):
    if current_user.role_id != 2:
        flash("You don't have access to this page.", category="error")
        
        return redirect(url_for("views.home", user=current_user))
    
    db.session.query(Report).filter_by(post_id=post_id).delete()
    post = Post.query.filter_by(post_id=post_id).first()
    
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for("views.reported_forums", user=current_user))


@views.route("/search", methods=["GET", "POST"])
def search():
    forums = []
    posts = []

    if request.method == "POST":
        search = request.form.get("search")
        forums = Forum.query.filter(Forum.name.like('%' + search + '%'))
        posts = Post.query.filter(Post.title.like('%' + search + '%'))

    return render_template("search.html", user=current_user, forums=forums, posts=posts)
