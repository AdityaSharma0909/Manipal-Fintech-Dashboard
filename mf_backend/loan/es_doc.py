from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Loan
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from elasticsearch_dsl import analyzer

@registry.register_document
class LoanSearch(Document):

    account = fields.ObjectField(properties={
        'account_id': fields.TextField(attr='get_customer_account_id'),
        'customer_id': fields.TextField(attr='get_customer_customer_id'),
        'email': fields.KeywordField(attr='get_customer_email'),
        'occupation': fields.TextField(attr='get_customer_occupation'),
        'sub_occupation': fields.TextField(attr='get_customer_sub_occupation'),
        'net_annual_income': fields.IntegerField(attr='get_customer_net_annual_income'),
        'aadhar_no': fields.TextField(attr='get_customer_aadhar_no'),
        'pan_no': fields.TextField(attr='get_customer_pan_no'),
        'first_name': fields.TextField(attr='get_customer_firstname'),
        'last_name': fields.TextField(attr='get_customer_lastname'),
    })

    branch = fields.ObjectField(properties={
        'branch_id': fields.TextField(),
        'branch_name': fields.TextField(),
        'branch_code': fields.TextField(),
    })

    class Index:
        # Name of the Elasticsearch index
        name = 'loans'

        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Loan # The model associated with this 

        # queryset_pagination = 50

        # The fields of the model you want to be indexed in Elasticsearch
        # fields = [field.name for field in Application._meta.fields]
        fields = [
            'loan_id',
            'loan_number',
            'status',
            'term',
            'intrest_rate',
            'penalty',
            'tenure',
            'loan_amount',
            'loan_type',
            'purpose_of_loan',
            'eligible_amount',
            'total_goods_price',
            'total_weight',
            'net_weight',
            'period',
            'gst',
            'gold_rate_per_gram',
            'lending_gold_rate_per_gram',
            'disbursed_amount',
            'disbursed_date',
            'due_date',
            'disbursal_amount',
            'net_disbursed_amount',
            'last_payment_date',
            'current_emi',
            'interest_accrued_till_date',
            'principal_paid',
            'interest_paid',
            'penalty_paid',
            'principal_remaining',
            'interest_remaining',
            'next_due_date',
            'next_due_generation_date',
            'accrual_on_hold',
            'interest_last_accrued_on',
        ]


class LoanSearchSerializer(DocumentSerializer):
    class Meta:
        document = LoanSearch
        fields = '__all__'