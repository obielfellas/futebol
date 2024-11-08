import random
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import os

engine = create_engine(f'sqlite:///futebolpy.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Time(Base):
    __tablename__ = 'times'

    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)
    dinheiro = Column(Float)

    estadio_id = Column(Integer, ForeignKey('estadios.id'))
    estadio = relationship('Estadio', back_populates='time_mandante')

    def __repr__(self):
        return f'<Time(nome={self.nome}, dinheiro={self.dinheiro:.2f})>'

class Estadio(Base):
    __tablename__ = 'estadios'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    capacidade = Column(Integer)
    time_mandante = relationship('Time', back_populates='estadio', uselist=False)

    def __repr__(self):
        return f'<Estadio(nome={self.nome}, capacidade={self.capacidade})>'

class Jogador(Base):
    __tablename__ = 'jogadores'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    numero_camisa = Column(Integer)
    posicao = Column(String)
    preco = Column(Float)
    time_id = Column(Integer, ForeignKey('times.id'))
    time = relationship('Time', backref='jogadores')

    def __repr__(self):
        return f'<Jogador(nome={self.nome}, número={self.numero_camisa}, posição={self.posicao}, preço={self.preco:.2f}, time={self.time.nome})>'

Base.metadata.create_all(engine)

def adicionar_time(nome, dinheiro):
    time = session.query(Time).filter_by(nome=nome).first()
    if not time:
        time = Time(nome=nome, dinheiro=dinheiro)
        session.add(time)
        session.commit()

def adicionar_estadio(nome, capacidade, time_mandante_nome):
    time_mandante = session.query(Time).filter_by(nome=time_mandante_nome).first()
    if not time_mandante:
        print(f'Time mandante "{time_mandante_nome}" não encontrado.')
        return

    estadio = Estadio(nome=nome, capacidade=capacidade, time_mandante=time_mandante)
    session.add(estadio)
    time_mandante.estadio = estadio
    session.commit()

def adicionar_jogador(nome, numero_camisa, posicao, preco, time_nome):
    time = session.query(Time).filter_by(nome=time_nome).first()
    if not time:
        print(f'Time "{time_nome}" não encontrado.')
        return

    jogador = Jogador(nome=nome, numero_camisa=numero_camisa, posicao=posicao, preco=preco, time=time)
    session.add(jogador)
    session.commit()

def visualizar_informacoes_time(time_nome):
    time = session.query(Time).filter_by(nome=time_nome).first()
    if not time:
        print(f'Time "{time_nome}" não encontrado.')
        return

    estadio = time.estadio
    print(f'Informações do Time: {time.nome} (Orçamento: {time.dinheiro:.2f})')
    if estadio:
        print(f'Estádio: {estadio.nome}, Capacidade: {estadio.capacidade}')
    else:
        print('Este time não possui estádio registrado.')
    
    print('Jogadores:')
    for jogador in time.jogadores:
        print(jogador)

def contratar_jogador(jogador_nome, novo_time_nome):
    jogador = session.query(Jogador).filter_by(nome=jogador_nome).first()
    novo_time = session.query(Time).filter_by(nome=novo_time_nome).first()
    
    if not jogador:
        print(f'Jogador "{jogador_nome}" não encontrado.')
        return
    if not novo_time:
        print(f'Time "{novo_time_nome}" não encontrado.')
        return

    print(f'O preço do jogador {jogador.nome} é {jogador.preco:.2f}.')
    if novo_time.dinheiro < jogador.preco:
        print(f'O {novo_time.nome} não tem dinheiro suficiente para contratar {jogador.nome}.')
        return

    confirmar = input(f'Deseja contratar o jogador {jogador.nome} por {jogador.preco:.2f}? ')
    if confirmar.lower() == 'sim':
        novo_time.dinheiro -= jogador.preco
        jogador.time.dinheiro += jogador.preco
        jogador.time = novo_time
        session.commit()
        print(f'Jogador {jogador.nome} foi contratado pelo {novo_time.nome}. Orçamento restante: {novo_time.dinheiro:.2f}')
    else:
        print('Contratação cancelada.')

def excluir_jogador(jogador_nome):
    jogador = session.query(Jogador).filter_by(nome=jogador_nome).first()
    if not jogador:
        print(f'Jogador "{jogador_nome}" não encontrado.')
        return

    confirmar = input(f'Deseja realmente excluir o jogador {jogador.nome}? ')
    if confirmar.lower() == 'sim':
        time_nome = jogador.time.nome
        session.delete(jogador)
        session.commit()
        print(f'Jogador {jogador.nome} foi excluído do time {time_nome}.')
    else:
        print('Exclusão cancelada.')

def alterar_preco_jogador(jogador_nome, novo_preco):
    jogador = session.query(Jogador).filter_by(nome=jogador_nome).first()
    if not jogador:
        print(f'Jogador "{jogador_nome}" não encontrado.')
        return

    jogador.preco = novo_preco
    session.commit()
    print(f'O novo preço do jogador {jogador.nome} é {jogador.preco:.2f}.')

def simular_jogo(time1_nome, time2_nome):
    time1 = session.query(Time).filter_by(nome=time1_nome).first()
    time2 = session.query(Time).filter_by(nome=time2_nome).first()

    if not time1 or not time2:
        print('Um ou ambos os times não foram encontrados.')
        return

    if time1.estadio:
        print(f'Estádio: {time1.estadio.nome} (Capacidade: {time1.estadio.capacidade})')
    else:
        print(f'O time {time1.nome} não tem estádio registrado.')
        return

    print(f'{time1.nome} x {time2.nome}')

    placar_time1 = random.randint(0, 5)
    placar_time2 = random.randint(0, 5)

    print(f'Placar final: {time1.nome} {placar_time1} x {placar_time2} {time2.nome}')

def main():
    while True:
        print('')
        print('1. Adicionar Time')
        print('2. Adicionar Estádio')
        print('3. Adicionar Jogador')
        print('4. Visualizar Informações do Time')
        print('5. Contratar Jogador')
        print('6. Excluir Jogador')
        print('7. Alterar Preço do Jogador')
        print('8. Simular Jogo')
        print('9. Sair')

        opcao = input('Opção: ')
        if opcao == '1':
            nome = input('Nome do Time: ')
            dinheiro = float(input('Dinheiro do Time: '))
            adicionar_time(nome, dinheiro)
        elif opcao == '2':
            nome = input('Nome do Estádio: ')
            capacidade = int(input('Capacidade do Estádio: '))
            time_mandante_nome = input('Nome do Time Mandante: ')
            adicionar_estadio(nome, capacidade, time_mandante_nome)
        elif opcao == '3':
            nome = input('Nome do Jogador: ')
            numero_camisa = int(input('Número da Camisa: '))
            posicao = input('Posição do Jogador: ')
            preco = float(input('Preço do Jogador: '))
            time_nome = input('Nome do Time: ')
            adicionar_jogador(nome, numero_camisa, posicao, preco, time_nome)
        elif opcao == '4':
            time_nome = input('Nome do Time: ')
            visualizar_informacoes_time(time_nome)
        elif opcao == '5':
            jogador_nome = input('Nome do Jogador: ')
            novo_time_nome = input('Nome do Novo Time: ')
            contratar_jogador(jogador_nome, novo_time_nome)
        elif opcao == '6':
            jogador_nome = input('Nome do Jogador: ')
            excluir_jogador(jogador_nome)
        elif opcao == '7':
            jogador_nome = input('Nome do Jogador: ')
            novo_preco = float(input('Novo Preço: '))
            alterar_preco_jogador(jogador_nome, novo_preco)
        elif opcao == '8':
            time1_nome = input('Nome do Time 1: ')
            time2_nome = input('Nome do Time 2: ')
            simular_jogo(time1_nome, time2_nome)
        elif opcao == '9':
            print('Obrigado pela atenção!')
            break
        else:
            print('Opção inválida. Tente novamente.')

if __name__ == '__main__':
    main()
