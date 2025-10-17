from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    nome = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(100))
    tipo = db.Column(db.String(20), default='usuario')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NOVOS CAMPOS PARA CONFIRMAÇÃO DE EMAIL
    email_confirmado = db.Column(db.Boolean, default=False)
    token_confirmacao = db.Column(db.String(100))
    
    agendamentos = db.relationship('Agendamento', backref='usuario', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.tipo == 'admin'

    # NOVOS MÉTODOS PARA CONFIRMAÇÃO DE EMAIL
    def gerar_token_confirmacao(self):
        """Gera um token único para confirmação de email"""
        self.token_confirmacao = secrets.token_urlsafe(32)
        return self.token_confirmacao

    def verificar_token_confirmacao(self, token):
        """Verifica se o token de confirmação é válido"""
        return secrets.compare_digest(self.token_confirmacao, token)

    def confirmar_email(self):
        """Marca o email como confirmado"""
        self.email_confirmado = True
        self.token_confirmacao = None

    def __repr__(self):
        return f'User({self.email}, {self.nome})'

class Terminal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    telefone = db.Column(db.String(20))
    horario_abertura = db.Column(db.Time, default='08:00')
    horario_fechamento = db.Column(db.Time, default='18:00')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    docas = db.relationship('Doca', backref='terminal', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'Terminal({self.nome})'

class Doca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    terminal_id = db.Column(db.Integer, db.ForeignKey('terminal.id'), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    tipo_carga = db.Column(db.String(50), default='geral')
    status = db.Column(db.String(20), default='ativa')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    agendamentos = db.relationship('Agendamento', backref='doca', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'Doca({self.numero}, Terminal: {self.terminal.nome})'

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doca_id = db.Column(db.Integer, db.ForeignKey('doca.id'), nullable=False)
    data_agendamento = db.Column(db.DateTime, nullable=False)
    duracao_estimada = db.Column(db.Integer, default=60)
    tipo_operacao = db.Column(db.String(20), nullable=False)
    tipo_carga = db.Column(db.String(50))
    placa_veiculo = db.Column(db.String(10), nullable=False)
    nome_motorista = db.Column(db.String(100), nullable=False)
    telefone_motorista = db.Column(db.String(20))
    observacoes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pendente')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NOVOS CAMPOS PARA CANCELAMENTO
    data_cancelamento = db.Column(db.DateTime)
    motivo_cancelamento = db.Column(db.Text)

    def __repr__(self):
        return f'Agendamento({self.id}, {self.data_agendamento}, {self.status})'
    
    # MÉTODO PARA VERIFICAR SE PODE SER CANCELADO
    def pode_ser_cancelado(self):
        agora = datetime.utcnow()
        # Não pode cancelar agendamentos que já passaram
        if self.data_agendamento <= agora:
            return False
        # Só pode cancelar agendamentos pendentes ou confirmados
        return self.status in ['pendente', 'confirmado']