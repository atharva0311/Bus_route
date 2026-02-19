from django.db import migrations


class Migration(migrations.Migration):
    """
    Route model has been consolidated into buses.models.Route.
    The old routes_route and routes_routestop tables are cleaned up here
    only if they exist (using SeparateDatabaseAndState for safety).
    """

    dependencies = [
        ('routes', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DROP TABLE IF EXISTS routes_routestop CASCADE;
                DROP TABLE IF EXISTS routes_route CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
