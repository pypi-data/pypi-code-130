import kisa, whois
import sys


def runServer(arg):
    print(arg)
    if arg == "whois":
    	whois.run()
    elif args == "kisa":
        kisa.run()