'''This module defines private manager components.'''
import pandas as pd
from frostaura.managers.asset_reporting_manager import IAssetReportingManager
from frostaura.data_access.personal_asset_data_access import IPersonalAssetDataAccess
from frostaura.engines.asset_calculations_engine import IAssetCalculationsEngine
from frostaura.engines.asset_projection_engine import IAssetProjectionEngine
from frostaura.models.profit_calculation_result import ProfitCalculationResult
from frostaura.engines.asset_valuation_engine import IAssetValuationEngine
from frostaura.models import ValuationResult

class PersonalAssetReportingManager(IAssetReportingManager):
    '''Component to perform functions related to personal asset reporting.'''

    def __init__(self,
                 personal_asset_data_access: IPersonalAssetDataAccess,
                 asset_calculation_engine: IAssetCalculationsEngine,
                 asset_valuation_engine: IAssetValuationEngine,
                 asset_projection_engine: IAssetProjectionEngine,
                 config: dict = {}):
        self.personal_asset_data_access = personal_asset_data_access
        self.asset_calculation_engine = asset_calculation_engine
        self.asset_valuation_engine = asset_valuation_engine
        self.asset_projection_engine = asset_projection_engine
        self.config = config

    def __send_holdings_report__(self, holdings: list, holdings_profits: pd.DataFrame):
        overall_holdings_profit: ProfitCalculationResult = self.asset_calculation_engine.calculate_holdings_profit(holdings)
        holding_ratios: pd.DataFrame = self.asset_calculation_engine.calculate_holdings_ratios(holdings=holdings)

        overall_holdings_message: str = f'Overall Holdings Profits: ${round(overall_holdings_profit.value, 2)} ({round(overall_holdings_profit.percentage)}%)'
        #import matplotlib.pyplot as plt
        #import numpy as np
        #labels: list = [k for k in holding_ratios]
        #ratios: list = [holding_ratios[k] for k in holding_ratios]

        #plt.pie(ratios, labels=labels)
        #plt.show()
        print(f'holdings_profits: {holdings_profits}')
        print(overall_holdings_message)
        print(f'holding_profits: {holding_ratios}')

    def __send_wealth_projections_report(self,
                                         n_months: int,
                                         holdings_profits: pd.DataFrame,
                                         monthly_deposits: float):

        deposit_amounts_to_project: list = [
            monthly_deposits,
            monthly_deposits * 2,
            monthly_deposits * 4
        ]
        results: dict = {}

        for deposit_amount in deposit_amounts_to_project:
            results[deposit_amount] = {
                'annual_growth_rates': list(),
                'principal_values': list(),
                'monthly_deposits': list()
            }

            for row_index, row in holdings_profits.iterrows():
                company_name: str = row['name']
                symbol_valuation: ValuationResult = self.asset_valuation_engine.valuate(company_name=company_name,
                                                                                        symbol=row['symbol'])
                annual_growth_rate: float = symbol_valuation.eps_five_years

                if symbol_valuation.annual_dividend_percentage is not None:
                    annual_growth_rate += (symbol_valuation.annual_dividend_percentage / 100)

                results[deposit_amount]['annual_growth_rates'].append(annual_growth_rate)
                results[deposit_amount]['principal_values'].append(row['total_current_usd'])
                results[deposit_amount]['monthly_deposits'].append((deposit_amount / len(holdings_profits)))

            holdings_growth: pd.DataFrame = self.asset_projection_engine.project_monthly_holdings_growth(n_months=n_months,
                                                                                    annual_growth_rates=results[deposit_amount]['annual_growth_rates'],
                                                                                    principal_values=results[deposit_amount]['principal_values'],
                                                                                    monthly_deposits=results[deposit_amount]['monthly_deposits'])

            results[deposit_amount]['holdings_growth'] = holdings_growth

        print(results)

    def send_reports(self):
        '''Generate and send asset reports.'''

        holdings: list = self.personal_asset_data_access.get_personal_transactions()
        holdings_profits: pd.DataFrame = self.asset_calculation_engine.calculate_holdings_profits(holdings=holdings)
        n_months_to_project: int = 12 * 15 # 15 Years
        usd_zar_exchange_rate: float = 16.17
        monthly_deposits: float = 1000 / usd_zar_exchange_rate

        self.__send_holdings_report__(holdings=holdings,
                                      holdings_profits=holdings_profits)
        self.__send_wealth_projections_report(n_months=n_months_to_project,
                                              holdings_profits=holdings_profits,
                                              monthly_deposits=monthly_deposits)
