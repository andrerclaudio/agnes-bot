# pylint: disable=missing-module-docstring missing-function-docstring wrong-import-order unused-argument import-error useless-return
# pylint: disable=line-too-long too-many-locals invalid-name unused-import consider-using-f-string wildcard-import unused-wildcard-import

"""
Entry point to the code.
Telegram bot snippet to run a bot and interact with people.
"""


# Import the main application
from app import application


def main():
    """
    Run the application.
    """
    application()
    return None


if __name__ == "__main__":
    # Run the main function.
    main()
