from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, IntegerField
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