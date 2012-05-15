from django.db import connection
from django.utils.datastructures import DictWrapper
from django.db.models import PositiveSmallIntegerField


class UnsupportedBackend(Exception):
    """
    A unsupported backend was used with this field.
    """
    pass


class ISONumericField(PositiveSmallIntegerField):
    """
    PositiveSmallIntegerField with a max_value of 999.
    """

    def get_internal_type(self):
        return "PositiveSmallIntegerField"

    def db_type(self):
        from django.conf import settings
        if settings.DATABASE_ENGINE in ('postgresql', 'postgresql_psycopg2'):
            format = 'smallint CHECK ("%(column)s" >= 0 and ' + \
                   '"%(column)s" < 1000)'
        elif settings.DATABASE_ENGINE == 'oracle':
            format = 'NUMBER(11) CHECK (%(qn_column)s >= 0 and ' + \
                   '%(qn_column)s < 1000)'
        elif settings.DATABASE_ENGINE == 'sqlite3':
            format = 'smallint unsigned'
        elif settings.DATABASE_ENGINE == 'mysql':
            format = 'smallint UNSIGNED'
        else:
            raise UnsupportedBackend()
        return format % \
               DictWrapper(self.__dict__, connection.ops.quote_name, "qn_")

    def formfield(self, **kwargs):
        """
        Set maximum value in *formfield* to 999.
        """
        defaults = {'min_value': 0, 'max_value': 999}
        defaults.update(kwargs)
        return super(PositiveSmallIntegerField, self).formfield(**defaults)
