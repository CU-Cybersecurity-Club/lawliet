# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import uuid
from django.db import models
from django.utils import timezone

# from labs.models import LabEnvironment
# from user.models import User


def gen_connection_name():
    # 160 bits of randomness
    return f"lawliet-env-{uuid.uuid4()}"


class GuacamoleConnection(models.Model):
    connection_id = models.AutoField(primary_key=True)
    connection_name = models.CharField(max_length=128, default=gen_connection_name)
    parent = models.ForeignKey(
        "GuacamoleConnectionGroup", models.CASCADE, blank=True, null=True
    )
    protocol = models.CharField(max_length=32)
    proxy_port = models.IntegerField(blank=True, null=True)
    proxy_hostname = models.CharField(max_length=512, blank=True, null=True)
    proxy_encryption_method = models.CharField(max_length=4, blank=True, null=True)
    max_connections = models.IntegerField(blank=True, null=True)
    max_connections_per_user = models.IntegerField(blank=True, null=True)
    connection_weight = models.IntegerField(blank=True, null=True)
    failover_only = models.IntegerField(default=0)

    # Additional custom fields, provided outside of Guacamole
    lab = models.ForeignKey("labs.LabEnvironment", on_delete=models.CASCADE,)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE,)

    class Meta:
        managed = True
        db_table = "guacamole_connection"
        unique_together = (("connection_name", "parent"),)


class GuacamoleConnectionAttribute(models.Model):
    connection = models.ForeignKey(GuacamoleConnection, models.CASCADE)
    attribute_name = models.CharField(max_length=128)
    attribute_value = models.CharField(max_length=4096)

    class Meta:
        managed = True
        db_table = "guacamole_connection_attribute"
        unique_together = (("connection", "attribute_name"),)


class GuacamoleConnectionGroup(models.Model):
    connection_group_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey("self", models.CASCADE, blank=True, null=True)
    connection_group_name = models.CharField(max_length=128)
    type = models.CharField(max_length=14)
    max_connections = models.IntegerField(blank=True, null=True)
    max_connections_per_user = models.IntegerField(blank=True, null=True)
    enable_session_affinity = models.IntegerField()

    class Meta:
        managed = True
        db_table = "guacamole_connection_group"
        unique_together = (("connection_group_name", "parent"),)


class GuacamoleConnectionGroupAttribute(models.Model):
    connection_group = models.ForeignKey(GuacamoleConnectionGroup, models.CASCADE)
    attribute_name = models.CharField(max_length=128)
    attribute_value = models.CharField(max_length=4096)

    class Meta:
        managed = True
        db_table = "guacamole_connection_group_attribute"
        unique_together = (("connection_group", "attribute_name"),)


class GuacamoleConnectionGroupPermission(models.Model):
    entity = models.OneToOneField("GuacamoleEntity", models.CASCADE, primary_key=True)
    connection_group = models.ForeignKey(GuacamoleConnectionGroup, models.CASCADE)
    permission = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = "guacamole_connection_group_permission"
        unique_together = (("entity", "connection_group", "permission"),)


class GuacamoleConnectionHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("GuacamoleUser", models.CASCADE, blank=True, null=True)
    username = models.CharField(max_length=128)
    remote_host = models.CharField(max_length=256, blank=True, null=True)
    connection = models.ForeignKey(
        GuacamoleConnection, models.CASCADE, blank=True, null=True
    )
    connection_name = models.CharField(max_length=128)
    sharing_profile = models.ForeignKey(
        "GuacamoleSharingProfile", models.CASCADE, blank=True, null=True
    )
    sharing_profile_name = models.CharField(max_length=128, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "guacamole_connection_history"


class GuacamoleConnectionParameter(models.Model):
    connection = models.ForeignKey("GuacamoleConnection", on_delete=models.CASCADE)
    parameter_name = models.CharField(max_length=128)
    parameter_value = models.CharField(max_length=4096)

    class Meta:
        managed = True
        db_table = "guacamole_connection_parameter"
        unique_together = (("connection", "parameter_name"),)


class GuacamoleConnectionPermission(models.Model):
    entity = models.ForeignKey("GuacamoleEntity", models.CASCADE)
    connection = models.ForeignKey(GuacamoleConnection, models.CASCADE)
    permission = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = "guacamole_connection_permission"
        unique_together = (("entity", "connection", "permission"),)


class GuacamoleEntity(models.Model):
    entity_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = "guacamole_entity"
        unique_together = (("type", "name"),)


class GuacamoleSharingProfile(models.Model):
    sharing_profile_id = models.AutoField(primary_key=True)
    sharing_profile_name = models.CharField(max_length=128)
    primary_connection = models.ForeignKey(GuacamoleConnection, models.CASCADE)

    class Meta:
        managed = True
        db_table = "guacamole_sharing_profile"
        unique_together = (("sharing_profile_name", "primary_connection"),)


class GuacamoleSharingProfileAttribute(models.Model):
    sharing_profile = models.OneToOneField(
        GuacamoleSharingProfile, models.CASCADE, primary_key=True
    )
    attribute_name = models.CharField(max_length=128)
    attribute_value = models.CharField(max_length=4096)

    class Meta:
        managed = True
        db_table = "guacamole_sharing_profile_attribute"
        unique_together = (("sharing_profile", "attribute_name"),)


class GuacamoleSharingProfileParameter(models.Model):
    sharing_profile = models.OneToOneField(
        GuacamoleSharingProfile, models.CASCADE, primary_key=True
    )
    parameter_name = models.CharField(max_length=128)
    parameter_value = models.CharField(max_length=4096)

    class Meta:
        managed = True
        db_table = "guacamole_sharing_profile_parameter"
        unique_together = (("sharing_profile", "parameter_name"),)


class GuacamoleSharingProfilePermission(models.Model):
    entity = models.OneToOneField(GuacamoleEntity, models.CASCADE, primary_key=True)
    sharing_profile = models.ForeignKey(GuacamoleSharingProfile, models.CASCADE)
    permission = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = "guacamole_sharing_profile_permission"
        unique_together = (("entity", "sharing_profile", "permission"),)


class GuacamoleSystemPermission(models.Model):
    entity_id = models.IntegerField()
    permission = models.CharField(max_length=23)

    class Meta:
        managed = True
        db_table = "guacamole_system_permission"
        unique_together = (("entity_id", "permission"),)


class GuacamoleUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    entity = models.OneToOneField(GuacamoleEntity, models.CASCADE)
    password_hash = models.BinaryField(max_length=32)
    password_salt = models.BinaryField(max_length=32, blank=True, null=True)
    password_date = models.DateTimeField(default=timezone.now)
    disabled = models.IntegerField(default=0)
    expired = models.IntegerField(default=0)
    access_window_start = models.TimeField(blank=True, null=True)
    access_window_end = models.TimeField(blank=True, null=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    timezone = models.CharField(max_length=64, blank=True, null=True)
    full_name = models.CharField(max_length=256, blank=True, null=True)
    email_address = models.CharField(max_length=256, blank=True, null=True)
    organization = models.CharField(max_length=256, blank=True, null=True)
    organizational_role = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "guacamole_user"


class GuacamoleUserAttribute(models.Model):
    user = models.OneToOneField(GuacamoleUser, models.CASCADE, primary_key=True)
    attribute_name = models.CharField(max_length=128)
    attribute_value = models.CharField(max_length=4096)

    class Meta:
        managed = True
        db_table = "guacamole_user_attribute"
        unique_together = (("user", "attribute_name"),)


class GuacamoleUserGroup(models.Model):
    user_group_id = models.AutoField(primary_key=True)
    entity = models.OneToOneField(GuacamoleEntity, models.CASCADE)
    disabled = models.IntegerField()

    class Meta:
        managed = True
        db_table = "guacamole_user_group"


class GuacamoleUserGroupAttribute(models.Model):
    user_group = models.OneToOneField(
        GuacamoleUserGroup, models.CASCADE, primary_key=True
    )
    attribute_name = models.CharField(max_length=128)
    attribute_value = models.CharField(max_length=4096)

    class Meta:
        managed = True
        db_table = "guacamole_user_group_attribute"
        unique_together = (("user_group", "attribute_name"),)


class GuacamoleUserGroupMember(models.Model):
    user_group = models.OneToOneField(
        GuacamoleUserGroup, models.CASCADE, primary_key=True
    )
    member_entity = models.ForeignKey(GuacamoleEntity, models.CASCADE)

    class Meta:
        managed = True
        db_table = "guacamole_user_group_member"
        unique_together = (("user_group", "member_entity"),)


class GuacamoleUserGroupPermission(models.Model):
    entity = models.OneToOneField(GuacamoleEntity, models.CASCADE, primary_key=True)
    affected_user_group = models.ForeignKey(GuacamoleUserGroup, models.CASCADE)
    permission = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = "guacamole_user_group_permission"
        unique_together = (("entity", "affected_user_group", "permission"),)


class GuacamoleUserHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(GuacamoleUser, models.CASCADE, blank=True, null=True)
    username = models.CharField(max_length=128)
    remote_host = models.CharField(max_length=256, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "guacamole_user_history"


class GuacamoleUserPasswordHistory(models.Model):
    password_history_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(GuacamoleUser, models.CASCADE)
    password_hash = models.CharField(max_length=32)
    password_salt = models.CharField(max_length=32, blank=True, null=True)
    password_date = models.DateTimeField()

    class Meta:
        managed = True
        db_table = "guacamole_user_password_history"


class GuacamoleUserPermission(models.Model):
    entity_id = models.IntegerField()
    affected_user_id = models.IntegerField()
    permission = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = "guacamole_user_permission"
        unique_together = (("entity_id", "affected_user_id", "permission"),)
