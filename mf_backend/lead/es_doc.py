

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Lead
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from account.models import Account


@registry.register_document
class LeadSearch(Document):
    phone = fields.TextField(attr="phone_to_str")

    # account = fields.ObjectField(properties={
    #     'account_id': fields.TextField(),
    #     'customer_id': fields.TextField(),
    #     'email': fields.TextField(),
    #     'occupation': fields.TextField(),
    #     'sub_occupation': fields.TextField(),
    #     'net_annual_income': fields.IntegerField(),
    #     'aadhar_no': fields.TextField(),
    #     'pan_no': fields.TextField(),
    # })

    class Index:
        # Name of the Elasticsearch index
        name = 'leads'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Lead # The model associated with this 
        # queryset_pagination = 50

        # The fields of the model you want to be indexed in Elasticsearch
        # fields = [field.name for field in Application._meta.fields]
        fields = [
            'lead_id',
            'first_name',
            'last_name',
            'lead_type',
            # 'phone',
            'status',
            
        ]

        # related_model = [Account]

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





class LeadSearchSerializer(DocumentSerializer):
    class Meta:
        document = LeadSearch
        fields = '__all__'