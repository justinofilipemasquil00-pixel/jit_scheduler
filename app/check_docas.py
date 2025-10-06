from app import create_app, db
from app.models import Doca, Terminal

app = create_app()

with app.app_context():
    # Verificar terminais
    terminais = Terminal.query.all()
    print(f'Terminais: {len(terminais)}')
    for terminal in terminais:
        print(f'Terminal: {terminal.nome}')
    
    # Verificar docas ativas
    docas = Doca.query.filter_by(status='ativa').all()
    print(f'\nDocas ativas: {len(docas)}')
    for doca in docas:
        print(f'Doca {doca.numero} - {doca.terminal.nome} ({doca.tipo_carga})')
    
    # Se não houver docas, criar algumas
    if not docas:
        print("\nNenhuma doca ativa encontrada! Criando docas...")
        
        # Verificar se tem terminal, se não criar
        if not terminais:
            print("Criando terminal...")
            terminal = Terminal(
                nome="Terminal Principal",
                endereco="Av. Principal, 1000",
                telefone="(11) 9999-9999"
            )
            db.session.add(terminal)
            db.session.commit()
            print(f"Terminal criado: {terminal.nome}")
        else:
            terminal = terminais[0]
        
        # Criar docas
        for i in range(1, 4):
            doca = Doca(
                terminal_id=terminal.id,
                numero=str(i).zfill(2),
                tipo_carga='geral',
                status='ativa'
            )
            db.session.add(doca)
        
        db.session.commit()
        print("Docas criadas com sucesso!")
        
        # Verificar novamente
        docas = Doca.query.filter_by(status='ativa').all()
        print(f'\nDocas ativas agora: {len(docas)}')
        for doca in docas:
            print(f'- Doca {doca.numero} - {doca.terminal.nome}')