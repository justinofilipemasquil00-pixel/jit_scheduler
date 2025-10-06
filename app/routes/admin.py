from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Agendamento, Terminal, Doca, User
from app import db
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app.email import send_agendamento_confirmacao, send_agendamento_cancelamento, send_novo_agendamento_admin, send_agendamento_rejeitado  # ← ADICIONE ESTA LINHA

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_agendamentos = Agendamento.query.count()
    agendamentos_hoje = Agendamento.query.filter(
        db.func.date(Agendamento.data_agendamento) == datetime.today().date()
    ).count()
    agendamentos_pendentes = Agendamento.query.filter_by(status='pendente').count()
    total_usuarios = User.query.filter_by(tipo='usuario').count()
    agendamentos_recentes = Agendamento.query.order_by(
        Agendamento.data_criacao.desc()
    ).limit(5).all()
    return render_template('admin/dashboard.html',
                           total_agendamentos=total_agendamentos,
                           agendamentos_hoje=agendamentos_hoje,
                           agendamentos_pendentes=agendamentos_pendentes,
                           total_usuarios=total_usuarios,
                           agendamentos_recentes=agendamentos_recentes)

@admin_bp.route('/agendamentos')
@login_required
def agendamentos():
    status_filter = request.args.get('status', 'todos')
    query = Agendamento.query
    if status_filter != 'todos':
        query = query.filter_by(status=status_filter)
    agendamentos_lista = query.order_by(Agendamento.data_agendamento.asc()).all()
    return render_template('admin/agendamentos.html',
                           agendamentos=agendamentos_lista,
                           status_filter=status_filter)

# CORREÇÃO: Adicionar decorador de rota para aprovar agendamento
@admin_bp.route('/agendamentos/<int:id>/aprovar', methods=['POST'])
@login_required
def aprovar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = 'confirmado'
    db.session.commit()
    
    # ENVIAR EMAIL DE CONFIRMAÇÃO
    try:
        send_agendamento_confirmacao(agendamento)
        flash('Agendamento aprovado e email de confirmação enviado!', 'success')
    except Exception as e:
        flash(f'Agendamento aprovado, mas erro ao enviar email: {str(e)}', 'warning')
    
    return redirect(url_for('admin.agendamentos'))

# CORREÇÃO: Adicionar decorador de rota para rejeitar agendamento
@admin_bp.route('/agendamentos/<int:id>/rejeitar', methods=['POST'])
@login_required
def rejeitar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = 'rejeitado'  # ← CORRIGIDO: mudar para 'rejeitado' em vez de 'cancelado'
    db.session.commit()
    
    # ENVIAR EMAIL DE REJEIÇÃO
    try:
        send_agendamento_rejeitado(agendamento)
        flash('Agendamento rejeitado e email enviado!', 'success')
    except Exception as e:
        flash(f'Agendamento rejeitado, mas erro ao enviar email: {str(e)}', 'warning')
    
    return redirect(url_for('admin.agendamentos'))

# ========== TERMINAIS ==========
@admin_bp.route('/terminais')
@login_required
def terminais():
    terminais_lista = Terminal.query.all()
    return render_template('admin/terminais.html', terminais=terminais_lista)

@admin_bp.route('/terminais/novo', methods=['GET', 'POST'])
@login_required
def novo_terminal():
    if request.method == 'POST':
        nome = request.form.get('nome')
        endereco = request.form.get('endereco')
        telefone = request.form.get('telefone')
        horario_abertura = request.form.get('horario_abertura')
        horario_fechamento = request.form.get('horario_fechamento')
        
        terminal = Terminal(
            nome=nome,
            endereco=endereco,
            telefone=telefone,
            horario_abertura=datetime.strptime(horario_abertura, '%H:%M').time(),
            horario_fechamento=datetime.strptime(horario_fechamento, '%H:%M').time()
        )
        db.session.add(terminal)
        db.session.commit()
        flash('Terminal criado com sucesso!', 'success')
        return redirect(url_for('admin.terminais'))
    
    return render_template('admin/novo_terminal.html')

@admin_bp.route('/terminais/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_terminal(id):
    terminal = Terminal.query.get_or_404(id)
    
    if request.method == 'POST':
        terminal.nome = request.form.get('nome')
        terminal.endereco = request.form.get('endereco')
        terminal.telefone = request.form.get('telefone')
        terminal.horario_abertura = datetime.strptime(request.form.get('horario_abertura'), '%H:%M').time()
        terminal.horario_fechamento = datetime.strptime(request.form.get('horario_fechamento'), '%H:%M').time()
        
        db.session.commit()
        flash('Terminal atualizado com sucesso!', 'success')
        return redirect(url_for('admin.terminais'))
    
    return render_template('admin/editar_terminal.html', terminal=terminal)

@admin_bp.route('/terminais/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_terminal(id):
    terminal = Terminal.query.get_or_404(id)
    db.session.delete(terminal)
    db.session.commit()
    flash('Terminal excluído com sucesso!', 'success')
    return redirect(url_for('admin.terminais'))

# ========== DOCAS ==========
@admin_bp.route('/docas')
@login_required
def docas():
    terminal_id = request.args.get('terminal', type=int)
    status_filter = request.args.get('status')
    
    query = Doca.query.join(Terminal)
    
    if terminal_id:
        query = query.filter(Doca.terminal_id == terminal_id)
    if status_filter:
        query = query.filter(Doca.status == status_filter)
    
    docas_lista = query.all()
    terminais = Terminal.query.all()
    return render_template('admin/docas.html', docas=docas_lista, terminais=terminais)

@admin_bp.route('/docas/novo', methods=['GET', 'POST'])
@login_required
def nova_doca():
    if request.method == 'POST':
        terminal_id = request.form.get('terminal_id')
        numero = request.form.get('numero')
        tipo_carga = request.form.get('tipo_carga')
        status = request.form.get('status')
        
        doca = Doca(
            terminal_id=terminal_id,
            numero=numero,
            tipo_carga=tipo_carga,
            status=status
        )
        db.session.add(doca)
        db.session.commit()
        flash('Doca criada com sucesso!', 'success')
        return redirect(url_for('admin.docas'))
    
    terminais = Terminal.query.all()
    return render_template('admin/nova_doca.html', terminais=terminais)

@admin_bp.route('/docas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_doca(id):
    doca = Doca.query.get_or_404(id)
    
    if request.method == 'POST':
        doca.terminal_id = request.form.get('terminal_id')
        doca.numero = request.form.get('numero')
        doca.tipo_carga = request.form.get('tipo_carga')
        doca.status = request.form.get('status')
        
        db.session.commit()
        flash('Doca atualizada com sucesso!', 'success')
        return redirect(url_for('admin.docas'))
    
    terminais = Terminal.query.all()
    return render_template('admin/editar_doca.html', doca=doca, terminais=terminais)

@admin_bp.route('/docas/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_doca(id):
    doca = Doca.query.get_or_404(id)
    db.session.delete(doca)
    db.session.commit()
    flash('Doca excluída com sucesso!', 'success')
    return redirect(url_for('admin.docas'))

# ========== RELATÓRIOS ==========
@admin_bp.route('/relatorios')
@login_required
def relatorios():
    # Estatísticas básicas para o dashboard de relatórios
    total_agendamentos = Agendamento.query.count()
    
    # Agendamentos deste mês - CORREÇÃO
    primeiro_dia_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    agendamentos_mes = Agendamento.query.filter(
        Agendamento.data_criacao >= primeiro_dia_mes
    ).count()
    
    # Taxa de ocupação simplificada - CORREÇÃO
    total_minutos = db.session.query(func.sum(Agendamento.duracao_estimada)).scalar() or 0
    horas_totais = 30 * 12 * 60  # 30 dias × 12 horas × 60 minutos
    taxa_ocupacao = (total_minutos / horas_totais) * 100 if horas_totais > 0 else 0
    
    # Agendamentos por status
    agendamentos_por_status = db.session.query(
        Agendamento.status,
        func.count(Agendamento.id)
    ).group_by(Agendamento.status).all()
    
    # Agendamentos por terminal - CORREÇÃO
    agendamentos_por_terminal = db.session.query(
        Terminal.nome,
        func.count(Agendamento.id)
    ).select_from(Terminal).join(Doca).join(Agendamento).group_by(Terminal.id, Terminal.nome).all()
    
    return render_template('admin/relatorios.html',
                         total_agendamentos=total_agendamentos,
                         agendamentos_mes=agendamentos_mes,
                         taxa_ocupacao=round(taxa_ocupacao, 2),
                         agendamentos_por_status=agendamentos_por_status,
                         agendamentos_por_terminal=agendamentos_por_terminal)

@admin_bp.route('/relatorios/agendamentos')
@login_required
def relatorio_agendamentos():
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    if data_inicio_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
    else:
        data_inicio = date.today() - timedelta(days=30)
    
    if data_fim_str:
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    else:
        data_fim = date.today()
    
    agendamentos = Agendamento.query.filter(
        Agendamento.data_agendamento.between(data_inicio, data_fim)
    ).order_by(Agendamento.data_agendamento.desc()).all()
    
    return render_template('admin/relatorio_agendamentos.html',
                         agendamentos=agendamentos,
                         data_inicio=data_inicio,
                         data_fim=data_fim)

@admin_bp.route('/relatorios/utilizacao')
@login_required
def relatorio_utilizacao():
    # Relatório de utilização das docas - CORREÇÃO
    utilizacao_docas = db.session.query(
        Doca.numero,
        Terminal.nome,
        func.count(Agendamento.id).label('total_agendamentos'),
        func.sum(Agendamento.duracao_estimada).label('total_minutos')
    ).select_from(Doca).join(Terminal).outerjoin(Agendamento).group_by(Doca.id, Doca.numero, Terminal.nome).all()
    
    return render_template('admin/relatorio_utilizacao.html',
                         utilizacao_docas=utilizacao_docas)