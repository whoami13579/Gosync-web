from flask_login import UserMixin
from . import db
from sqlalchemy.sql import func

Forum_user = db.Table(
    "forum_users",
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id")),
    db.Column(
        "forum_id",
        db.Integer,
        db.ForeignKey("forums.forum_id"),
    ),
)

Post_likes = db.Table(
    "post_likes",
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id")),
    db.Column(
        "post_id",
        db.Integer,
        db.ForeignKey("posts.post_id"),
    ),
)

Post_member = db.Table(
    "post_members",
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id")),
    db.Column(
        "post_id",
        db.Integer,
        db.ForeignKey("posts.post_id"),
    ),
)


class Role(db.Model):
    __tablename__ = "roles"

    def __init__(self, role_id, name):
        self.role_id = role_id
        self.role_name = name

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True)

    users = db.relationship("User", backref="role")

    def __repr__(self):
        return f"id: {self.role_id}, type: {self.role_name}"


class User(db.Model, UserMixin):
    __tablename__ = "users"

    def __init__(self, email, name, nickname, password, phone, credit_score, role_id):
        self.email = email
        self.name = name
        self.nickname = nickname
        self.password = password
        self.phone = phone
        self.credit_score = credit_score
        self.role_id = role_id

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150), unique=True)
    nickname = db.Column(db.String(20))
    password = db.Column(db.String(150))
    credit_score = db.Column(db.Integer())
    phone = db.Column(db.String(10))


    role_id = db.Column(db.ForeignKey("roles.role_id"))

    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f"id: {self.user_id}, email: {self.email}, name: {self.name}, nickname: {self.nickname}, credit score: {self.credit_score}, role: {self.role_id}"


# 分類
class Forum(db.Model):
    __tablename__ = "forums"

    def __init__(self, name, description, user_id):
        self.name = name
        self.description = description
        self.user_id = user_id

    forum_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    description = db.Column(db.String(150), unique=True)
    user_id = db.Column(db.ForeignKey("users.user_id"))

    users = db.relationship("User", secondary=Forum_user, backref="forums")

    def __repr__(self):
        return f"id: {self.forum_id}, name: {self.name}"


# 事件
class Post(db.Model):
    __tablename__ = "posts"

    def __init__(self, title, tags, content, start, end, meeting_point, destination, max_participants, user_id, forum_id):
        self.title = title
        self.tags = tags
        self.content = content
        self.start = start
        self.end = end
        self.meeting_point = meeting_point
        self.destination = destination
        self.max_participants = max_participants
        self.report = False
        self.user_id = user_id
        self.forum_id = forum_id

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    tags = db.Column(db.String(20))
    content = db.Column(db.String(300))
    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    meeting_point = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    max_participants = db.Column(db.Integer)
    report = db.Column(db.Boolean)

    user_id = db.Column(db.ForeignKey("users.user_id"))
    forum_id = db.Column(db.ForeignKey("forums.forum_id"))

    author = db.relationship("User", backref="posts")
    forum = db.relationship("Forum", backref="posts")
    likes = db.relationship("User", secondary=Post_likes, backref="likes")
    members = db.relationship("User", secondary=Post_member, backref="events")

    def __repr__(self):
        return f"id: {self.post_id}, title: {self.title}, tag: {self.tag}, content: {self.content}, likes: {self.likes}, date: {self.date}, report: {self.report}, user_id: {self.user_id}, forum_id: {self.forum_id}"


# 聊天內容
class Comment(db.Model):
    __tablename__ = "comments"

    def __init__(self, text, user_id, post_id):
        self.text = text
        self.user_id = user_id
        self.post_id = post_id

    comment_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))

    user_id = db.Column(db.ForeignKey("users.user_id"))
    post_id = db.Column(db.ForeignKey("posts.post_id"))

    user = db.relationship("User", backref="comments")
    post = db.relationship("Post", backref="comments")


class Report(db.Model):
    __tablename__ = "reports"

    def __init__(self, reason, user_id, post_id):
        self.reason = reason
        self.user_id = user_id
        self.post_id = post_id
    
    report_id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(50))

    user_id = db.Column(db.ForeignKey("users.user_id"))
    post_id = db.Column(db.ForeignKey("posts.post_id"))

    post = db.relationship("Post", backref="reports")

    def __repr__(self):
        return f"id: {self.report_id}, reason: {self.reason}, post_id: {self.post_id}"
