# Generated by Django 3.0.3 on 2020-04-29 20:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("guacamole", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="guacamoleconnection",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="guacamoleusergrouppermission",
            name="affected_user_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="guacamole.GuacamoleUserGroup",
            ),
        ),
        migrations.AddField(
            model_name="guacamoleusergroupmember",
            name="member_entity",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="guacamole.GuacamoleEntity",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleusergroupattribute",
            unique_together={("user_group", "attribute_name")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleuserattribute", unique_together={("user", "attribute_name")},
        ),
        migrations.AddField(
            model_name="guacamolesharingprofilepermission",
            name="sharing_profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="guacamole.GuacamoleSharingProfile",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="guacamolesharingprofileparameter",
            unique_together={("sharing_profile", "parameter_name")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamolesharingprofileattribute",
            unique_together={("sharing_profile", "attribute_name")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamolesharingprofile",
            unique_together={("sharing_profile_name", "primary_connection")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleconnectionpermission",
            unique_together={("entity", "connection", "permission")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleconnectionparameter",
            unique_together={("connection", "parameter_name")},
        ),
        migrations.AddField(
            model_name="guacamoleconnectiongrouppermission",
            name="connection_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="guacamole.GuacamoleConnectionGroup",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleconnectiongroupattribute",
            unique_together={("connection_group", "attribute_name")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleconnectiongroup",
            unique_together={("connection_group_name", "parent")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleconnectionattribute",
            unique_together={("connection", "attribute_name")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleconnection", unique_together={("connection_name", "parent")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleusergrouppermission",
            unique_together={("entity", "affected_user_group", "permission")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleusergroupmember",
            unique_together={("user_group", "member_entity")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamolesharingprofilepermission",
            unique_together={("entity", "sharing_profile", "permission")},
        ),
        migrations.AlterUniqueTogether(
            name="guacamoleconnectiongrouppermission",
            unique_together={("entity", "connection_group", "permission")},
        ),
    ]
