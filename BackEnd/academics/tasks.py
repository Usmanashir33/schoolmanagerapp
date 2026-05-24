import logging
import  time 
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from core.websocketutils import signal_sender

from .utils import ClassRoomServices

from .models import (
    ClassRoom,
    PromotionLog
)

from school.models import Session
from .serializers import PromotionLogSerializer


logger = logging.getLogger(__name__)


def send_promotion_update(promotion_log):
    """Send websocket update to school room"""
    try:
        time.sleep(1)  # simulate delay for better frontend experience
        room_name = f"school-{promotion_log.school.id}"
        data = {
            "type": "school_feeder2",
            "promotion_log": PromotionLogSerializer(
                promotion_log
            ).data
        }
        signal_sender(room_name, data)
    except Exception as e:
        logger.error(
            f"Failed to send promotion websocket update: {str(e)}"
        )


@shared_task(bind=True, max_retries=3)
def promote_students_task(self, mappings, session_id, log_id):
    promotion_log = None

    try:

        # fetch promotion log
        promotion_log = PromotionLog.objects.select_related(
            "school"
        ).filter(id=log_id).first()

        if not promotion_log:
            return {
                "success": False,
                "error": "Promotion log not found"
            }

        # fetch session once
        session = Session.objects.filter(
            id=session_id,
            school__id=promotion_log.school.id
        ).first()

        if not session:
            promotion_log.status = "failed"
            promotion_log.completed_at = timezone.now()
            promotion_log.save(
                update_fields=["status", "completed_at"]
            )

            return {
                "success": False,
                "error": "Session not found"
            }

        # update processing state
        promotion_log.started_at = timezone.now()
        promotion_log.status = "processing"
        promotion_log.save(
            update_fields=["started_at", "status"]
        )

        # fetch all classrooms once
        class_ids = []

        for item in mappings:

            from_id = item.get("fromClassId")
            to_id = item.get("toClassId")

            if from_id:
                class_ids.append(from_id)

            if to_id:
                class_ids.append(to_id)

        classrooms = {
            classroom.id: classroom
            for classroom in ClassRoom.objects.filter(
                id__in=class_ids
            )
        }

        batch_count = 0
        promoted_count = 0

        for item in mappings:

            old_class_id = item.get("fromClassId")
            new_class_id = item.get("toClassId")

            # skip same class promotions
            if old_class_id == new_class_id:
                continue

            old_class = classrooms.get(old_class_id)
            new_class = classrooms.get(new_class_id)

            # validate classrooms
            if not old_class or not new_class:
                logger.warning(
                    f"Invalid classroom mapping: "
                    f"{old_class_id} -> {new_class_id}"
                )
                continue

            # atomic batch processing
            with transaction.atomic():

                promoted = ClassRoomServices.promote_students(
                    old_class,
                    new_class,
                    session,
                    promotion_log
                )

            if promoted:
                promoted_count += promoted

            batch_count += 1

            # update progress every batch
            promotion_log.processed_batches = batch_count
            promotion_log.status = "processing"
            promotion_log.save(
                update_fields=[
                    "processed_batches",
                    "status"
                ]
            )

            # live websocket update
            send_promotion_update(promotion_log)

        # finalize
        promotion_log.completed_at = timezone.now()
        promotion_log.status = "completed"

        promotion_log.save(
            update_fields=[
                "completed_at",
                "status"
            ]
        )

        # final websocket update
        send_promotion_update(promotion_log)

        return {
            "success": True,
            "promoted_count": promoted_count,
            "batch_count": batch_count
        }

    except Exception as exc:

        logger.error(
            f"Promotion task failed: {str(exc)}"
        )

        if promotion_log:

            promotion_log.status = "failed"
            promotion_log.completed_at = timezone.now()

            promotion_log.save(
                update_fields=[
                    "status",
                    "completed_at"
                ]
            )

            send_promotion_update(promotion_log)

        raise self.retry(
            exc=exc,
            countdown=10
        )