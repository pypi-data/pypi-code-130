from typing import Any, Awaitable, Callable


class Order:
    def __init__(
        self,
        on: Callable[[], bool],
        action: Callable[[], Awaitable[None]],
    ) -> None:
        self._on = on
        self._action = action
        self._aborted = False

    async def resolve(self) -> bool:
        """
        Try to resolve the order:
        Either the order is aborted or
        check if the conditions are met, if so
        execute the order's action.

        Return if the order was resolved
        """
        if self._aborted:
            return True
        if self._on():
            await self._action()
            return True
        return False

    def abort(self) -> None:
        """
        Abort the order, it won't be executed
        """
        self._aborted = True


class OrderMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._orders: list[Order] = []

    def place_order(self, order: Order) -> None:
        """
        Place an order
        """
        self._orders.append(order)

    async def _resolve_orders(self) -> None:
        """
        Try to resolve orders
        """
        to_remove = []
        for order in self._orders:
            if await order.resolve():
                to_remove.append(order)

        for order in to_remove:
            self._orders.remove(order)
