from .base import Event, Data


class PaymentOrderEventStates:
    CREATED = "created"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    DENIED = "denied"
    APPROVED = "approved"


class PaymentOrderData(Data):
    @property
    def is_completed(self):
        return self.status == PaymentOrderEventStates.COMPLETED

    @property
    def is_cancelled(self):
        return self.status == PaymentOrderEventStates.CANCELLED
    
    @property
    def is_denied(self):
        return self.status == PaymentOrderEventStates.CANCELLED


class PaymentOrderEvent(Event):
    @property
    def data(self):
        return PaymentOrderData(json_data=self.json_data.get("data", {}))

    @property
    def event_type(self):
        return self.json_data.get("event")
