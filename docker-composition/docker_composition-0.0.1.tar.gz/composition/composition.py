import os

import fire


def main():
    print(f"Hello, {os.getcwd()}")


def entrypoint():
    fire.Fire(main)


if __name__ == "__main__":
    entrypoint()
