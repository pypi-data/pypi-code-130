def get_estimated_charges(profile):
    session = boto3.Session(profile_name=profile)
    client = session.client('cloudwatch', region_name='us-east-1')
    today = datetime.now() + timedelta(days=1)    
    yesterday = timedelta(days=2)
    start_date = today - yesterday
    
    response = client.get_metric_statistics(
        Namespace='AWS/Billing',
        MetricName='EstimatedCharges',
        Dimensions=[
            {
            'Name': 'Currency',
            'Value': 'USD'
            },
        ],
        Period=86400,
        StartTime=start_date,
        EndTime=today,
        Statistics=['Maximum'],
        Unit='None'
    )
    maxi = 0
    for x in response['Datapoints']:
        if x['Maximum'] > maxi:
            maxi = x['Maximum']

    print(maxi) 