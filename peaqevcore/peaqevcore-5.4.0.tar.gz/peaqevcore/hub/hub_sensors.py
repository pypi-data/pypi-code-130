from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from ..models.hub.hubmember import HubMember
from ..models.hub.currentpeak import CurrentPeak
from ..models.hub.carpowersensor import CarPowerSensor
from ..models.hub.chargerobject import ChargerObject
from ..models.hub.chargerswitch import ChargerSwitch
from ..services.locale.Locale import LocaleData
from ..models.hub.power import Power
from .hub_options import HubOptions

@dataclass
class IHubSensors:
    charger_enabled: HubMember = field(init=False)
    charger_done: HubMember = field(init=False)
    current_peak: CurrentPeak = field(init=False)
    totalhourlyenergy: HubMember = field(init=False)
    carpowersensor: CarPowerSensor = field(init=False)
    locale: LocaleData = field(init=False)
    chargerobject: ChargerObject = field(init=False)
    chargerobject_switch: ChargerSwitch = field(init=False)

    @abstractmethod
    def setup(self):
        pass

    def create_hub_base_data(
            self,
            options: HubOptions,
            state_machine,
            domain: str
    ):
        resultdict = {}

        self.locale = LocaleData(
            options.locale,
            domain
        )
        self.current_peak = CurrentPeak(
            data_type=float,
            initval=0,
            startpeaks=options.startpeaks,
        )
        self.chargerobject = ChargerObject(
            data_type=self.chargertype.charger.native_chargerstates,
            listenerentity=self.chargertype.charger.entities.chargerentity
        )
        resultdict[self.chargerobject.entity] = self.chargerobject.is_initialized

        self.carpowersensor = CarPowerSensor(
            data_type=int,
            listenerentity=self.chargertype.charger.entities.powermeter,
            powermeter_factor=self.chargertype.charger.options.powermeter_factor,
            hubdata=self
        )
        self.chargerobject_switch = ChargerSwitch(
            hass=state_machine,
            data_type=bool,
            listenerentity=self.chargertype.charger.entities.powerswitch,
            initval=False,
            currentname=self.chargertype.charger.entities.ampmeter,
            ampmeter_is_attribute=self.chargertype.charger.options.ampmeter_is_attribute,
            hubdata=self
        )

    @abstractmethod
    def init_hub_values(self):
        pass

@dataclass
class HubSensorsLite(IHubSensors):
   def setup(self):
        pass


@dataclass
class HubSensors(IHubSensors):
    powersensormovingaverage: HubMember = field(init=False)
    powersensormovingaverage24: HubMember = field(init=False)
    
    power: Power = field(init=False)

    def setup(self):
        pass


class HubSensorsFactory:
    @staticmethod
    def create(options: HubOptions) -> IHubSensors:
        if options.peaqev_lite:
            return HubSensorsLite()
        return HubSensors()



