import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import PaymentManager
from ob_dj_store.core.stores.models import Order

logger = logging.getLogger(__name__)


class Payment(models.Model):
    """Payment captures the order payment either COD or via a Gateway"""

    class PaymentStatus(models.TextChoices):
        INIT = "INIT"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"
        ERROR = "ERROR"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
    )
    status = models.CharField(
        max_length=100,
        default=PaymentStatus.INIT,
        choices=PaymentStatus.choices,
    )
    method = models.ForeignKey(
        "stores.PaymentMethod",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    orders = models.ManyToManyField("stores.Order", related_name="payments")
    amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )
    currency = models.CharField(_("Currency"), max_length=10)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    payment_post_at = models.DateTimeField(_("Payment Post At"), null=True, blank=True)

    objects = PaymentManager()

    class Meta:
        ordering = ["-created_at"]

    def mark_paid(self):
        self.status = self.PaymentStatus.SUCCESS
        orders = list(self.orders.all())
        for order in orders:
            order.status = Order.OrderStatus.PAID
            order.save()
        self.save()

    def mark_failed(self):
        self.status = self.PaymentStatus.FAILED
        self.save()
