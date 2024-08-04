from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """Handle the truncation of all tables in the database."""
    help = 'Truncate all tables in the database'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute('''
                DO
                $func$
                BEGIN
                    EXECUTE (
                        SELECT string_agg('TRUNCATE TABLE ' # noqa
                        || tablename || ' CASCADE;', ' ')
                        FROM pg_tables
                        WHERE schemaname = 'public'
                    );
                END
                $func$;
            ''')
        self.stdout.write(self.style.SUCCESS(
            'Successfully truncated all tables')
        )
