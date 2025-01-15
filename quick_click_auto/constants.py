# This file is part of quick-click-auto.
# It is based on [auto-click-auto](https://github.com/KAUTH/auto-click-auto/)
# by Konstantinos Papadopoulos .
# Licensed under the MIT License.

from enum import Enum
from typing import List, Set


class ShellType(str, Enum):
    """An enum with the supported shell types for tab autocompletion."""

    BASH = "bash"
    ZSH = "zsh"

    @classmethod
    def get_all(cls) -> Set[str]:
        """Return a set of all the supported shell types."""

        return {e for e in cls}

    @classmethod
    def get_all_values(cls) -> List[str]:
        """Return a list with all the enum members' values, the shell names."""

        return [e.value for e in cls]
