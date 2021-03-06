from peewee import PrimaryKeyField, TextField, ForeignKeyField, BigIntegerField

from .basemodel import BaseModel
from .performance import Performance


class PCPerformance(BaseModel):
    id = PrimaryKeyField(column_name='pc_performance_id')
    performance = ForeignKeyField(Performance, column_name='performance_id')
    name = TextField(column_name='pc_performance_name')
    description = TextField(column_name='pc_performance_description')
    emoji_id = BigIntegerField(column_name='emoji_id')

    class Meta:
        table_name = 'PCPerformance'


if __name__ == '__main__':
    for row in PCPerformance.select():
        print(row.id, row.name)