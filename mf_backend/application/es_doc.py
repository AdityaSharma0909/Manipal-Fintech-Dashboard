

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Application
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from elasticsearch_dsl import analyzer


# html_strip = analyzer(
#     'html_strip',
#     tokenizer="uax_url_email",
#     filter=["email", "lowercase", "unique"],
#     char_filter=["html_strip"]
# )

@registry.register_document
class ApplicationSearch(Document):

    account = fields.ObjectField(properties={
        'account_id': fields.TextField(),
        'customer_id': fields.TextField(),
        'email': fields.KeywordField(),
        'occupation': fields.TextField(),
        'sub_occupation': fields.TextField(),
        'net_annual_income': fields.IntegerField(),
        'aadhar_no': fields.TextField(),
        'pan_no': fields.TextField(),
        'first_name': fields.TextField(attr='get_customer_firstname'),
        'last_name': fields.TextField(attr='get_customer_lastname'),
    })
    
    # account = fields.TextField(attr='account_to_str')


    class Index:
        # Name of the Elasticsearch index
        name = 'applications'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    # class Meta:
    #     model = Application # The model associated with this 

    class Django:
        model = Application # The model associated with this 
        # queryset_pagination = 50

        # The fields of the model you want to be indexed in Elasticsearch
        # fields = [field.name for field in Application._meta.fields]
        fields = [
            'application_id',
            # 'account',
            'status',
            'application_number',
            'purpose_of_loan',
            'loan_amount',
            'contra_loan_amount',
            'application_type',
            'disbursal_amount',
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





class ApplicationSearchSerializer(DocumentSerializer):
    class Meta:
        document = ApplicationSearch
        fields = '__all__'