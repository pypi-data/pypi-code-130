import pickle
import sys
import argparse
from funcx.serialize import FuncXSerializer

if __name__ == '__main__':

    fxs = FuncXSerializer()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default='serialized_bufs.pkl')
    args = parser.parse_args()

    data = None
    with open(args.filename, 'rb') as f:
        data = pickle.load(f)
        print("Data loaded")

    if sys.version != data['metadata']['source_py_version']:
        print("Version Mismatch!!!", end='')
    print(f"Source:{data['metadata']['source_py_version']} Target:{sys.version}")

    for function in data:
        if function == 'metadata':
            continue
        print(f"Checking function:{function}")

        for ser_method in data[function]:
            print(f"Method : {ser_method}")
            key = data[function][ser_method]['key']
            buf = data[function][ser_method]['buffer']

            try:
                fxs.methods_for_code[key].deserialize(buf)
            except Exception:
                print(f"Failed to deserialize with {ser_method}")
