import argparse
import os
import sys
import zlib

from . import binary_search_tree

argparser = argparse.ArgumentParser(description="Key-value store")
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

def main(argv=sys.argv[1:]):
    print("hello")
    args = argparser.parse_args(argv)
    if args.command == "init":
        cmd_init(args)
    elif args.command == "connect":
        cmd_connect(args)

class Database():

    path = None
    root = None # Root node

    def __init__(self, path):
        if not os.path.isdir(path):
            raise Exception("Not a database %s" % path)
        self.path = path
        
        data = ""
        data_path = self.get_path("data")
        if os.stat(data_path).st_size > 0:
            file = open(data_path, "rb")
            data = zlib.decompress(file.read()).decode()
            file.close()

        self.root = binary_search_tree.deserialize(data)

    def get_path(self, *path):
        return os.path.join(self.path, *path)

    # Serialize updated tree and write to data file
    def save(self):
        data_path = self.get_path("data")
        file = open(data_path, "wb")

        string = binary_search_tree.serialize(self.root)

        file.write(zlib.compress(string.encode()))
        file.close()

def db_init(path):
    print("(INIT)")

    if os.path.exists(path):
        raise Exception("%s already exists" % path)
    os.makedirs(path)

    file = open(os.path.join(path, "meta"), "x")
    file.close()
    file = open(os.path.join(path, "data"), "x")
    file.close()
    file = open(os.path.join(path, "logs"), "x")
    file.close()

def db_connect(path):
    print("(CONNECT)")

    if not os.path.exists(path):
        print("Path does not exist.")

    db = Database(path)

    # Main loop
    while True:
        cmd = input("What would you like to do? (get/put/del/quit): ")

        if cmd == "get":
            key = input("(GET) Key: ")

            result = binary_search_tree.search(db.root, key)

            if result:
                print(result)
            else:
                print("(GET) Key not found")
                
        
        elif cmd == "put":
            key = input("(PUT) Key: ")
            val = input("(PUT) Value: ")
            db.root = binary_search_tree.insert(db.root, key, val)

        elif cmd == "del":
            key = input("(DEL) Key: ")
            db.root = binary_search_tree.delete(db.root, key)

        elif cmd == "quit":
            print("(QUIT) Shutting down.")
            
            db.save()

            break

        else:
            print("Not sure what you meant by that.")
        
        cmd = None

argsp = argsubparsers.add_parser("init", help="Initialize a new database.")
argsp.add_argument("path", metavar="directory", nargs="?", default="./db", help="Location of database.")

def cmd_init(args):
    db_init(args.path)

argsp = argsubparsers.add_parser("connect", help="Connect to an existing database.")
argsp.add_argument("path", metavar="directory", nargs="?", default="./db", help="Location of database.")

def cmd_connect(args):
    db_connect(args.path)

if __name__ == "__main__":
    main()