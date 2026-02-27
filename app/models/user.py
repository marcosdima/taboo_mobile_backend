from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    

    ID = 'id'
    ALIAS = 'alias'
    PASSWORD = 'password_hash'


    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def to_dict(self):
        return {
            'id': self.id,
            'alias': self.alias,
        }


    def __repr__(self):
        return f'<User {self.alias}>'

