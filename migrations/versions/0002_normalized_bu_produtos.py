"""Normaliza BUs e produtos em tabelas N:N.

Revision ID: 0002_normalized_bu_produtos
Revises: 0001_initial_schema
Create Date: 2026-11-06

Compatível com SQLite (desenvolvimento) e PostgreSQL (produção/Render).
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_normalized_bu_produtos'
down_revision = '0001_initial_schema'
branch_labels = None
depends_on = None


def _extrair_nomes(csv):
    """Quebra uma string CSV em nomes únicos, preservando a ordem."""
    if not csv:
        return []
    nomes = []
    for pedaco in str(csv).split(','):
        pedaco = pedaco.strip()
        if pedaco and pedaco not in nomes:
            nomes.append(pedaco)
    return nomes


def _id_ou_criar(conn, tabela, nome):
    """Busca o id do registro pelo nome; insere se não existir.

    `INSERT ... ON CONFLICT (nome) DO NOTHING` é válido tanto em
    PostgreSQL quanto em SQLite >= 3.24. O id é recuperado por SELECT
    (não depende de lastrowid, confiável apenas no SQLite).
    """
    conn.execute(
        sa.text(f'INSERT INTO {tabela} (nome) VALUES (:nome)'      # noqa: S608
                ' ON CONFLICT (nome) DO NOTHING'),
        {'nome': nome},
    )
    linha = conn.execute(
        sa.text(f'SELECT id FROM {tabela} WHERE nome = :nome'),    # noqa: S608
        {'nome': nome},
    ).first()
    if linha is None:
        raise RuntimeError(f'Falha ao resolver id de {tabela}<{nome}>')
    return linha[0]


def _sql_concat(conn):
    """GROUP_CONCAT (SQLite) ou string_agg (Postgres), conforme o dialeto."""
    if conn.dialect.name == 'sqlite':
        return "GROUP_CONCAT({col}, ', ')"
    return "string_agg({col}, ', ')"



def upgrade():
    # 1. Cria as tabelas normalizadas
    op.create_table(
        'business_unit',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nome', sa.String(100), nullable=False, unique=True),
    )
    op.create_table(
        'produto',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nome', sa.String(100), nullable=False, unique=True),
    )
    op.create_table(
        'empresa_bus',
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresa.id'), primary_key=True),
        sa.Column('business_unit_id', sa.Integer(), sa.ForeignKey('business_unit.id'), primary_key=True),
    )
    op.create_table(
        'indicacao_produtos',
        sa.Column('indicacao_id', sa.Integer(), sa.ForeignKey('indicacao.id'), primary_key=True),
        sa.Column('produto_id', sa.Integer(), sa.ForeignKey('produto.id'), primary_key=True),
    )

    # 2. Migra os dados dos CSVs para as tabelas N:N
    conn = op.get_bind()

    empresas = conn.execute(sa.text('SELECT id, bus_contratados FROM empresa')).fetchall()
    for empresa_id, contratados in empresas:
        for nome in _extrair_nomes(contratados):
            bu_id = _id_ou_criar(conn, 'business_unit', nome)
            conn.execute(
                sa.text('INSERT INTO empresa_bus (empresa_id, business_unit_id) '
                        'VALUES (:e, :b) ON CONFLICT DO NOTHING'),
                {'e': empresa_id, 'b': bu_id},
            )

    indicacoes = conn.execute(
        sa.text('SELECT id, produtos_escolhidos FROM indicacao')
    ).fetchall()
    for indicacao_id, produtos in indicacoes:
        for nome in _extrair_nomes(produtos):
            produto_id = _id_ou_criar(conn, 'produto', nome)
            conn.execute(
                sa.text('INSERT INTO indicacao_produtos (indicacao_id, produto_id) '
                        'VALUES (:i, :p) ON CONFLICT DO NOTHING'),
                {'i': indicacao_id, 'p': produto_id},
            )

    # 3. Remove colunas CSV
    with op.batch_alter_table('empresa') as batch_op:
        batch_op.drop_column('bus_contratados')
    with op.batch_alter_table('indicacao') as batch_op:
        batch_op.drop_column('produtos_escolhidos')


def downgrade():
    # Recria as colunas CSV com base nas tabelas M:N (dialetos tratados por _sql_concat)
    with op.batch_alter_table('empresa') as batch_op:
        batch_op.add_column(sa.Column('bus_contratados', sa.String(500)))
    with op.batch_alter_table('indicacao') as batch_op:
        batch_op.add_column(sa.Column('produtos_escolhidos', sa.String(500)))

    conn = op.get_bind()
    concat = _sql_concat(conn)

    empresas = conn.execute(sa.text(
        'SELECT empresa_id, ' + concat.format(col='bu.nome') + ' '
        'FROM empresa_bus eb JOIN business_unit bu ON bu.id = eb.business_unit_id '
        'GROUP BY empresa_id'
    )).fetchall()
    for empresa_id, nomes in empresas:
        conn.execute(
            sa.text('UPDATE empresa SET bus_contratados = :n WHERE id = :id'),
            {'n': nomes, 'id': empresa_id},
        )

    indicacoes = conn.execute(sa.text(
        'SELECT indicacao_id, ' + concat.format(col='p.nome') + ' '
        'FROM indicacao_produtos ip JOIN produto p ON p.id = ip.produto_id '
        'GROUP BY indicacao_id'
    )).fetchall()
    for indicacao_id, nomes in indicacoes:
        conn.execute(
            sa.text('UPDATE indicacao SET produtos_escolhidos = :n WHERE id = :id'),
            {'n': nomes, 'id': indicacao_id},
        )

    op.drop_table('indicacao_produtos')
    op.drop_table('empresa_bus')
    op.drop_table('produto')
    op.drop_table('business_unit')
