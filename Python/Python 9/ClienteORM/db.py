"""
Objetos do sqlalchemy core para a realização da conexão e operação do Banco de Dados
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# check_same_thread=False permite acesso ao database por mais de uma thread
DB_CONNECTION = 'sqlite:///data\db.data?check_same_thread=False'
engine = create_engine(DB_CONNECTION, echo=False)
Base = declarative_base() # Refere-se ao database do banco
Session = sessionmaker(bind=engine)
