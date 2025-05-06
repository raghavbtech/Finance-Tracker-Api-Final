
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api
from models import db, bcrypt
from api import (
    UserResource, 
    TransactionListResource, TransactionResource,
    BankListResource, BankResource
)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'SECRETKEY'

db.init_app(app)
bcrypt.init_app(app)

api = Api(app)

# Transaction endpoints
api.add_resource(TransactionListResource, "/api/transactions")
api.add_resource(TransactionResource, "/api/transactions/<int:transaction_id>")

# Bank endpoints 
api.add_resource(BankListResource, "/api/banks")
api.add_resource(BankResource, "/api/banks/<int:bank_id>")

# user info
api.add_resource(UserResource, "/api/user/<int:user_id>")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
