'''This module defines private manager components.'''
from frostaura.managers.asset_reporting_manager import IAssetReportingManager
from frostaura.data_access.personal_asset_data_access import IPersonalAssetDataAccess
from frostaura.engines.asset_calculations_engine import IAssetCalculationsEngine
from frostaura.models.profit_calculation_result import ProfitCalculationResult

class PersonalAssetReportingManager(IAssetReportingManager):
    '''Component to perform functions related to personal asset reporting.'''

    def __init__(self,
                 personal_asset_data_access: IPersonalAssetDataAccess,
                 asset_calculation_engine: IAssetCalculationsEngine,
                 config: dict = {}):
        self.personal_asset_data_access = personal_asset_data_access
        self.asset_calculation_engine = asset_calculation_engine
        self.config = config

    def __send_holdings_report__(self):
        raise NotImplementedError()

    def __send_wealth_projections_report(self):
        raise NotImplementedError()

    def send_reports(self):
        '''Generate and send asset reports.'''

        self.__send_holdings_report__()
        self.__send_wealth_projections_report()

        holdings: list = self.personal_asset_data_access.get_personal_transactions()
        holdings = self.asset_calculation_engine.interpolate_holdings_profits(holdings=holdings)
        overall_holdings_profit: ProfitCalculationResult = self.asset_calculation_engine.calculate_holdings_profit(holdings)

        #import matplotlib.pyplot as plt
        #import numpy as np

        holding_ratios: dict = self.asset_calculation_engine.calculate_holdings_ratios(holdings=holdings)
        #labels: list = [k for k in holding_ratios]
        #ratios: list = [holding_ratios[k] for k in holding_ratios]

        #plt.pie(ratios, labels=labels)
        #plt.show() 
