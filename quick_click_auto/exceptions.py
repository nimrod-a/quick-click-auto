# This file is part of quick-click-auto.
# It is based on [auto-click-auto](https://github.com/KAUTH/auto-click-auto/)
# by Konstantinos Papadopoulos .
# Licensed under the MIT License.

class QuickClickAutoError(Exception):
    """Custom exception with an error message for `quick_click_auto`."""

    def __init__(self, message):
        super().__init__(message)


class ShellConfigurationFileNotFoundError(QuickClickAutoError):
    """Exception raised when the shell configuration file does not exist."""

    pass


class ShellTypeNotSupportedError(QuickClickAutoError):
    """Exception raised when the shell type is not supported."""

    pass


class ShellEnvVarNotFoundError(QuickClickAutoError):
    """
    Exception raised when the shell type cannot be inferred from the `SHELL`
    environment variable.
    """

    pass
