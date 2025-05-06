from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import db, User, Bank
from app import app, bcrypt, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('showbank'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/showbank')
@login_required
def showbank():
    banks = Bank.query.filter_by(user_id=current_user.id).all()
    return render_template('showbank.html', user=current_user, banks=banks)



@app.route('/delete_bank/<int:bankaccount1>', methods=['POST'])
def delete_bank(bankaccount1):

    bank_account = Bank.query.filter_by(bankaccount=bankaccount1).first()
    if bank_account:
        db.session.delete(bank_account)
        db.session.commit()
        flash('Bank account deleted successfully!', 'success')
    else:
        flash('Bank account not found!', 'error')

    return redirect(url_for('showbank'))  # Redirect to the dashboard or appropriate page

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

