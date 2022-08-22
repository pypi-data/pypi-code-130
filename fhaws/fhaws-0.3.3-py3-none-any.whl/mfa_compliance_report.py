import time
import fhaws.iam as iam

def mfa_compliance_report(account):
    users = set([user['UserName'] for user in iam.get_users(account)])
    mfas =  set([mfa['User']['UserName'] for mfa in iam.get_mfas(account)])
    without_mfas = users - mfas 

    print("\nMFA Compliance Report: {}\n{}".format(time.asctime(), "-" * 47))
    print("Total Users: {}".format(len(users)))
    print("Total MFAs: {}".format(len(mfas))) 
    print("Users Without MFA: {}".format(len(without_mfas)))

    if without_mfas:
        print("Status: Not In Compliance ❌\n")
        print("Users out of compliance 😡:")
        for user in without_mfas:
            print("\t🔥 {}".format(user))
    else:
        print("Status: In Compliance ✅\n")

if __name__ == "__main__":
    account = "fredhutch" #profile to use
    mfa_compliance_report(account)