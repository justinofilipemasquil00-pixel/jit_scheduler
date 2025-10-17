from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional
from app.models import Doca, User
from datetime import datetime
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo

class AgendamentoForm(FlaskForm):
    doca_id = SelectField('Doca', coerce=int, validators=[DataRequired()], choices=[])
    data_agendamento = DateTimeField('Data e Hora do Agendamento', 
                                   format='%Y-%m-%d %H:%M', 
                                   validators=[DataRequired()],
                                   render_kw={
                                       "placeholder": "Clique para selecionar data e hora",
                                       "id": "datetimepicker",
                                       "class": "form-control",
                                       "autocomplete": "off"
                                   })
    duracao_estimada = IntegerField('Duração Estimada (minutos)', 
                                   default=60, 
                                   validators=[DataRequired()],
                                   render_kw={"placeholder": "60"})
    tipo_operacao = SelectField('Tipo de Operação', 
                               choices=[
                                   ('', 'Selecione o tipo de operação'),
                                   ('carga', 'Carga'),
                                   ('descarga', 'Descarga'),
                                   ('ambos', 'Carga e Descarga')
                               ], 
                               validators=[DataRequired()])
    tipo_carga = SelectField('Tipo de Carga', 
                            choices=[
                                ('', 'Selecione o tipo de carga'),
                                ('geral', 'Carga Geral'),
                                ('frigorifica', 'Carga Frigorífica'),
                                ('perigosa', 'Carga Perigosa'),
                                ('granel', 'Granel')
                            ], 
                            validators=[DataRequired()])
    placa_veiculo = StringField('Placa do Veículo', 
                               validators=[DataRequired(), Length(min=7, max=8)],
                               render_kw={"placeholder": "ABC1D23"})
    nome_motorista = StringField('Nome do Motorista', 
                                validators=[DataRequired()],
                                render_kw={"placeholder": "Nome completo"})
    telefone_motorista = StringField('Telefone do Motorista',
                                    validators=[Optional()],
                                    render_kw={"placeholder": "(11) 99999-9999"})
    observacoes = TextAreaField('Observações',
                               validators=[Optional()],
                               render_kw={"rows": 3, "placeholder": "Observações adicionais..."})
    submit = SubmitField('Solicitar Agendamento')

class RegistrationForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    empresa = StringField('Empresa', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Criar Conta')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado. Use outro email ou faça login.')

# NOVO FORMULÁRIO PARA CANCELAMENTO
class CancelamentoForm(FlaskForm):
    motivo_cancelamento = TextAreaField('Motivo do Cancelamento', 
                                      validators=[DataRequired()],
                                      render_kw={
                                          "rows": 4,
                                          "placeholder": "Descreva o motivo do cancelamento...",
                                          "class": "form-control"
                                      })
    submit = SubmitField('Confirmar Cancelamento', 
                        render_kw={"class": "btn btn-danger"})

# NOVOS FORMULÁRIOS PARA RECUPERAÇÃO DE SENHA
class RecuperacaoSenhaForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(), Email()],
                       render_kw={
                           "placeholder": "seu@email.com",
                           "class": "form-control"
                       })
    submit = SubmitField('Enviar Link de Recuperação',
                        render_kw={"class": "btn btn-primary"})

class RedefinirSenhaForm(FlaskForm):
    password = PasswordField('Nova Senha', 
                            validators=[DataRequired(), Length(min=6)],
                            render_kw={
                                "placeholder": "Mínimo 6 caracteres",
                                "class": "form-control"
                            })
    confirm_password = PasswordField('Confirmar Nova Senha', 
                                    validators=[DataRequired(), EqualTo('password')],
                                    render_kw={
                                        "placeholder": "Digite a senha novamente",
                                        "class": "form-control"
                                    })
    submit = SubmitField('Redefinir Senha',
                        render_kw={"class": "btn btn-success"})

# NOVOS FORMULÁRIOS PARA GERENCIAMENTO DE PERFIL
class EditarPerfilForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)],
                      render_kw={"class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                       render_kw={"class": "form-control"})
    empresa = StringField('Empresa', validators=[DataRequired(), Length(min=2, max=100)],
                         render_kw={"class": "form-control"})
    
    # Dados Pessoais
    telefone = StringField('Telefone',
                          render_kw={
                              "placeholder": "+258 84 123 4567",
                              "class": "form-control"
                          })
    nuit = StringField('NUIT Pessoal',
                      render_kw={
                          "placeholder": "123456789",
                          "class": "form-control"
                      })
    genero = SelectField('Gênero',
                        choices=[
                            ('', 'Selecione o gênero'),
                            ('masculino', 'Masculino'),
                            ('feminino', 'Feminino'),
                            ('outro', 'Outro')
                        ],
                        render_kw={"class": "form-control"})
    data_nascimento = DateField('Data de Nascimento',
                               format='%Y-%m-%d',
                               render_kw={
                                   "class": "form-control",
                                   "type": "date"
                               })
    
    # Dados Profissionais
    cargo = StringField('Cargo/Função',
                       render_kw={
                           "placeholder": "Gestor Logístico, Operador, etc.",
                           "class": "form-control"
                       })
    departamento = StringField('Departamento',
                              render_kw={
                                  "placeholder": "Logística, Compras, Distribuição",
                                  "class": "form-control"
                              })
    tipo_empresa = SelectField('Tipo de Empresa',
                              choices=[
                                  ('', 'Selecione o tipo de empresa'),
                                  ('importadora', 'Importadora'),
                                  ('exportadora', 'Exportadora'),
                                  ('transportadora', 'Transportadora'),
                                  ('comercio', 'Comércio'),
                                  ('industria', 'Indústria'),
                                  ('outro', 'Outro')
                              ],
                              render_kw={"class": "form-control"})
    nuit_empresa = StringField('NUIT da Empresa',
                              render_kw={
                                  "placeholder": "123456789",
                                  "class": "form-control"
                              })
    
    # Dados Geográficos
    provincia = SelectField('Província',
                           choices=[
                               ('', 'Selecione a província'),
                               ('maputo', 'Maputo'),
                               ('gaza', 'Gaza'),
                               ('inhambane', 'Inhambane'),
                               ('sofala', 'Sofala'),
                               ('manica', 'Manica'),
                               ('tete', 'Tete'),
                               ('zambezia', 'Zambézia'),
                               ('nampula', 'Nampula'),
                               ('cabo_delgado', 'Cabo Delgado'),
                               ('niassa', 'Niassa')
                           ],
                           render_kw={"class": "form-control"})
    cidade = StringField('Cidade',
                        render_kw={
                            "placeholder": "Maputo, Matola, Beira, etc.",
                            "class": "form-control"
                        })
    bairro = StringField('Bairro',
                        render_kw={
                            "placeholder": "Nome do bairro",
                            "class": "form-control"
                        })
    endereco_completo = TextAreaField('Endereço Completo',
                                     render_kw={
                                         "rows": 3,
                                         "placeholder": "Endereço completo para referência",
                                         "class": "form-control"
                                     })
    
    # Contatos Adicionais
    telefone_alternativo = StringField('Telefone Alternativo',
                                      render_kw={
                                          "placeholder": "+258 86 123 4567",
                                          "class": "form-control"
                                      })
    whatsapp = StringField('WhatsApp',
                          render_kw={
                              "placeholder": "+258 84 123 4567",
                              "class": "form-control"
                          })
    
    submit = SubmitField('Atualizar Perfil',
                        render_kw={"class": "btn btn-primary"})

class AlterarSenhaForm(FlaskForm):
    senha_atual = PasswordField('Senha Atual',
                               validators=[DataRequired()],
                               render_kw={
                                   "placeholder": "Digite sua senha atual",
                                   "class": "form-control"
                               })
    nova_senha = PasswordField('Nova Senha',
                              validators=[DataRequired(), Length(min=6)],
                              render_kw={
                                  "placeholder": "Mínimo 6 caracteres",
                                  "class": "form-control"
                              })
    confirmar_senha = PasswordField('Confirmar Nova Senha',
                                   validators=[DataRequired(), EqualTo('nova_senha')],
                                   render_kw={
                                       "placeholder": "Digite a nova senha novamente",
                                       "class": "form-control"
                                   })
    submit = SubmitField('Alterar Senha',
                        render_kw={"class": "btn btn-warning"})