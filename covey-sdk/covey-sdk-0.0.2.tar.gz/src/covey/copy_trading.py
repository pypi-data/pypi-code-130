import datetime
import pandas as pd
from portfolio import Portfolio
from collections.abc import Iterable
from dotenv import load_dotenv

load_dotenv()

# gather the portfolio state as of point in time
def get_composite_portfolio(addresses):
    # make sure the list of addresses is an interable list
    if not isinstance(addresses, Iterable) or isinstance(addresses, str):
        # convert it to list if needed
        addresses = [addresses] 

    # grab current timestamp - this will be used to get 'active positions' in the portfolio
    current_time_stamp = datetime.datetime.now()

    # get rid of minute,second, and microsecond (lol)
    current_time_stamp_clean = current_time_stamp.replace(minute =0, second =0, microsecond =0)

    tracked_addresses = addresses

    # create a portfolio instance for each address
    tracked_portfolios = [Portfolio(address = a) for a in tracked_addresses]

    # calculate each portfolio in the tracked list
    [t.calculate_portfolio() for t in tracked_portfolios]

    # capture the portfolios current (gross) positions (this will eventually be done at 3:45pm) 
    tracked_current_gross_positions = pd.concat([p.get_active_positions(current_time_stamp_clean) for p in tracked_portfolios])

    # create the target percent abs column - since we are de-GROSS-ing
    tracked_current_gross_positions['target_percentage_abs'] = abs(tracked_current_gross_positions['target_percentage'].astype(float))

    # get the total gross position amount per user
    tracked_current_gross_positions['user_gross_pct'] = tracked_current_gross_positions.groupby('address')['target_percentage_abs'].transform('sum')

    # create the percentage adjusted to degross
    tracked_current_gross_positions['target_percentage_adj'] = tracked_current_gross_positions['target_percentage'].astype(float)/tracked_current_gross_positions['user_gross_pct'].astype(float)

    # isolate columns we need to aggregate
    agg_columns = ['target_percentage','target_percentage_abs', 'user_gross_pct','target_percentage_adj','post_cumulative_share_count']

    # isolate columns to aggregate BY
    agg_by_columns = ['symbol']

    # create the aggregated (composite) portfolio
    composite_portfolio = tracked_current_gross_positions[agg_by_columns + agg_columns].groupby(agg_by_columns).sum()

    return composite_portfolio

# trade posting function - passing in the copy_portfolio - standalone single user address
def post_rebalance_trades(user_address : str, trades : dict):
    p = Portfolio(address = user_address)

    # convert the trades dict to one long string
    trades_str = ''
    for k,v in trades.items():
        trades_str += k + ':' + str(v) + ','

    # remove the last comma
    trades_str = trades_str.rstrip(trades_str[-1])

    # call the post trades function from the trades class (inherited in the Portfolio class)
    p.post_trades_polygon(trades_str)
    return 0

# rebalancing logic - since a trade string is composed of a series of tickers and target allocations, we don't need a difference between
# the two target_percentage_adj columns in the comaprison df but rather just a set of rules that tell us when to resize with the new target
# note that since we filter out current positions of 0 in the get_active_positions function of the Portfolio class, the only time there should
# be a zero rebalance situation is if we see a ticker in left hand side only
def get_rebalance_amount(row, threshold):
    # grab the difference in target percentages
    target_diff = abs(row['target_percentage_adj_y'] - row['target_percentage_adj_x'])

    # if the ticker only appears on the left side of comparison df, it dropped off and we must zero it out
    if row['_merge'] == 'left_only':
        return 0
    # now we see the ticker on both sides - we resutn the right hand side allocation only if the difference is above a certain threshold
    # note returning 888 which will be an indicator to drop it from the trades list. Can't use 0 because that's a legitimate allocation
    elif row['_merge'] == 'both':
        return row['target_percentage_adj_y'] if target_diff > threshold else 888
    # if it's in the right side only then its easy, we need to enter a (new) ticker we did not have before
    elif row['_merge'] == 'right_only':
        return row['target_percentage_adj_y']
    # otherwise return 888 again for it to be deleted (this should never be hit but here just in case)
    else:
        return 888

# export to csv
def export_to_csv(df:pd.DataFrame, name : str):
    df.to_csv(name +'.csv')
    return 0

if __name__ == "__main__":
    # user will have needed to already created an account (wallet) in metamask
    # https://myterablock.medium.com/how-to-create-or-import-a-metamask-wallet-a551fc2f5a6b
    user_address = '0xA9f484902d2905e4d95513C4e7d06CA08211bd4b'  # vadim's copy trading meta mask

    # copy portfolio addresses we will be copying from
    # set a list of addresses to track - can be made dynamic later
    copy_addresses = ['0xf66aD6E503F8632c85C82027c9Df12FAE205e916','0xa3893f84cb02cd9ad96a5b689f43f731e81416a9','0xac179aa0b2bdd996bd2df83c5a33fff63d1b7c72']

    # get the user's portfolio, still using the composite function but its a single item list so trivially a non composite portfolio
    user_portfolio = get_composite_portfolio(user_address)

    # get the composite portfolio from the copy addresses
    copy_portfolio = get_composite_portfolio(copy_addresses)

    # create a comparision dataframe of the user and copy portfolio to see what we need to rebalance
    comparison_df = pd.merge(user_portfolio, copy_portfolio, on = 'symbol', how = 'outer',indicator=True)

    # fill in the blank adjusted target percentages (as of 100% gross) with 0s to avoid math issues
    comparison_df['target_percentage_adj_x'].fillna(0, inplace=True)
    comparison_df['target_percentage_adj_y'].fillna(0, inplace=True)

    # if there is a post cumulative share count of 0 but the target percentage is !=0, that means we had a position that did not price,
    # but nevertheless that trade should still happen
    # calculate the rebalancing trades - thereshold passed in here as 0.01
    comparison_df['rebalance_amount'] = comparison_df.apply(get_rebalance_amount,threshold = 0.01, axis=1)

    # remove the 888 unecessary lines that don't need rebalancing
    comparison_df = comparison_df[comparison_df['rebalance_amount'] != 888]

    # check the user portfolio in csv
    export_to_csv(comparison_df, "comparison_df")

    # extract the trades needed to rebalance
    rebalance_dict = comparison_df.to_dict()['rebalance_amount']
    
    # print out the trades needed
    print(rebalance_dict)

    # post the rebalance (or initial if new portfolio) trades
    #post_rebalance_trades(user_address, rebalance_dict)

    # check to make sure the portfolios are aligned
