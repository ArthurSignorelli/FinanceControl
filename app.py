from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Transaction
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Criação do banco
with app.app_context():
    if not os.path.exists('database.db'):
        db.create_all()

# Página inicial pública
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Dashboard protegido
@app.route('/dashboard')
@login_required
def dashboard():
    receitas = Transaction.query.filter_by(type='receita', user_id=current_user.id).all()
    despesas = Transaction.query.filter_by(type='despesa', user_id=current_user.id).all()

    total_receitas = sum(r.amount for r in receitas)
    total_despesas = sum(d.amount for d in despesas)
    saldo = total_receitas - total_despesas

    return render_template('dashboard.html',
                           receitas=total_receitas,
                           despesas=total_despesas,
                           saldo=saldo)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        tipo = request.form.get('type')
        descricao = request.form.get('description')
        valor = request.form.get('amount')
        data = request.form.get('date')

        if not tipo or not descricao or not valor or not data:
            flash("Preencha todos os campos corretamente.")
            return redirect(url_for('add_transaction'))

        try:
            valor = float(valor)
        except ValueError:
            flash("Valor inválido.")
            return redirect(url_for('add_transaction'))

        nova = Transaction(type=tipo, description=descricao, amount=valor, date=data, user_id=current_user.id)
        db.session.add(nova)
        db.session.commit()
        flash("Transação adicionada com sucesso.")
        return redirect(url_for('dashboard'))

    return render_template('add_transaction.html')

@app.route('/transactions')
@login_required
def transactions():
    transacoes = Transaction.query.filter_by(user_id=current_user.id).all()
    return render_template('transactions.html', transacoes=transacoes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('username')
        senha = request.form.get('password')
        user = User.query.filter_by(username=usuario).first()
        if user and check_password_hash(user.password, senha):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form.get('username')
        senha = request.form.get('password')
        if not usuario or not senha:
            flash("Preencha todos os campos.")
            return redirect(url_for('register'))

        hash_senha = generate_password_hash(senha)

        if User.query.filter_by(username=usuario).first():
            flash('Usuário já existe')
            return redirect(url_for('register'))

        novo_user = User(username=usuario, password=hash_senha)
        db.session.add(novo_user)
        db.session.commit()
        flash('Usuário cadastrado com sucesso. Faça login.')
        return redirect(url_for('login'))

    return render_template('login.html', cadastro=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
