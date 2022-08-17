import sys
import json
import requests
import dataclasses

from .payload import Payload
from .utils import Serializable
from .configurator import Config
from .constants import DEFAULT_URL


@dataclasses.dataclass
class FoodItem(Serializable):

    name: str
    cost: float
    quantity: int

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self) | {"total_cost": self.total_cost}

    @classmethod
    def from_dict(cls, data: dict) -> "FoodItem":
        return FoodItem(
            name=data["name"], cost=data["unitCost"], quantity=data["quantity"]
        )

    @property
    def total_cost(self) -> float:
        return self.cost * self.quantity


@dataclasses.dataclass
class Order(Serializable):

    id: int
    date: str
    customer: str
    items: list[FoodItem] = dataclasses.field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "customer": self.customer,
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Order":

        date = data["createdAt"].split("T")[0]
        items = [
            FoodItem.from_dict(item) for item in data["cartDetails"]["items"]["dishes"]
        ]

        return Order(
            date=date,
            items=items,
            id=data["id"],
            customer=data["creator"]["name"],
        )

    def __len__(self) -> int:
        return len(self.items)


def get_orders(payload: Payload, config: Config, url: str = DEFAULT_URL) -> list[Order]:

    orders: list[Order] = []

    with requests.Session() as session:

        session.headers.update(config.headers)
        session.cookies.update(config.cookies)

        while True:

            response = session.post(url, data=payload.to_json())

            if not response.ok:
                sys.stderr.write(f"error: {response.status_code} {response.reason}")
                continue

            resp_data = response.json()

            if new_orders := resp_data.get("orders"):
                orders.extend([Order.from_dict(order) for order in new_orders])
            else:
                print(resp_data)

            if len(new_orders) < payload.count:
                # No more orders to fetch
                break

            payload.offSet += payload.count

    return orders
