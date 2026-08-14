import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from simple_history.models import HistoricalRecords

from onboarding_v2.constants import ApplicationStage, ApplicationStatus
from onboarding_v2.models import ApplicationV2, ApplicationStatusHistory

logger = logging.getLogger(__name__)


def get_current_user():
    request = getattr(HistoricalRecords.thread, "request", None)
    if request and hasattr(request, "user"):
        user = request.user
        if getattr(user, "is_authenticated", False):
            return user
    return None


@receiver(pre_save, sender=ApplicationV2)
def application_v2_pre_save(sender, instance, **kwargs):
    # Set submitted_at if application stage or status indicates submission
    if (
        instance.stage == ApplicationStage.SUBMITTED
        or instance.status in {
            ApplicationStatus.SENT_FOR_PRE_SCREENING,
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.PUNCHING_PENDING,
            ApplicationStatus.SUBMITTED_TO_UNDERWRITING,
            ApplicationStatus.RH_APPROVAL_PENDING,
        }
    ):
        if not instance.submitted_at:
            instance.submitted_at = timezone.now()

    # Ensure submitted_at is included in update_fields if update_fields was provided
    update_fields = kwargs.get("update_fields")
    if update_fields is not None and instance.submitted_at:
        if isinstance(update_fields, list) and "submitted_at" not in update_fields:
            update_fields.append("submitted_at")
        elif isinstance(update_fields, set) and "submitted_at" not in update_fields:
            update_fields.add("submitted_at")

    if instance.pk:
        try:
            old_instance = ApplicationV2.objects.filter(pk=instance.pk).only("status").first()
            if old_instance and old_instance.status != instance.status:
                instance._status_changed_from = old_instance.status
            else:
                instance._status_changed_from = None
        except Exception as e:
            logger.warning("Error fetching previous status for ApplicationV2: %s", e)
            instance._status_changed_from = None
    else:
        # Brand new application
        instance._is_new_application = True


@receiver(post_save, sender=ApplicationV2)
def application_v2_post_save(sender, instance, created, **kwargs):
    user = getattr(instance, "_status_changed_by", None) or get_current_user()
    if user and not getattr(user, "is_authenticated", False):
        user = None

    try:
        if created:
            ApplicationStatusHistory.objects.create(
                application=instance,
                from_status=None,
                to_status=instance.status,
                changed_by=user,
            )
        elif getattr(instance, "_status_changed_from", None) is not None:
            ApplicationStatusHistory.objects.create(
                application=instance,
                from_status=instance._status_changed_from,
                to_status=instance.status,
                changed_by=user,
            )
            instance._status_changed_from = None
    except Exception as e:
        logger.error("Failed to record ApplicationStatusHistory for %s: %s", instance.application_id, e)

