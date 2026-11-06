"""Executa as migrações do banco antes do servidor subir.

Rodado pelo Dockerfile no boot do container (antes do gunicorn).
Lida com os três estados possíveis do banco:
- alembic_version presente: somente upgrade (nunca stamp sobre migrações
  pendentes, para não pular migrações de dados)
- sem alembic_version, mas com tabelas: schema criado fora do Alembic
  (db.create_all() legado). Se houver coluna CSV (schema 0001), aplica
  stamp 0001; se já é o schema atual, stamp no head.
- banco vazio: upgrade cria tudo desde 0001
"""

from flask_migrate import stamp, upgrade
from sqlalchemy import inspect

from app import create_app, db

REVISAO_SCHEMA_LEGADO = '0001_initial_schema'


def _executar():
    app = create_app()
    with app.app_context():
        inspetor = inspect(db.engine)
        tabelas = inspetor.get_table_names()

        if 'alembic_version' in tabelas:
            pass  # registro válido: upgrade() segue direto
        elif not tabelas:
            pass  # banco vazio: upgrade() cria tudo
        elif inspetor.has_table('empresa') and 'bus_contratados' in {
            col['name'] for col in inspetor.get_columns('empresa')
        }:
            # Schema legado (CSVs) criado por db.create_all(), sem registro
            app.logger.info('Schema legado sem alembic_version; aplicando stamp %s', REVISAO_SCHEMA_LEGADO)
            stamp(revision=REVISAO_SCHEMA_LEGADO)
        else:
            # Tabelas já no schema atual, mas sem registro (ex.: create_all recente)
            app.logger.info('Banco sem alembic_version e sem schema legado; aplicando stamp no head')
            stamp()

        upgrade()
        app.logger.info('Migrações concluídas.')


if __name__ == '__main__':
    _executar()
