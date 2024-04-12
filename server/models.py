from flask import Flask, session
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'secret-key'
api = Api(app)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username
        }

@app.before_first_request
def create_tables():
    db.create_all()

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, location='json')
        args = parser.parse_args()

        user = User.query.filter_by(username=args['username']).first()
        if user:
            session['user_id'] = user.id
            return user.serialize(), 200
        else:
            return {'message': 'User not found'}, 404

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id', None)
            return '', 204
        else:
            return '', 401

class CheckSession(Resource):
    def get(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return user.serialize(), 200
        else:
            return '', 401

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(debug=True)