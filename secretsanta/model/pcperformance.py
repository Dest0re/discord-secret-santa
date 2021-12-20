from peewee import PrimaryKeyField, TextField, ForeignKeyField

from basemodel import BaseModel
from performance import Performance


class PCPerformance(BaseModel):
    id = PrimaryKeyField(column_name='pc_performance_id')
    performance = ForeignKeyField(Performance, column_name='performance_id')
    name = TextField(column_name='pc_performance_name')

    class Meta:
        table_name = 'PCPerformance'


if __name__ == '__main__':
    print(PCPerformance.select().execute())