from django.db import models


class CreditScoreRange(models.Model):
    id = models.IntegerField(primary_key=True)
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    score_color = models.CharField(max_length=15)
    score_band = models.CharField(max_length=20)

    class Meta:
        db_table = "credit_score_range"
        ordering = ["id"]

    def __str__(self):
        return f"{self.min_score}-{self.max_score} ({self.score_band})"
