
from flask import request
from flask_restful import Resource
from models import db, User, Bank, Transaction

# -------------------- USER --------------------
class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "role": user.role
        }

# -------------------- BANK --------------------
class BankListResource(Resource):
    def get(self):
        user_id = request.args.get("user_id")
        if not user_id:
            return {"message": "Missing user_id"}, 400

        banks = Bank.query.filter_by(user_id=user_id).all()
        return [
            {
                "id": b.id,
                "bankaccount": b.bankaccount,
                "name": b.name,
                "bname": b.bname,
                "ifsc": b.ifsc
            } for b in banks
        ]

    def post(self):
        data = request.get_json()
        user_id = data.get("user_id")
        if not user_id:
            return {"message": "Missing user_id"}, 400

        new_bank = Bank(
            bankaccount=data.get("bankaccount"),
            name=data.get("name"),
            bname=data.get("bname"),
            ifsc=data.get("ifsc"),
            user_id=user_id
        )
        db.session.add(new_bank)
        db.session.commit()
        return {"message": "Bank added successfully."}, 201

class BankResource(Resource):
    def get(self, bank_id):
        bank = Bank.query.get_or_404(bank_id)
        return {
            "id": bank.id,
            "bankaccount": bank.bankaccount,
            "name": bank.name,
            "bname": bank.bname,
            "ifsc": bank.ifsc
        }

    def put(self, bank_id):
        bank = Bank.query.get_or_404(bank_id)
        data = request.get_json()
        bank.bankaccount = data.get("bankaccount", bank.bankaccount)
        bank.name = data.get("name", bank.name)
        bank.bname = data.get("bname", bank.bname)
        bank.ifsc = data.get("ifsc", bank.ifsc)
        db.session.commit()
        return {"message": "Bank updated successfully."}

    def delete(self, bank_id):
        bank = Bank.query.get_or_404(bank_id)
        db.session.delete(bank)
        db.session.commit()
        return {"message": "Bank deleted successfully."}

# -------------------- TRANSACTION --------------------
class TransactionListResource(Resource):
    def get(self):
        user_id = request.args.get("user_id")
        if not user_id:
            return {"message": "Missing user_id"}, 400

        transactions = Transaction.query.filter_by(user_id=user_id).all()
        return [
            {
                "id": t.id,
                "category": t.category,
                "amount": t.amount,
                "description": t.description or ""
            } for t in transactions
        ]

    def post(self):
        data = request.get_json()
        user_id = data.get("user_id")
        if not user_id:
            return {"message": "Missing user_id"}, 400
        if not data.get("category") or not data.get("amount"):
            return {"message": "Category and amount are required."}, 400

        new_transaction = Transaction(
            category=data["category"],
            amount=float(data["amount"]),
            description=data.get("description", ""),
            user_id=user_id
        )
        db.session.add(new_transaction)
        db.session.commit()
        return {"message": "Transaction added successfully."}, 201

class TransactionResource(Resource):
    def get(self, transaction_id):
        t = Transaction.query.get_or_404(transaction_id)
        user_id = request.args.get("user_id")
        if not user_id or str(t.user_id) != str(user_id):
            return {"message": "Unauthorized access"}, 403

        return {
            "id": t.id,
            "category": t.category,
            "amount": t.amount,
            "description": t.description or ""
        }

    def put(self, transaction_id):
        t = Transaction.query.get_or_404(transaction_id)
        user_id = request.args.get("user_id")
        if not user_id or str(t.user_id) != str(user_id):
            return {"message": "Unauthorized update"}, 403

        data = request.get_json()
        t.category = data.get("category", t.category)
        t.amount = float(data.get("amount", t.amount))
        t.description = data.get("description", t.description)
        db.session.commit()
        return {"message": "Transaction updated successfully."}

    def delete(self, transaction_id):
        t = Transaction.query.get_or_404(transaction_id)
        user_id = request.args.get("user_id")
        if not user_id or str(t.user_id) != str(user_id):
            return {"message": "Unauthorized delete"}, 403

        db.session.delete(t)
        db.session.commit()
        return {"message": "Transaction deleted successfully."}