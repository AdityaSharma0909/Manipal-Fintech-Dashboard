from django.core.management.base import BaseCommand
# from django.contrib.auth.models import User
from users.models import User
from oauth2_provider.models import Application, generate_client_secret, generate_client_id
# pylint: disable=import-error
from utils.envSetup import environment
from utils.constants import ROLES


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Initializing super admin started...")
        superUsers = User.objects.filter(role=ROLES.SUPER_ADMIN.value)
        if superUsers.count() == 0:
            user=User.objects.create_superuser(
                username=environment.DJANGO_SUPERUSER_USERNAME,
                password=environment.DJANGO_SUPERUSER_PASSWORD,
                phone=environment.DJANGO_SUPERUSER_PHONE,
                role=ROLES.SUPER_ADMIN.value,
                is_superuser=True,
                is_staff=True,
            )
            self.create_app(user)
            print("SuperUser created successfully.")
        else:
            print("SuperUser already exists.")

    def create_app(self, user):
        application = Application(
            name="Radian App",
            client_id=generate_client_id(),
            client_secret=generate_client_secret(),
            client_type="confidential",
            authorization_grant_type="password",
            user_id=user.user_id
        )
        application.save()
        print("OAuth Application created successfully.")
        return application