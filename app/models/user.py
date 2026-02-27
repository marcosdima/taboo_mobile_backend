from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), unique=True, nullable=False)


    def to_dict(self):
        return {
            'id': self.id,
            'alias': self.alias,
        }


    def __repr__(self):
        return f'<User {self.alias}>'
