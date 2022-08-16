from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


class Dataset(Enum):
    ADDRESSES_EXTENDED = "addresses_extended"
    EMAILS_EXTENDED = "emails_extended"
    PHONES_EXTENDED = "phones_extended"
    ACTIVITY_INDICATORS = "activity_indicators"


@dataclass
class ReceitaFederalPJData(BaseData):
    """ReceitaFederalPJData Data.

    Contains all data prospect from Receita Federal Data Source.

    Default Properties
    ==================

    * tax_id (str)                      The TaxId prospected.
                                        must be a valid CNPJ, formatted or not.
    * integration_status (str)          The current Integration Status, please check the
                                        `find_current_status` method for more info.
    * status_reason (str)               The human friendly reason for current status
    * prospect_date (datetime)          The prospect datetime.
    * payload (dict)                    Original payload received from prospection.
    * timeit (str)                      Time in seconds for retrieving data.
    * datasource_base_url (str)         Data Source Base Url
    * data_type (str)                   DataSource Object Name

    ReceitaFederalPJData Properties
    ===============================

    * official_name (str)               Company Official Name ("Razão Social").
    * trade_name (str)                  Company Trade Name ("Nome Fantasia").
    * foundation_date (date)            Company Foundation Date.
    * tax_regime (str)                  Tax Regime.
    * tax_status (str)                  Receita Federal Tax current status.
    * legal_nature_code (str)           Company Legal Nature Code.
    * legal_nature_description (str)    Company Legal Nature Description.
    * is_headquarter (bool)             Is Headquarter?
    * main_activity (str)               Company Main Activity Code ("CNAE code").
    * activities (List[str])            List of activities codes ("CNAE codes").

    """

    official_name: Optional[str] = None
    trade_name: Optional[str] = None
    foundation_date: Optional[date] = None
    tax_regime: Optional[str] = None
    tax_status: Optional[str] = None
    legal_nature_code: Optional[str] = None
    legal_nature_description: Optional[str] = None
    is_headquarter: Optional[bool] = None
    main_activity: Optional[str] = None
    activities: Optional[List[str]] = None
    address: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    mail: Optional[str] = None
    phone: Optional[str] = None
    employees_range: Optional[str] = None
    income_range: Optional[str] = None


class ReceitaFederalPJSerializer(BaseSchema):
    official_name = fields.String(allow_none=True)
    trade_name = fields.String(allow_none=True)
    foundation_date = fields.Date(allow_none=True)
    tax_regime = fields.String(allow_none=True)
    tax_status = fields.String(allow_none=True)
    legal_nature_code = fields.String(allow_none=True)
    legal_nature_description = fields.String(allow_none=True)
    is_headquarter = fields.Boolean(allow_none=True)
    activities = fields.List(fields.String, allow_none=True)
    main_activity = fields.String(allow_none=True)
    payload = fields.Dict(allow_none=True)
    address = fields.String(allow_none=True)
    city = fields.String(allow_none=True)
    neighborhood = fields.String(allow_none=True)
    state = fields.String(allow_none=True)
    zip_code = fields.String(allow_none=True)
    mail = fields.String(allow_none=True)
    phone = fields.String(allow_none=True)
    employees_range = fields.String(allow_none=True)
    income_range = fields.String(allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.info(f"Request Data received is: {data}")
        return data

    @post_load
    def make_data(self, data, **kwargs) -> ReceitaFederalPJData:
        logger.info(f"Deserialized Data received is: {data}")
        new_data = ReceitaFederalPJData(**data)
        new_data.datasource_base_url = ReceitaFederalPJ.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class ReceitaFederalPJ(BaseSnatch):
    default_timeout: int = 10
    default_max_days: int = 180
    base_url_key: str = "snatch.datasource_rf_url"
    authorization_token_key: str = "snatch.rf_secret_token"
    serializer_class: Type[Schema] = ReceitaFederalPJSerializer
    extends: List[Dataset] = None

    def _make_payload(self, dataset):
        payload = {"tax_id": self.tax_id}
        if dataset:
            payload["dataset"] = f"basic_data, {dataset}"
        else:
            payload["dataset"] = "basic_data"
        return payload

    def _format_dataset(self, dataset):
        if isinstance(dataset, list):
            dataset = ", ".join([x.value for x in dataset])
        return dataset

    def _post_new_prospect(self, timeout: int) -> BaseData:
        url = "/api/prospects/from_tax_id/"
        self.extends = self._format_dataset(self.extends)
        payload = self._make_payload(dataset=self.extends)
        logger.info(f"Using basic_data, {self.extends} as dataset")
        data = self._request_and_create_data(url=url, timeout=timeout, payload=payload)
        return data
