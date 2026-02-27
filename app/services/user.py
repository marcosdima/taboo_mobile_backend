from app.extensions import db
from app.models import User


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