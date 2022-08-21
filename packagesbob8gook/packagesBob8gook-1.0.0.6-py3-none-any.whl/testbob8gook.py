import kisa, whois
import sys


if __name__ == '__main__':
    args = sys.argv
    print(args)
    if args[1] == "whois":
    	whois.run()
    elif args[1] == "kisa":
        kisa.run()