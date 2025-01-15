[![GitHub license](https://img.shields.io/github/license/KAUTH/auto-click-auto)](https://github.com/KAUTH/auto-click-auto/blob/master/LICENSE).
[![pypi](https://img.shields.io/pypi/v/auto-click-auto.svg)](https://pypi.org/project/quick-click-auto/)

# quick-click-auto
Enable quick tab autocompletion for complex Click CLI applications. 

`quick-click-auto` is a small Python library that is used to quickly add tab shell completion support for
_Bash_ (version 4.4 and up), _Zsh_ for [Click](https://click.palletsprojects.com/en/8.1.x/#) CLI programs, and can be easily integrated as a Click command: 
```commandline
foo-bar --generate-command-completion 
```

## Why this fork exists
This project is a modified version of [auto-click-auto](https://github.com/KAUTH/auto-click-auto) by [KAUTH](https://github.com/KAUTH).
The original project is licensed under the [MIT License](https://github.com/nimrod-a/quick-click-auto/blob/main/LICENSE).

The main difference of this fork is the way shell completion is implemented.  

In the original version, `auto-click-auto` generates the command completion scripts everytime the shell is opened.
According to the official [Click docs](https://click.palletsprojects.com/en/stable/shell-completion/#enabling-completion), this has perfomance drawbacks: 
> Using eval means that the command is invoked and evaluated every time a shell is started, which can delay shell responsiveness

 This Fork aims to solve the perfomace hit by utilizing Clicks alternative approach:
> To speed [command completion] up, write the generated script to a file, then source that

**This alternative approach enables quickly adding command completion to complex CLI applications, where auto-click-auto may lead to reduced performance.**

It is important to note that the improved performance only applies when `quick-click-auto` is used as a seperate click command. 

In contrast to auto-click-auto, **this project currently does not automatically enable command autocompletion**. 

*Due to the specific target group and the substantial changes to the original codebase needed to implement this approach, I have decided to create a detached fork, instead of contributing upstream.*

For more information, take a look at [Implementation](#implementation).

## Installation
```commandline
pip install quick-click-auto
```

## Usage
There are two functions that `quick-click-auto` makes available: `enable_click_shell_completion` (general use)
and `enable_click_shell_completion_option` (to be used as a decorator).

In the function docstrings, you can find a detailed analysis of the available parameters and their use.

`quick-click-auto` will print the relative output when a shell completion is activated for the first time and can be
set to an extra verbosity if you want to display information about already configured systems or debug.

Here are some typical ways to enable autocompletion with `quick-click-auto`:


1) **Make shell completion a Click command option**

Example:
```python
import click

from quick_click_auto import enable_click_shell_completion_option


@click.command()
@enable_click_shell_completion_option(program_name="example-2")
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")
```

2) **Make shell completion a command (or subcommand of a group)**

This implementation option might be useful if you already have a "configuration" command in your CLI program.

Example:
```python
import click

from quick_click_auto import enable_click_shell_completion
from quick_click_auto.constants import ShellType


@click.group()
def cli():
    """Simple CLI program."""
    pass


@cli.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello(count, name):
    """Simple command that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")


@cli.group()
def config():
    """Program configuration."""
    pass


@config.command()
def shell_completion():
    """Activate shell completion for this program."""
    enable_click_shell_completion(
        program_name="example-3",
        shells={ShellType.BASH, ShellType.ZSH},
        verbose=True,
    )
```


## Implementation
`quick-click-auto` enables tab autocompletion based on [Click's documentation](https://click.palletsprojects.com/en/8.1.x/shell-completion/).

To enable command completion in Click CLI applications, the user needs to manually register a special function with the shell. The exact script varies depending on which shell is used.

The approach used by  `auto-click-auto` is to add a line to the shell configuration file, which generates the command completion scripts everytime the shell is started: 
```commandline
eval "$(_FOO_BAR_COMPLETE=shell_source foo-bar)"
```
As said, this may lead to delayed shell responsiveness, especially in complex CLI applications. On the upside, it can enable completley automatic shell autocompletion.

`quick-click-auto` on the other hand generates the command completion scripts only once and then sources them in the shell configuration file.

This is especially useful when integrating quick-click-auto as configuration command or a CLI option and greatly improves perfomance. 