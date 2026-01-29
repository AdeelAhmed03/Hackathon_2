"""
Main entry point for the todo application.
"""

from .cli import TodoCLI


def main() -> None:
    """
    Main function to run the todo application.
    """
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()