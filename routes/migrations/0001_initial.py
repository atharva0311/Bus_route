from django.db import migrations


class Migration(migrations.Migration):
    """
    Consolidated migration: replaces the old 0001_initial which created
    routes_route and routes_routestop tables. Those models have been
    consolidated into buses.Route. This migration creates no tables.
    """

    initial = True

    dependencies = []

    operations = []
