

from django_elasticsearch_dsl import Document, fields
from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl.registries import registry
from .models import Account
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from account.models import Account


@registry.register_document
class AccountSearch(Document):
    created_by = fields.ObjectField(properties={
        'user_id': fields.TextField(),
        'username': fields.TextField(),
        'phone': fields.TextField(attr="phone_to_str"),
        'role': fields.TextField(),
        'email': fields.TextField(),
        'first_name': fields.TextField(),
        'last_name': fields.TextField(),
    })

    user = fields.ObjectField(properties={
        'user_id': fields.TextField(),
        'username': fields.TextField(),
        'phone': fields.TextField(attr="phone_to_str"),
        'role': fields.TextField(),
        'email': fields.TextField(),
        'first_name': fields.TextField(),
        'last_name': fields.TextField(),
    })

    class Index:
        # Name of the Elasticsearch index
        name = 'accounts'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Account # The model associated with this 
        # queryset_pagination = 50

        # The fields of the model you want to be indexed in Elasticsearch
        # fields = [field.name for field in Application._meta.fields]
        fields = [
            'account_id',
            'customer_id',
            'email',
            'occupation',
            'sub_occupation',
            'net_annual_income',
            'aadhar_no',
            'pan_no',
            'status',
            'year_of_birth',
            'created_at',
        ]


class AccountSearchSerializer(DocumentSerializer):
    class Meta:
        document = AccountSearch
        fields = '__all__'