import logging

from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator
from django.db import connection
from django.utils.translation import gettext as _

"""
---------------------------------------------------
UserManager object for the custom User model
---------------------------------------------------
"""


class UserManager(BaseUserManager):

    logger = logging.getLogger("auth")

    def create_user(self, username, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)

        # Validate the User instance's fields, and save the User
        # to the database.
        result = user.full_clean()
        user.save()

        # Add the user to the Guacamole database
        with connection.cursor() as cur:
            self.logger.info(f"Putting {username} into the Guacamole database")

            query = """
            SET @salt = UNHEX(SHA2(UUID(), 256));

            INSERT INTO guacamole_entity
                (name, type)
            VALUES
                ("%s", "USER");

            INSERT INTO guacamole_user
                (entity_id, password_salt, password_hash, password_date)
            SELECT
                entity_id,
                @salt,
                UNHEX(SHA2(CONCAT("%s", HEX(@salt)), 256)),
                NOW()
            FROM guacamole_entity
            WHERE name = "%s" AND type = "USER";
            """
            self.logger.debug(query)
            cur.execute(query, [username, password, username])

            query = """
            INSERT INTO guacamole_user_permission
                (entity_id, affected_user_id, permission)
            SELECT
                guacamole_entity.entity_id, guacamole_user.user_id, permission
            FROM (
                SELECT
                    "%s" AS username,
                    "%s" AS affected_username,
                    "READ"    AS permission
                UNION SELECT
                    "%s" AS username,
                    "%s" AS affected_username,
                    "UPDATE"  AS permission
            ) permissions
            JOIN
                guacamole_entity
                ON permissions.username = guacamole_entity.name
                AND guacamole_entity.type = "USER"
            JOIN
                guacamole_entity affected
                ON permissions.affected_username = affected.name
                AND guacamole_entity.type = "USER"
            JOIN
                guacamole_user
                ON guacamole_user.entity_id = affected.entity_id;
            """
            self.logger.debug(query)
            cur.execute(query, 4 * [username])

        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser must be created with is_staff=True."))
        elif not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser must be created with is_superuser=True."))
        else:
            return self.create_user(
                username=username, email=email, password=password, **extra_fields
            )
