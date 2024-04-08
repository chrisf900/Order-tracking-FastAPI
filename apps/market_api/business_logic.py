from sqlalchemy import func

from apps.market_api.exceptions import InvalidDeliveryStatusTransition


class DeliveryStatus:
    state_name = ""

    def __init__(self, order, db):
        self.order = order
        self.db = db

    def new_state(self, state) -> None:
        self.__class__ = state

    def action(self, state) -> None:
        raise NotImplementedError()

    def __str__(self):
        return self.state_name

    def _set_status(self, new_status) -> None:
        """saves the new status in DB"""

        self.order.delivery_status = new_status.state_name
        self.order.updated_at = func.now()
        self.db.commit()
        self.db.refresh(self.order)


class PreparingForDelivery(DeliveryStatus):
    state_name = "PREPARING_FOR_DELIVERY"

    def action(self, state):
        if state.state_name == "IN_PROGRESS":
            self._set_status(new_status=state)
            self.new_state(state)

        if state.state_name == "CANCELLED":
            self._set_status(new_status=state)
            self.new_state(state)


class InProgress(DeliveryStatus):
    state_name = "IN_PROGRESS"

    def action(self, state):
        if state.state_name == "DELIVERED":
            self._set_status(new_status=state)
            self.new_state(state)


class Delivered(DeliveryStatus):
    state_name = "DELIVERED"

    def action(self, state):
        self._set_status(new_status=state)


class Cancelled(DeliveryStatus):
    state_name = "CANCELLED"

    def action(self, state):
        self._set_status(new_status=state)


class DeliveryStateMachine:
    def __init__(self, state, order, db):
        self.state = state(order, db)

    def change(self, state) -> None:
        self.state.action(state)


def get_state_class(state: str):
    if state == "PREPARING_FOR_DELIVERY":
        return PreparingForDelivery
    elif state == "IN_PROGRESS":
        return InProgress
    elif state == "DELIVERED":
        return Delivered
    elif state == "CANCELLED":
        return Cancelled

    else:
        raise InvalidDeliveryStatusTransition("{} status not valid".format(state))
