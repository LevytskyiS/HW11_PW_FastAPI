"""Init

Revision ID: 856dc275c10a
Revises: 87d340575b72
Create Date: 2023-02-26 11:12:13.495573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '856dc275c10a'
down_revision = '87d340575b72'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=True)
    op.create_index(op.f('ix_contacts_phone'), 'contacts', ['phone'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contacts_phone'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_email'), table_name='contacts')
    # ### end Alembic commands ###