import argparse

from .lethe import snap, push_ref, fetch_ref


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--parent', '-p', action='append', default=['HEAD'])
    parser.add_argument('--target', '-t', action='append')
    parser.add_argument('--message', '-m')
    parser.add_argument('--repo', '-r')

    args = parser.parse_args()

    print(snap(parent_refs=args.parent,
               target_refs=args.target,
               message=args.message,
               cwd=args.repo))
    return 0


def push() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--remote', '-s', default='origin')
    parser.add_argument('--target', '-t', default='refs/lethe/LATEST')
    parser.add_argument('--repo', '-r')

    args = parser.parse_args()

    print(push_ref(remote=args.remote,
                   target_ref=args.target,
                   cwd=args.repo))
    return 0


def fetch() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--remote', '-s', default='origin')
    parser.add_argument('--target', '-t', default='refs/lethe/LATEST')
    parser.add_argument('--repo', '-r')

    args = parser.parse_args()

    print(fetch_ref(remote=args.remote,
                    remote_ref=args.target,
                    cwd=args.repo))
    return 0
