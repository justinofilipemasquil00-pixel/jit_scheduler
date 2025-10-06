from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Login simples para teste - mantendo os usuários de teste
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Verificar usuários de teste
        if email == 'admin@jit.com' and password == 'admin123':        
            user = User.query.filter_by(email=email).first()
            if not user:
                # Criar usuario admin se não existir
                user = User(email=email, nome='Administrador', empresa='JIT', tipo='admin')
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))

        elif email == 'usuario@jit.com' and password == 'user123':     
            user = User.query.filter_by(email=email).first()
            if not user:
                # Criar usuario comum se não existir
                user = User(email=email, nome='Usuário Teste', empresa='Teste Ltda', tipo='usuario')
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('usuario.dashboard'))

        # Verificar usuários do banco de dados
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('usuario.dashboard'))
        else:
            flash('Email ou senha inválidos', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Verificar se o email já existe
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Este email já está cadastrado. Use outro email ou faça login.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Criar novo usuário
        user = User(
            email=form.email.data,
            nome=form.nome.data,
            empresa=form.empresa.data,
            tipo='usuario'  # Todos os novos usuários são usuários comuns
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('main.index'))