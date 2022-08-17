'''This module defines projection engine components.'''
from logging import debug
import pandas as pd
from frostaura.engines.asset_projection_engine import IAssetProjectionEngine

class SimpleAssetProjectionEngine(IAssetProjectionEngine):
    '''Calculations-related functionality using some maths under-the-hood.'''

    def __init__(self, config: dict = {}):
        self.config = config

    def project_monthly_asset_growth(self,
                                     n_months: int,
                                     annual_growth_rate: float,
                                     principal_value: float,
                                     monthly_deposit: float = 0) -> pd.DataFrame:
        '''Determine an asset's growth at a given annual rate over a specified number of months while applying a monthly deposit.'''

        data = {
            'month': list(),
            'deposits_withdrawals': list(),
            'interest': list(),
            'total_deposits_withdrawals': list(),
            'accrued_interest': list(),
            'balance': list()
        }

        data['month'].append(0)
        data['deposits_withdrawals'].append(0)
        data['interest'].append(0)
        data['total_deposits_withdrawals'].append(0)
        data['accrued_interest'].append(0)
        data['balance'].append(principal_value)

        for i in range(1, n_months + 1):
            data['month'].append(i)
            data['deposits_withdrawals'].append(monthly_deposit)
            data['interest'].append((annual_growth_rate / 12) * data['balance'][-1])
            data['accrued_interest'].append(data['accrued_interest'][-1] + data['interest'][-1])
            data['total_deposits_withdrawals'].append(data['total_deposits_withdrawals'][-1] + monthly_deposit)
            data['balance'].append(data['interest'][-1] + data['balance'][-1] + monthly_deposit)

        response: pd.DataFrame = pd.DataFrame(data)

        return response.set_index('month')

    def project_monthly_holdings_growth(self,
                                   n_months: int,
                                   annual_growth_rates: list,
                                   principal_values: list,
                                   monthly_deposits: list) -> pd.DataFrame:
        '''Determine a comprehensive holdings growth at a given annual rates over a specified numbers of months while applying a monthly deposits.'''

        projections: list = list()

        for month_index in range(len(annual_growth_rates)):
            projection = self.project_monthly_asset_growth(n_months=n_months,
                                                           annual_growth_rate=annual_growth_rates[month_index],
                                                           principal_value=principal_values[month_index],
                                                           monthly_deposit=monthly_deposits[month_index])

            projections.append(projection)

        data = {
            'month': list(),
            'deposits_withdrawals': list(),
            'interest': list(),
            'total_deposits_withdrawals': list(),
            'accrued_interest': list(),
            'balance': list()
        }

        for month_index in range(1, n_months + 1):
            data['month'].append(month_index)
            data['deposits_withdrawals'].append(sum([p.loc[month_index]['deposits_withdrawals'] for p in projections]))

            previous_row_balances: float = sum([p.loc[month_index - 1]['balance'] for p in projections])
            current_row_balances: float = sum([p.loc[month_index]['balance'] for p in projections])
            current_deposits: float = sum([p.loc[month_index]['deposits_withdrawals'] for p in projections])
            interest = 1 - previous_row_balances / (current_row_balances - current_deposits)

            data['interest'].append(interest)
            data['total_deposits_withdrawals'].append(sum([p.loc[month_index]['total_deposits_withdrawals'] for p in projections]))
            data['accrued_interest'].append(sum([p.loc[month_index]['accrued_interest'] for p in projections]))
            data['balance'].append(sum([p.loc[month_index]['balance'] for p in projections]))

        return pd.DataFrame(data)
