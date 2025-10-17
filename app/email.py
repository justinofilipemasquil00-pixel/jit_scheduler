from flask_mail import Message
from flask import render_template, current_app, url_for  # ADICIONE url_for AQUI
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_agendamento_confirmacao(agendamento):
    """Envia email de confirmação de agendamento"""
    subject = current_app.config['EMAIL_SUBJECT_PREFIX'] + 'Confirmação de Agendamento'
    
    # Corpo do email em texto simples
    text_body = f"""
    Prezado(a) {agendamento.usuario.nome},
    
    Seu agendamento foi confirmado com sucesso!
    
    Detalhes do Agendamento:
    - Doca: {agendamento.doca.numero} - {agendamento.doca.terminal.nome}
    - Data e Hora: {agendamento.data_agendamento.strftime('%d/%m/%Y às %H:%M')}
    - Duração: {agendamento.duracao_estimada} minutos
    - Tipo de Operação: {agendamento.tipo_operacao.title()}
    - Veículo: {agendamento.placa_veiculo}
    - Motorista: {agendamento.nome_motorista}
    
    Por favor, apresente-se no terminal com 15 minutos de antecedência.
    
    Atenciosamente,
    Equipe Sistema JIT
    """
    
    # Corpo do email em HTML
    html_body = render_template('email/agendamento_confirmacao.html', 
                               agendamento=agendamento)
    
    send_email(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[agendamento.usuario.email],
        text_body=text_body,
        html_body=html_body
    )

def send_agendamento_cancelamento(agendamento):
    """Envia email de cancelamento de agendamento"""
    subject = current_app.config['EMAIL_SUBJECT_PREFIX'] + 'Cancelamento de Agendamento'
    
    text_body = f"""
    Prezado(a) {agendamento.usuario.nome},
    
    Seu agendamento foi cancelado.
    
    Detalhes do Agendamento Cancelado:
    - Doca: {agendamento.doca.numero} - {agendamento.doca.terminal.nome}
    - Data e Hora: {agendamento.data_agendamento.strftime('%d/%m/%Y às %H:%M')}
    - Motivo do Cancelamento: {agendamento.motivo_cancelamento or 'Não informado'}
    
    Se precisar fazer um novo agendamento, acesse nosso sistema.
    
    Atenciosamente,
    Equipe Sistema JIT
    """
    
    html_body = render_template('email/agendamento_cancelamento.html',
                               agendamento=agendamento)
    
    send_email(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[agendamento.usuario.email],
        text_body=text_body,
        html_body=html_body
    )

def send_novo_agendamento_admin(agendamento):
    """Notifica admin sobre novo agendamento pendente"""
    from app.models import User
    
    # Buscar todos os administradores
    admins = User.query.filter_by(tipo='admin').all()
    admin_emails = [admin.email for admin in admins]
    
    if not admin_emails:
        return
    
    subject = current_app.config['EMAIL_SUBJECT_PREFIX'] + 'Novo Agendamento Pendente'
    
    text_body = f"""
    Novo agendamento pendente de aprovação:
    
    Detalhes:
    - Usuário: {agendamento.usuario.nome} ({agendamento.usuario.email})
    - Empresa: {agendamento.usuario.empresa}
    - Doca: {agendamento.doca.numero} - {agendamento.doca.terminal.nome}
    - Data e Hora: {agendamento.data_agendamento.strftime('%d/%m/%Y às %H:%M')}
    - Duração: {agendamento.duracao_estimada} minutos
    - Veículo: {agendamento.placa_veiculo}
    - Motorista: {agendamento.nome_motorista}
    
    Acesse o sistema para aprovar ou rejeitar este agendamento.
    """
    
    html_body = render_template('email/novo_agendamento_admin.html',
                               agendamento=agendamento)
    
    send_email(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=admin_emails,
        text_body=text_body,
        html_body=html_body
    )

def send_agendamento_rejeitado(agendamento):
    """Envia email quando agendamento é rejeitado pelo admin"""
    subject = current_app.config['EMAIL_SUBJECT_PREFIX'] + 'Agendamento Rejeitado'
    
    text_body = f"""
    Prezado(a) {agendamento.usuario.nome},
    
    Seu agendamento foi rejeitado.
    
    Detalhes do Agendamento Rejeitado:
    - Doca: {agendamento.doca.numero} - {agendamento.doca.terminal.nome}
    - Data e Hora: {agendamento.data_agendamento.strftime('%d/%m/%Y às %H:%M')}
    - Veículo: {agendamento.placa_veiculo}
    
    Entre em contato conosco para mais informações ou faça um novo agendamento.
    
    Atenciosamente,
    Equipe Sistema JIT
    """
    
    html_body = render_template('email/agendamento_rejeitado.html',
                               agendamento=agendamento)
    
    send_email(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[agendamento.usuario.email],
        text_body=text_body,
        html_body=html_body
    )

def send_email_confirmacao(user):
    """Envia email de confirmação de conta"""
    subject = current_app.config['EMAIL_SUBJECT_PREFIX'] + 'Confirme sua Conta'

    # Gerar token de confirmação
    token = user.gerar_token_confirmacao()
    
    # Corpo do email em texto simples
    text_body = f"""
    Prezado(a) {user.nome},

    Bem-vindo ao Sistema JIT!

    Para confirmar sua conta, clique no link abaixo:

    {url_for('auth.confirmar_email', token=token, _external=True)}

    Se você não criou esta conta, por favor ignore este email.

    Atenciosamente,
    Equipe Sistema JIT
    """

    # Corpo do email em HTML
    html_body = render_template('email/confirmar_conta.html',
                               user=user, token=token)

    send_email(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    )

# NOVA FUNÇÃO PARA RECUPERAÇÃO DE SENHA
def send_email_recuperacao_senha(user):
    """Envia email para recuperação de senha"""
    subject = current_app.config['EMAIL_SUBJECT_PREFIX'] + 'Recuperação de Senha'

    # Gerar token de recuperação
    token = user.gerar_token_recuperacao()
    
    # Corpo do email em texto simples
    text_body = f"""
    Prezado(a) {user.nome},

    Recebemos uma solicitação para redefinir a senha da sua conta no Sistema JIT.

    Para redefinir sua senha, clique no link abaixo:

    {url_for('auth.recuperar_senha_token', token=token, _external=True)}

    Este link expirará em 1 hora.

    Se você não solicitou a redefinição de senha, por favor ignore este email.

    Atenciosamente,
    Equipe Sistema JIT
    """

    # Corpo do email em HTML
    html_body = render_template('email/recuperar_senha.html',
                               user=user, token=token)

    send_email(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    )
    