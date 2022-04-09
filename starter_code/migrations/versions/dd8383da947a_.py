"""empty message

Revision ID: dd8383da947a
Revises: 207ebaa57e5b
Create Date: 2022-04-05 00:04:39.217807

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dd8383da947a'
down_revision = '207ebaa57e5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('show')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('show',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], name='show_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], name='show_venue_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='show_pkey')
    )
    op.drop_table('Show')
    # ### end Alembic commands ###
