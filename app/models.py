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
    
    # NOVOS CAMPOS PARA PERFIL PROFISSIONAL (MOÇAMBIQUE)
    telefone = db.Column(db.String(20))
    nuit = db.Column(db.String(9))  # NUIT pessoal (9 dígitos)
    genero = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    cargo = db.Column(db.String(50))
    departamento = db.Column(db.String(50))
    tipo_empresa = db.Column(db.String(50))
    nuit_empresa = db.Column(db.String(9))  # NUIT da empresa
    provincia = db.Column(db.String(50))
    cidade = db.Column(db.String(50))
    bairro = db.Column(db.String(100))
    endereco_completo = db.Column(db.Text)
    telefone_alternativo = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    data_ultimo_acesso = db.Column(db.DateTime)
    ativo = db.Column(db.Boolean, default=True)
    
    # NOVOS CAMPOS PARA SISTEMA DE ACESSO POR ETAPAS
    perfil_completo = db.Column(db.Boolean, default=False)
    nivel_acesso = db.Column(db.String(20), default='limitado')  # limitado, completo
    
    # NOVOS CAMPOS PARA SEGURANÇA E CONFIABILIDADE
    telefone_verificado = db.Column(db.Boolean, default=False)
    nuit_verificado = db.Column(db.Boolean, default=False)
    empresa_validada = db.Column(db.Boolean, default=False)
    pontuacao_confiabilidade = db.Column(db.Integer, default=100)
    agendamentos_concluidos = db.Column(db.Integer, default=0)
    agendamentos_cancelados = db.Column(db.Integer, default=0)
    
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

    # NOVOS MÉTODOS PARA RECUPERAÇÃO DE SENHA
    def gerar_token_recuperacao(self):
        """Gera um token único para recuperação de senha"""
        self.token_confirmacao = secrets.token_urlsafe(32)
        return self.token_confirmacao

    def verificar_token_recuperacao(self, token):
        """Verifica se o token de recuperação é válido"""
        return secrets.compare_digest(self.token_confirmacao, token)

    # NOVO MÉTODO PARA ATUALIZAR DATA DE ÚLTIMO ACESSO
    def atualizar_ultimo_acesso(self):
        """Atualiza a data do último acesso"""
        self.data_ultimo_acesso = datetime.utcnow()
        db.session.commit()

    # NOVOS MÉTODOS PARA SISTEMA DE ACESSO POR ETAPAS
    def tem_acesso_completo(self):
        """Verifica se o usuário tem acesso completo ao sistema"""
        return self.nivel_acesso == 'completo' and self.perfil_completo

    def verificar_campos_obrigatorios(self):
        """Verifica se todos os campos obrigatórios do perfil estão preenchidos"""
        campos_obrigatorios = [
            self.telefone,
            self.nuit,
            self.genero,
            self.data_nascimento,
            self.cargo,
            self.departamento,
            self.tipo_empresa,
            self.nuit_empresa,
            self.provincia,
            self.cidade,
            self.bairro,
            self.endereco_completo
        ]
        return all(campo is not None and str(campo).strip() != '' for campo in campos_obrigatorios)

    def completar_perfil(self):
        """Marca o perfil como completo e concede acesso total"""
        if self.verificar_campos_obrigatorios():
            self.perfil_completo = True
            self.nivel_acesso = 'completo'
            return True
        return False

    def get_nivel_acesso_display(self):
        """Retorna a descrição do nível de acesso"""
        return {
            'limitado': 'Acesso Limitado',
            'completo': 'Acesso Completo'
        }.get(self.nivel_acesso, 'Acesso Limitado')

    def pode_agendar(self):
        """Verifica se o usuário pode fazer agendamentos"""
        return self.tem_acesso_completo() and self.ativo

    def pode_ver_dashboard(self):
        """Verifica se o usuário pode acessar o dashboard completo"""
        return self.tem_acesso_completo()

    # NOVOS MÉTODOS PARA SEGURANÇA E CONFIABILIDADE
    def calcular_confiabilidade(self):
        """Calcula pontuação de confiabilidade baseada no histórico"""
        base = 100
        penalidade_cancelamentos = self.agendamentos_cancelados * 5
        bonus_concluidos = self.agendamentos_concluidos * 2
        
        self.pontuacao_confiabilidade = max(0, base - penalidade_cancelamentos + bonus_concluidos)
        return self.pontuacao_confiabilidade

    def get_status_verificacao(self):
        """Retorna o status de verificação do usuário"""
        verificacoes = [
            ('Email', self.email_confirmado),
            ('Telefone', self.telefone_verificado),
            ('NUIT', self.nuit_verificado),
            ('Empresa', self.empresa_validada)
        ]
        return verificacoes

    def get_nivel_verificacao(self):
        """Retorna o nível de verificação (0-4)"""
        return sum([self.email_confirmado, self.telefone_verificado, 
                   self.nuit_verificado, self.empresa_validada])

    def pode_acessar_recurso_avancado(self):
        """Verifica se pode acessar recursos avançados"""
        return (self.get_nivel_verificacao() >= 2 and 
                self.pontuacao_confiabilidade >= 80)

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