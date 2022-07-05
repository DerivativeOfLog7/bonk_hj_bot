import sys


def die(msg: str, code: int) -> None:
    """Show a message, wait for the user to press enter, then exit"""
    print(msg)
    input()
    sys.exit(code)
