import boto3

def create_tax_exempt_case(profile, taxed_accounts):
    "Open a support request with AWS to have them change accounts to tax exempt status"
    session = boto3.Session(profile_name=profile)
    client = session.client('support', endpoint_url='https://support.us-east-1.amazonaws.com')
    messageBody = """The following AWS account numbers are currently paying sales tax but should have a tax exempt status:
                    \n\t - {}\t\n\nPlease modify these accounts to have a tax exempt status.\n""".format("\n\t - ".join(taxed_accounts))

    response = client.create_case(subject='Accounts with incorrect tax exempt status',
                serviceCode='billing', severityCode='normal', categoryCode='us-sales-tax',
                communicationBody=messageBody, language='en', issueType='customer-service')

if __name__ == "__main__":
    pass