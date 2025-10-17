from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Agendamento, Doca, User
from app.forms import AgendamentoForm, CancelamentoForm, EditarPerfilForm, AlterarSenhaForm, CompletarPerfilForm
from app import db
from datetime import datetime, timedelta
from app.email import send_agendamento_cancelamento, send_novo_agendamento_admin

usuario_bp = Blueprint('usuario', __name__)

# ROTA PARA COMPLETAR PERFIL OBRIGATÓRIO - APENAS UMA VEZ
@usuario_bp.route('/completar-perfil', methods=['GET', 'POST'])
@login_required
def completar_perfil():
    """Rota para completar perfil obrigatório - acesso total"""
    # Se já tem acesso completo, redireciona
    if current_user.tem_acesso_completo():
        flash('Seu perfil já está completo!', 'info')
        return redirect(url_for('usuario.dashboard'))
    
    form = CompletarPerfilForm()
    
    if form.validate_on_submit():
        try:
            # Atualizar dados obrigatórios
            current_user.telefone = form.telefone.data
            current_user.nuit = form.nuit.data
            current_user.genero = form.genero.data
            current_user.data_nascimento = form.data_nascimento.data
            current_user.cargo = form.cargo.data
            current_user.departamento = form.departamento.data
            current_user.tipo_empresa = form.tipo_empresa.data
            current_user.nuit_empresa = form.nuit_empresa.data
            current_user.provincia = form.provincia.data
            current_user.cidade = form.cidade.data
            current_user.bairro = form.bairro.data
            current_user.endereco_completo = form.endereco_completo.data
            
            # Contatos opcionais
            current_user.telefone_alternativo = form.telefone_alternativo.data
            current_user.whatsapp = form.whatsapp.data
            
            # Ativar acesso completo
            if current_user.completar_perfil():
                db.session.commit()
                flash('Perfil completado com sucesso! Agora você tem acesso total ao sistema.', 'success')
                return redirect(url_for('usuario.dashboard'))
            else:
                flash('Erro ao completar perfil. Verifique os campos obrigatórios.', 'danger')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar perfil: {str(e)}', 'danger')
    
    return render_template('usuario/completar_perfil.html', form=form)

@usuario_bp.route('/dashboard')
@login_required
def dashboard():
    # VERIFICAR ACESSO COMPLETO - SISTEMA DE ETAPAS
    if not current_user.tem_acesso_completo():
        flash('Complete seu perfil para ter acesso total ao sistema.', 'warning')
        return redirect(url_for('usuario.completar_perfil'))
    
    # Calcular estatísticas reais - VERSÃO CORRIGIDA E OTIMIZADA
    hoje = datetime.now().date()
    
    try:
        # Agendamentos de HOJE (data_agendamento é hoje)
        agendamentos_hoje = Agendamento.query.filter(
            db.func.date(Agendamento.data_agendamento) == hoje,
            Agendamento.user_id == current_user.id
        ).count()
        
        # Agendamentos CONFIRMADOS (qualquer data)
        agendamentos_confirmados = Agendamento.query.filter_by(
            user_id=current_user.id, 
            status='confirmado'
        ).count()
        
        # Agendamentos PENDENTES (qualquer data)
        agendamentos_pendentes = Agendamento.query.filter_by(
            user_id=current_user.id, 
            status='pendente'
        ).count()
        
        # TOTAL de agendamentos
        total_agendamentos = Agendamento.query.filter_by(
            user_id=current_user.id
        ).count()
        
        # PRÓXIMOS agendamentos (futuros + pendentes/confirmados)
        proximos_agendamentos = Agendamento.query.filter(
            Agendamento.user_id == current_user.id,
            Agendamento.data_agendamento >= datetime.now(),
            Agendamento.status.in_(['pendente', 'confirmado'])
        ).order_by(Agendamento.data_agendamento.asc()).limit(5).all()

        # DEBUG no console
        print(f"=== DASHBOARD DEBUG - Usuário: {current_user.nome} ===")
        print(f"Agendamentos hoje: {agendamentos_hoje}")
        print(f"Agendamentos confirmados: {agendamentos_confirmados}")
        print(f"Agendamentos pendentes: {agendamentos_pendentes}")
        print(f"Total agendamentos: {total_agendamentos}")
        print(f"Próximos agendamentos: {len(proximos_agendamentos)}")
        print("=" * 50)

    except Exception as e:
        print(f"ERRO no dashboard: {e}")
        # Valores padrão em caso de erro
        agendamentos_hoje = 0
        agendamentos_confirmados = 0
        agendamentos_pendentes = 0
        total_agendamentos = 0
        proximos_agendamentos = []

    return render_template('usuario/dashboard.html',
                           agendamentos_hoje=agendamentos_hoje,
                           agendamentos_confirmados=agendamentos_confirmados,
                           agendamentos_pendentes=agendamentos_pendentes,
                           total_agendamentos=total_agendamentos,
                           proximos_agendamentos=proximos_agendamentos)

@usuario_bp.route('/agendamentos')
@login_required
def agendamentos():
    # VERIFICAR ACESSO COMPLETO - SISTEMA DE ETAPAS
    if not current_user.tem_acesso_completo():
        flash('Complete seu perfil para visualizar seus agendamentos.', 'warning')
        return redirect(url_for('usuario.completar_perfil'))
    
    agendamentos_lista = Agendamento.query.filter_by(user_id=current_user.id).order_by(Agendamento.data_agendamento.desc()).all()
    
    # Adicionar informação se pode cancelar para cada agendamento
    for agendamento in agendamentos_lista:
        agendamento.pode_cancelar = agendamento.pode_ser_cancelado()
    
    return render_template('usuario/agendamentos.html', 
                         agendamentos=agendamentos_lista,
                         datetime=datetime)

@usuario_bp.route('/novo-agendamento', methods=['GET', 'POST'])
@login_required
def novo_agendamento():
    # VERIFICAR SE PODE AGENDAR - SISTEMA DE ETAPAS
    if not current_user.pode_agendar():
        flash('Complete seu perfil para poder fazer agendamentos.', 'warning')
        return redirect(url_for('usuario.completar_perfil'))
    
    form = AgendamentoForm()

    # Carregar docas disponíveis
    docas = Doca.query.filter_by(status='ativa').all()
    form.doca_id.choices = [(d.id, f'{d.terminal.nome} - Doca {d.numero} ({d.tipo_carga})') for d in docas]
    
    # CORREÇÃO: Usar -1 em vez de string vazia para evitar erro de conversão
    if form.doca_id.choices:
        form.doca_id.choices.insert(0, (-1, 'Selecione uma doca'))

    if form.validate_on_submit():
        # CORREÇÃO: Verificar se uma doca válida foi selecionada
        if form.doca_id.data == -1:
            flash('Por favor, selecione uma doca.', 'danger')
            return render_template('usuario/novo_agendamento.html', form=form)
        
        print("Formulário validado! Processando...")
        
        # Verificar conflito de horário
        conflito = Agendamento.query.filter(
            Agendamento.doca_id == form.doca_id.data,
            Agendamento.data_agendamento.between(
                form.data_agendamento.data - timedelta(minutes=form.duracao_estimada.data),
                form.data_agendamento.data + timedelta(minutes=form.duracao_estimada.data)
            ),
            Agendamento.status.in_(['pendente', 'confirmado'])
        ).first()

        if conflito:
            flash('Já existe um agendamento para esta doca neste horário!', 'danger')
            return render_template('usuario/novo_agendamento.html', form=form)

        # Criar agendamento
        agendamento = Agendamento(
            user_id=current_user.id,
            doca_id=form.doca_id.data,
            data_agendamento=form.data_agendamento.data,
            duracao_estimada=form.duracao_estimada.data,
            tipo_operacao=form.tipo_operacao.data,
            tipo_carga=form.tipo_carga.data,
            placa_veiculo=form.placa_veiculo.data.upper(),
            nome_motorista=form.nome_motorista.data,
            telefone_motorista=form.telefone_motorista.data,
            observacoes=form.observacoes.data,
            status='pendente'
        )

        db.session.add(agendamento)
        db.session.commit()

        # ENVIAR EMAIL PARA ADMINISTRADORES SOBRE NOVO AGENDAMENTO
        try:
            send_novo_agendamento_admin(agendamento)
            print("Email de notificação enviado para administradores")
        except Exception as e:
            print(f"Erro ao enviar email para admin: {e}")

        flash('Agendamento solicitado com sucesso! Aguarde a confirmação.', 'success')
        return redirect(url_for('usuario.agendamentos'))
    
    # Debug: mostrar erros de validação
    if request.method == 'POST' and not form.validate():
        print("Erros de validação:", form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erro no campo {getattr(form, field).label.text}: {error}', 'danger')

    return render_template('usuario/novo_agendamento.html', form=form)

# NOVA ROTA PARA CANCELAMENTO DE AGENDAMENTO
@usuario_bp.route('/agendamentos/<int:id>/cancelar', methods=['GET', 'POST'])
@login_required
def cancelar_agendamento(id):
    # VERIFICAR ACESSO COMPLETO - SISTEMA DE ETAPAS
    if not current_user.tem_acesso_completo():
        flash('Complete seu perfil para cancelar agendamentos.', 'warning')
        return redirect(url_for('usuario.completar_perfil'))
    
    agendamento = Agendamento.query.get_or_404(id)
    
    # Verificar se o agendamento pertence ao usuário logado
    if agendamento.user_id != current_user.id:
        flash('Você não tem permissão para cancelar este agendamento.', 'danger')
        return redirect(url_for('usuario.agendamentos'))
    
    # Verificar se pode ser cancelado
    if not agendamento.pode_ser_cancelado():
        flash('Este agendamento não pode ser cancelado.', 'warning')
        return redirect(url_for('usuario.agendamentos'))
    
    form = CancelamentoForm()
    
    if form.validate_on_submit():
        # Atualizar status e dados de cancelamento
        agendamento.status = 'cancelado'
        agendamento.motivo_cancelamento = form.motivo_cancelamento.data
        agendamento.data_cancelamento = datetime.utcnow()
        
        db.session.commit()
        
        # ENVIAR EMAIL DE CANCELAMENTO
        try:
            send_agendamento_cancelamento(agendamento)
            flash('Agendamento cancelado e email enviado!', 'success')
        except Exception as e:
            flash(f'Agendamento cancelado, mas erro ao enviar email: {str(e)}', 'warning')
        
        return redirect(url_for('usuario.agendamentos'))
    
    return render_template('usuario/cancelar_agendamento.html', 
                         agendamento=agendamento, 
                         form=form)

# NOVAS ROTAS PARA GERENCIAMENTO DE PERFIL
@usuario_bp.route('/perfil')
@login_required
def perfil():
    """Página para visualizar o perfil do usuário"""
    # Atualizar data do último acesso
    current_user.atualizar_ultimo_acesso()
    return render_template('usuario/perfil.html')

@usuario_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Página para editar o perfil do usuário"""
    form = EditarPerfilForm(obj=current_user)
    
    if form.validate_on_submit():
        try:
            # Atualizar campos básicos
            current_user.nome = form.nome.data
            current_user.email = form.email.data
            current_user.empresa = form.empresa.data
            
            # Dados pessoais
            current_user.telefone = form.telefone.data
            current_user.nuit = form.nuit.data
            current_user.genero = form.genero.data
            current_user.data_nascimento = form.data_nascimento.data
            
            # Dados profissionais
            current_user.cargo = form.cargo.data
            current_user.departamento = form.departamento.data
            current_user.tipo_empresa = form.tipo_empresa.data
            current_user.nuit_empresa = form.nuit_empresa.data
            
            # Dados geográficos
            current_user.provincia = form.provincia.data
            current_user.cidade = form.cidade.data
            current_user.bairro = form.bairro.data
            current_user.endereco_completo = form.endereco_completo.data
            
            # Contatos adicionais
            current_user.telefone_alternativo = form.telefone_alternativo.data
            current_user.whatsapp = form.whatsapp.data
            
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('usuario.perfil'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
    
    return render_template('usuario/editar_perfil.html', form=form)

@usuario_bp.route('/perfil/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Página para alterar a senha do usuário"""
    form = AlterarSenhaForm()
    
    if form.validate_on_submit():
        try:
            # Verificar senha atual
            if not current_user.check_password(form.senha_atual.data):
                flash('Senha atual incorreta!', 'danger')
                return render_template('usuario/alterar_senha.html', form=form)
            
            # Atualizar senha
            current_user.set_password(form.nova_senha.data)
            db.session.commit()
            
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('usuario.perfil'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao alterar senha: {str(e)}', 'danger')
    
    return render_template('usuario/alterar_senha.html', form=form)