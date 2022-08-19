import boto3
from datetime import datetime, timedelta

def get_linked_account_charges(profile, start_date, end_date, resolution):
    "Gather the charge details (discount, taxes, charges) for accounts linked to parent"
    accounts = {}
    session = boto3.Session(profile_name=profile)
    client = session.client('ce')
    response = client.get_cost_and_usage(
                    TimePeriod={'Start':start_date.strftime("%Y-%m-%d"),'End':end_date.strftime("%Y-%m-%d")},
                    #TimePeriod={'Start':start_date,'End':end_date},
                    Granularity=resolution,
                    Metrics=['UNBLENDED_COST'],
                    GroupBy=[
                        {'Type':'DIMENSION','Key':'LINKED_ACCOUNT'},
                        {'Type':'DIMENSION','Key':'RECORD_TYPE'}
                        ]
                    )

    for item in response['ResultsByTime'][0]['Groups']:
        accountId = item['Keys'][0]
        account_type = item['Keys'][1]
        cost = float(item['Metrics']['UnblendedCost']['Amount'])
        if accountId not in accounts:
            accounts[accountId] = {}
        if "Discount" in account_type:
            accounts[accountId]['discount'] = cost
        if account_type == "Tax":
            accounts[accountId]['tax'] = cost
        if account_type == "Usage":
            accounts[accountId]['charges'] = cost

    return(accounts)

def accounts_with_taxes(profile):
    "Accounts should be tax exempt, report accounts that have tax charges"
    end_month = datetime.utcnow().date()
    start_month = (end_month - timedelta(days=end_month.day)).replace(day=1)
    accounts = get_linked_account_charges(profile, start_month, end_month, 'MONTHLY')
    paying_taxes = []
    for account in accounts:
        if accounts[account]['tax'] > 0:
            paying_taxes.append(account)
    
    return(paying_taxes)


if __name__ == "__main__":
    pass

    