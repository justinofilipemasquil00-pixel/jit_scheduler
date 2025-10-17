from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import RegistrationForm, RecuperacaoSenhaForm, RedefinirSenhaForm  # ATUALIZE ESTA LINHA
from app.email import send_email_confirmacao, send_email_recuperacao_senha  # ADICIONE send_email_recuperacao_senha

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
                user.email_confirmado = True  # Admin não precisa confirmar email
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
                user.email_confirmado = True  # Usuário teste não precisa confirmar
                db.session.add(user)
                db.session.commit()
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('usuario.dashboard'))

        # Verificar usuários do banco de dados
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # VERIFICAR SE EMAIL ESTÁ CONFIRMADO
            if not user.email_confirmado:
                flash('Por favor, confirme seu email antes de fazer login. Verifique sua caixa de entrada.', 'warning')
                return render_template('auth/login.html')
                
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
        
        # Gerar token de confirmação
        user.gerar_token_confirmacao()

        db.session.add(user)
        db.session.commit()
        
        # ENVIAR EMAIL DE CONFIRMAÇÃO
        try:
            send_email_confirmacao(user)
            flash('Conta criada com sucesso! Enviamos um email de confirmação para você.', 'success')
        except Exception as e:
            flash('Conta criada, mas houve um erro ao enviar o email de confirmação. Entre em contato com o suporte.', 'warning')
            print(f"Erro ao enviar email: {e}")

        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/confirmar-email/<token>')
def confirmar_email(token):
    """Rota para confirmar o email do usuário"""
    user = User.query.filter_by(token_confirmacao=token).first()
    
    if not user:
        flash('Link de confirmação inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Confirmar o email
    user.confirmar_email()
    db.session.commit()
    
    flash('Email confirmado com sucesso! Agora você pode fazer login.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reenviar-confirmacao')
@login_required
def reenviar_confirmacao():
    """Rota para reenviar email de confirmação"""
    if current_user.email_confirmado:
        flash('Seu email já está confirmado.', 'info')
        return redirect(url_for('usuario.dashboard' if not current_user.is_admin() else 'admin.dashboard'))
    
    try:
        current_user.gerar_token_confirmacao()
        db.session.commit()
        send_email_confirmacao(current_user)
        flash('Email de confirmação reenviado! Verifique sua caixa de entrada.', 'success')
    except Exception as e:
        flash('Erro ao reenviar email de confirmação. Tente novamente.', 'danger')
        print(f"Erro ao reenviar email: {e}")
    
    return redirect(url_for('usuario.dashboard' if not current_user.is_admin() else 'admin.dashboard'))

# NOVAS ROTAS PARA RECUPERAÇÃO DE SENHA
@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    """Rota para solicitar recuperação de senha"""
    form = RecuperacaoSenhaForm()
    
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Gerar token e enviar email
            try:
                user.gerar_token_recuperacao()
                db.session.commit()
                send_email_recuperacao_senha(user)
                flash('Enviamos um email com instruções para redefinir sua senha.', 'info')
            except Exception as e:
                flash('Erro ao enviar email de recuperação. Tente novamente.', 'danger')
                print(f"Erro ao enviar email: {e}")
        else:
            # Mesma mensagem para evitar enumeração de emails
            flash('Se o email estiver cadastrado, enviaremos instruções para redefinir sua senha.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/recuperar_senha.html', form=form)

@auth_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def recuperar_senha_token(token):
    """Rota para redefinir a senha usando o token"""
    user = User.query.filter_by(token_confirmacao=token).first()
    
    if not user:
        flash('Link de recuperação inválido ou expirado.', 'danger')
        return redirect(url_for('auth.recuperar_senha'))
    
    form = RedefinirSenhaForm()
    
    if form.validate_on_submit():
        # Redefinir senha
        user.set_password(form.password.data)
        user.token_confirmacao = None  # Limpar token
        db.session.commit()
        
        flash('Senha redefinida com sucesso! Faça login com a nova senha.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/redefinir_senha.html', form=form, token=token)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('main.index'))