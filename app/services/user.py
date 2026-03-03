from app.extensions import db
from app.models import User
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import BadSignature, SignatureExpired
from flask import current_app


class UserService:
    def create_user(self, data):
        alias = data.get("alias")
        password = data.get("password")

        if not alias or not password:
            raise ValueError("Alias and password required")

        if User.query.filter_by(alias=alias).first():
            raise ValueError("Alias already exists")

        user = User(alias=alias)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user.to_dict()


    def get_user(self, user_id):
        user = User.query.get(user_id)
        return user.to_dict() if user else None


    def get_all_users(self):
        users = User.query.all()
        return [user.to_dict() for user in users]


    def update_user(self, user_id, data):
        user = User.query.get(user_id)
        if user:
            user.alias = data.get('alias', user.alias)
            if data.get('password'):
                user.set_password(data.get('password'))
            db.session.commit()
        return user.to_dict() if user else None


    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    
    def user_exists(self, id):
        return User.query.filter_by(id=id).first() is not None


    def authenticate_user(self, alias, password):
        if not alias or not password:
            return None

        user = User.query.filter_by(alias=alias).first()
        if not user or not user.check_password(password):
            return None

        return user


    def generate_token(self, user):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps({"user_id": user.id, "alias": user.alias})


    def get_user_from_token(self, token, max_age=86400):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

        try:
            payload = serializer.loads(token, max_age=max_age)
        except (BadSignature, SignatureExpired):
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        return User.query.get(user_id)