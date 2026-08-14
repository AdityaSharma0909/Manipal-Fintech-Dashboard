from django_elasticsearch_dsl import Document, fields, Keyword
from django_elasticsearch_dsl.registries import registry
from .models import User
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer


@registry.register_document
class UserSearch(Document):
    phone = fields.TextField(attr="phone_to_str")

    @classmethod
    def generate_id(cls, object_instance):
        return str(object_instance.pk)

    def prepare_user_id(self, instance):
        return str(instance.user_id) if instance.user_id else None

    def prepare_username(self, instance):
        return str(instance.username) if instance.username is not None else None

    class Index:
        # Name of the Elasticsearch index
        name = "users"
        # See Elasticsearch Indices API reference for available settings
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = User  # The model associated with this
        # queryset_pagination = 50

        # The fields of the model you want to be indexed in Elasticsearch
        # fields = [field.name for field in Application._meta.fields]
        fields = [
            "user_id",
            "first_name",
            "last_name",
            # 'account',
            # 'phone',
            "username",
            "role",
            "designation",
            "aadhar_no",
            "pan_no",
            "employee_id",
            "date_of_joining",
            "email",
        ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Configure how the index should be refreshed after an update.
        # See Elasticsearch documentation for supported options:
        # https://www.elastic.co/guide/en/elasticsearch/reference/master/docs-refresh.html
        # This per-Document setting overrides settings.ELASTICSEARCH_DSL_AUTO_REFRESH.
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000


class UserSearchSerializer(DocumentSerializer):
    class Meta:
        document = UserSearch
        fields = "__all__"
