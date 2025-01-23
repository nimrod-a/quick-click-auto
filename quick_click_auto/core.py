# This file is part of quick-click-auto.
# It is based on [auto-click-auto](https://github.com/KAUTH/auto-click-auto/)
# by Konstantinos Papadopoulos .
# Licensed under the MIT License.

import os
import platform
import subprocess
from typing import TYPE_CHECKING, Any, Callable, Optional, Set, TypeVar, Union

from click import Command, Context, Parameter, option

from .constants import ShellType
from .exceptions import ShellEnvVarNotFoundError, ShellTypeNotSupportedError
from .utils import (
    add_shell_configuration,
    create_file,
    detect_shell,
    remove_shell_configuration,
)

if TYPE_CHECKING:
    import typing_extensions as te

R = TypeVar("R")
T = TypeVar("T")
_AnyCallable = Callable[..., Any]
_Decorator: "te.TypeAlias" = Callable[[T], T]
FC = TypeVar("FC", bound=Union[_AnyCallable, Command])


def enable_click_shell_completion(
    program_name: str,
    shells: Optional[Set[ShellType]] = None,
    verbose: Optional[bool] = False,
) -> None:
    """
    Enable tab completion for Click's supported shell types.

    If ``shells`` is not provided, `quick-click-auto` will attempt to detect the
    shell type the user is currently running the program on.

    See https://click.palletsprojects.com/en/latest/shell-completion.
    `quick-click-auto` is using 

    :param program_name: The program name for which we enable shell completion,
    also described as the executable name.
    :param shells: The shell types for which we want to add tab completion
    support.
    :param verbose: `True` to print more details regarding the enabling,
    `False` otherwise. If this function is called on every run of the CLI
    program it might be better to set to `False`.
    :raise NotImplementedError: When ``shells`` option is not supported.
    """

    # Check that the program is run on one of the supported Operating Systems
    supported_os = ("Linux", "MacOS", "Darwin")
    os_name = platform.system()
    if os_name not in supported_os:
        if verbose is True:
            print(
                f"{os_name} is not one of the supported Operating Systems "
                f"({supported_os}) of `quick-click-auto`."
            )

        return None

    if shells is None:
        try:
            shells = {detect_shell()}

        except (ShellTypeNotSupportedError, ShellEnvVarNotFoundError) as err:
            if verbose is True:
                print(err)

            return None

    for shell in shells:

        if shell in (ShellType.BASH, ShellType.ZSH):

            # Translates to ~/.foo-bar-complete.shell
            completion_script_path = os.path.expanduser(
                f"~/.{program_name.lower().replace('-', '_')}.{shell.value}")

            # Edit shell config to auto source the file
            shell_config_file = os.path.expanduser(f"~/.{shell.value}rc")

            source_command = (
                f'source {completion_script_path} > /dev/null 2>&1'
            )

            old_config_string = (
                "# Shell completion configuration for the Click Python " +
                "package\n" + f"{program_name}"
            )

            remove_shell_configuration(
                shell_config_file=shell_config_file,
                config_string=old_config_string,
                verbose=verbose
            )

            add_shell_configuration(
                shell_config_file=shell_config_file,
                config_string=source_command,
                verbose=verbose,
            )

            # Translates to "$(_FOO_BAR_COMPLETE=shell_source foo-bar)"
            completion_script_function = f"$(_{program_name.upper().replace('-', '_')}_COMPLETE={shell.value}_source {program_name})"

            # Completion implementation: generate and source completion scripts
            generate_script_command = (
                f'echo \"{completion_script_function}\" > {completion_script_path}'
            )
            # Execute the command in the shell
            print(f"Executing '{generate_script_command}'")
            with open(os.devnull, 'w') as devnull:
                subprocess.run(generate_script_command,
                               shell=True, check=True, stderr=devnull)

        else:
            raise NotImplementedError


def enable_click_shell_completion_option(
    *param_decls: str,
    program_name: Optional[str] = None,
    shells: Optional[Set[ShellType]] = None,
    **kwargs: Any,
) -> _Decorator[FC]:
    """
    Add a ``--autocomplete`` option which enables tab completion and exits the
    program. This function can be used as a decorator in a Click command.

    If ``program_name`` is not provided, it will be detected from the command.

    If ``shells`` is not provided, `quick-click-auto` will attempt to detect the
    shell type the user is currently running the program on.

    Uses Click's `option` function. It is possible to pass the relevant
    function arguments to override the defaults ones, e.g., ``expose_value``,
    ``help``, etc.

    :param param_decls: One or more option names. Defaults to the single value
    ``"--autocomplete"``.
    :param program_name: The program name for which we enable shell completion,
    also described as the executable name.
    :param shells: The shell types for which we want to add tab completion
    support.
    :param kwargs: Extra arguments are passed to :func:`option`.
    """

    def callback(ctx: Context, param: Parameter, value: bool) -> None:
        if not value or ctx.resilient_parsing:
            return

        nonlocal program_name
        nonlocal shells

        if program_name is None:
            program_name = ctx.find_root().info_name

        assert program_name is not None

        enable_click_shell_completion(
            program_name=program_name, shells=shells, verbose=True
        )

        ctx.exit()
        return None

    if not param_decls:
        param_decls = ("--autocomplete",)

    kwargs.setdefault("is_flag", True)
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("is_eager", True)
    kwargs.setdefault("help", "Enable tab autocompletion and exit.")
    kwargs["callback"] = callback

    return option(*param_decls, **kwargs)
