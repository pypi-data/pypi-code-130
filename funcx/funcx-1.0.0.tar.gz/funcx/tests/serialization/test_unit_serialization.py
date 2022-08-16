import sys
import argparse
import pickle
from funcx.serialize import FuncXSerializer
from funcx.tests.unit import imported_fn, imported_decorated_fn, imported_decorated_fn_2


def local_fn(x):
    return x + 1


def decorator(func):
    def wrapper(*args, **kwargs):
        x = func(*args, **kwargs)
        return f"wrap {x} wrap"
    return wrapper


@decorator
def local_decorated_fn(x):
    return x


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default='serialized_bufs.pkl')
    args = parser.parse_args()

    fxs = FuncXSerializer(use_offprocess_checker=True)

    local_wrapper_imported_fn = decorator(imported_fn)

    test_functions = [local_fn,
                      local_decorated_fn,
                      imported_fn,
                      local_wrapper_imported_fn,
                      imported_decorated_fn,
                      imported_decorated_fn_2]

    serialized = {}
    serialized['metadata'] = {'source_py_version': sys.version}

    for test_case in test_functions:
        test_case_name = test_case.__name__
        serialized[test_case_name] = {}
        print(f"\n\nTesting test_case : {test_case.__name__}")

        for key, method in fxs.methods_for_code.items():
            method_name = method.__class__.__name__

            print(f"\nTrying method {method_name:>20}   ", end='')
            current = {'buffer': None,
                       'key': key,
                       'serialize_worked': False,
                       'offprocess_check': False}
            serialized[test_case_name][str(method)] = current

            try:
                buf = method.serialize(test_case)
                current['buffer'] = buf
            except Exception:
                print("Serialization: FAILED  ", end='')
                continue

            print("Serialization:SUCCESS  ", end='')
            current['serialize_worked'] = True

            try:
                r = fxs.deserialize_check(buf)
            except Exception:
                print("Deserialization: FAILED  ", end='')
                # print(f"{method} failed during deserialize check")
                continue
            else:
                print("Deserialization:SUCCESS  ", end='')

            current['offprocess_check'] = True

    print()
    with open(args.filename, 'wb') as f:
        pickle.dump(serialized, f)
    print(serialized)
