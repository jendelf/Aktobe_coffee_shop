"""Add crm_id to User (SQLite safe)"""

from alembic import op
import sqlalchemy as sa

# --- Идентификаторы миграции ---
revision = '2adf941b7d05'          # твой уникальный ID миграции
down_revision = 'fa7fee43d094'     # предыдущая миграция (можно посмотреть в истории)
branch_labels = None
depends_on = None
# -------------------------------

def upgrade():
    # 1. Создаем временную таблицу с нужной структурой
    op.create_table(
        'users_new',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('crm_id', sa.String(50), unique=True, nullable=True, index=True),
        sa.Column('tg_name', sa.String, unique=True, nullable=True),
        sa.Column('chat_id', sa.BigInteger, unique=True, nullable=True, index=True),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 2. Копируем данные из старой таблицы
    op.execute("""
        INSERT INTO users_new (id, tg_name, chat_id, name, phone, created_at)
        SELECT id, tg_name, chat_id, name, phone, created_at FROM users
    """)

    # 3. Удаляем старую таблицу
    op.drop_table('users')

    # 4. Переименовываем новую таблицу
    op.rename_table('users_new', 'users')


def downgrade():
    # Создаем старую структуру для отката
    op.create_table(
        'users_old',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('tg_name', sa.String, unique=True, nullable=True),
        sa.Column('chat_id', sa.Integer, unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Копируем данные обратно
    op.execute("""
        INSERT INTO users_old (id, tg_name, chat_id, name, phone, created_at)
        SELECT id, tg_name, chat_id, name, phone, created_at FROM users
    """)

    # Удаляем текущую таблицу и переименовываем старую
    op.drop_table('users')
    op.rename_table('users_old', 'users')
