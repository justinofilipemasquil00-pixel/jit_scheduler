from app import create_app, db 
from app.models import User, Terminal, Doca, Agendamento 
from datetime import datetime, time 
 
def populate_database(): 
    app = create_app() 
 
    with app.app_context(): 
        # Limpar tabelas 
        db.drop_all() 
        db.create_all() 
 
        # Criar usuarios 
        admin = User( 
            email='admin@jit.com', 
            nome='Administrador Sistema', 
            empresa='JIT Logistics', 
            tipo='admin' 
        ) 
        admin.set_password('admin123') 
 
        usuario1 = User( 
            email='usuario@jit.com', 
            nome='Joao Silva', 
            empresa='Transportes Silva Ltda', 
            tipo='usuario' 
        ) 
        usuario1.set_password('user123') 
 
        usuario2 = User( 
            email='maria@empresa.com', 
            nome='Maria Santos', 
            empresa='Logistica Santos ME', 
            tipo='usuario' 
        ) 
        usuario2.set_password('user123') 
 
        # Criar terminais 
        terminal1 = Terminal( 
            nome='Terminal Centro', 
            endereco='Rua Principal, 123 - Centro', 
            telefone='(11) 9999-8888', 
            horario_abertura=time(6, 0), 
            horario_fechamento=time(22, 0) 
        ) 
 
        terminal2 = Terminal( 
            nome='Terminal Zona Norte', 
            endereco='Av. Industrial, 456 - Zona Norte', 
            telefone='(11) 7777-6666', 
            horario_abertura=time(7, 0), 
            horario_fechamento=time(19, 0) 
        ) 
 
        # Criar docas 
        doca1 = Doca(terminal=terminal1, numero='D01', tipo_carga='geral') 
        doca2 = Doca(terminal=terminal1, numero='D02', tipo_carga='frigorifica') 
        doca3 = Doca(terminal=terminal1, numero='D03', tipo_carga='perigosa') 
        doca4 = Doca(terminal=terminal2, numero='D01', tipo_carga='geral') 
        doca5 = Doca(terminal=terminal2, numero='D02', tipo_carga='granel') 
 
        # Criar agendamentos 
        agendamento1 = Agendamento( 
            usuario=usuario1, 
            doca=doca1, 
            data_agendamento=datetime(2025, 10, 4, 9, 0), 
            duracao_estimada=90, 
            tipo_operacao='carga', 
            tipo_carga='geral', 
            placa_veiculo='ABC1D23', 
            nome_motorista='Pedro Oliveira', 
            telefone_motorista='(11) 8888-9999', 
            status='confirmado' 
        ) 
 
        agendamento2 = Agendamento( 
            usuario=usuario2, 
            doca=doca2, 
            data_agendamento=datetime(2025, 10, 4, 11, 0), 
            duracao_estimada=60, 
            tipo_operacao='descarga', 
            tipo_carga='frigorifica', 
            placa_veiculo='XYZ9W87', 
            nome_motorista='Carlos Mendes', 
            status='pendente' 
        ) 
 
        # Adicionar tudo ao banco 
        db.session.add_all([admin, usuario1, usuario2, terminal1, terminal2, 
                           doca1, doca2, doca3, doca4, doca5, 
                           agendamento1, agendamento2]) 
        db.session.commit() 
 
        print('Banco de dados populado com sucesso!') 
        print(f'Usuarios criados: {User.query.count()}') 
        print(f'Terminais criados: {Terminal.query.count()}') 
        print(f'Docas criadas: {Doca.query.count()}') 
        print(f'Agendamentos criados: {Agendamento.query.count()}') 
 
if __name__ == '__main__': 
    populate_database() 
