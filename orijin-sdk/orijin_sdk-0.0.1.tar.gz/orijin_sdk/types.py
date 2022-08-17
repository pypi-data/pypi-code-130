### Generic

class endpoints:
    def __init__(self) -> None:
        self.gql             = "/api/gql/query"
        self.file_uploads    = "/api/gql/query"
        self.consumer_login  = "/api/auth/customer/login"
        self.brand_login     = "/api/auth/login"

### GQL

from datetime import datetime

class SkuCategoryInput:
    id: int
    name: str

class SkuContentInput:
    title: str
    content: str

class SkuRetailerInput:
    retailerID: int
    url: str

class UpdateSku:
    name: str
    brand: str
    description: str
    ingredients: str
    weight: int
    weightUnit: str
    currency: str
    price: int
    purchasePoints: int
    loyaltyPoints: int
    categoryOne: list[SkuCategoryInput]
    categoryTwo: list[SkuCategoryInput]
    contents: list[SkuContentInput]
    retailLinks: list[SkuRetailerInput]
    isPointBound: bool
    organizationID: int

class UpdateOrder:
    description: str
    productUnits: int
    skuID: int
    organizationID: int

class CreateContainer:
    quantity: int
    description: str
    organizationID: int

class CreatePallet:
    quantity: int
    description: str
    containerID: int
    organizationID: int

class CreateCarton:
    quantity: int
    description: str
    palletID: int
    organizationID: int

class UpdateProduct:
    skuID: int
    orderID: int
    cartonID: int
    contractID: int
    retailerID: int
    organizationID: int
    description: str
    loyaltyPoints: int
    loyaltyPointsExpire: datetime
    inheritCartonHistory: bool