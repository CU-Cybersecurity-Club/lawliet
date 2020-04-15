import hashlib
import logging
import secrets

from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext as _
from guacamole.models import (
    GuacamoleEntity,
    GuacamoleSystemPermission,
    GuacamoleUser,
    GuacamoleUserPermission,
)

"""
---------------------------------------------------
UserManager object for the custom User model
---------------------------------------------------
"""


class UserManager(BaseUserManager):

    logger = logging.getLogger("auth")

    def create_user(self, username, email, password, **extra_fields):
        if extra_fields.get("is_superuser", False):
            self.logger.warn(f"Creating new superuser {username!r}")
        else:
            self.logger.info(f"Creating new user {username!r}")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)

        # Validate the User instance's fields, and save the User
        # to the database.
        result = user.full_clean()
        user.save()

        # Add the user to the Guacamole database
        h = hashlib.sha256()
        salt = secrets.token_bytes(32)
        h.update(password.encode("utf-8"))
        h.update(salt.hex().upper().encode("utf-8"))
        hashed_password = h.digest()

        self.logger.info(f"Adding GuacamoleEntity for new user {username!r}")
        entity = GuacamoleEntity.objects.create(name=username, type="USER")

        self.logger.info(f"Adding GuacamoleUser for new user {username!r}")
        guac_user = GuacamoleUser.objects.create(
            entity_id=entity.entity_id,
            password_salt=salt,
            password_hash=hashed_password,
            password_date=timezone.now(),
        )

        user_perms = ["READ", "UPDATE"]
        system_perms = []
        if user.is_superuser:
            user_perms.append("ADMINISTER")
            system_perms.extend(
                [
                    "CREATE_CONNECTION",
                    "CREATE_CONNECTION_GROUP",
                    "CREATE_SHARING_PROFILE",
                    "CREATE_USER",
                    "CREATE_USER_GROUP",
                    "ADMINISTER",
                ]
            )

        self.add_user_permissions(entity, guac_user, user_perms)
        self.add_system_permissions(entity, guac_user, system_perms)

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

    """
    Helper functions
    """

    def add_user_permissions(
        self, entity: GuacamoleEntity, user: GuacamoleUser, permissions
    ):
        """
        Add user-level permissions to a GuacamoleUser
        """

        guac_perms = []

        for perm in permissions:
            self.logger.info(f"Adding user permission {perm} for user {entity.name!r}")
            guac_perms.append(
                GuacamoleUserPermission(
                    entity_id=entity.entity_id,
                    affected_user_id=user.user_id,
                    permission=perm,
                )
            )

        GuacamoleUserPermission.objects.bulk_create(guac_perms)

    def add_system_permissions(
        self, entity: GuacamoleEntity, user: GuacamoleUser, permissions
    ):
        """
        Add system-level permissions to a GuacamoleUser
        """

        guac_perms = []

        for perm in permissions:
            self.logger.warn(
                f"Adding system permission {perm} for user {entity.name!r}"
            )
            guac_perms.append(
                GuacamoleSystemPermission(entity_id=entity.entity_id, permission=perm)
            )

        GuacamoleSystemPermission.objects.bulk_create(guac_perms)
