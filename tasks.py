"""Configures all tasks to run with invoke."""

from invoke import task
import glob
import os

@task(
    aliases=["flake8", "pep8"],
    help={
        'filename': 'File(s) to lint. Supports globbing.',
        'envdir': 'Specify the python virtual env dir to ignore. Defaults to "venv".',
        'noglob': 'Disable globbing of filenames. Can give issues in virtual environments',
    },
)
def lint(ctx, filename=None, envdir=['env', 'venv'], noglob=False):
    """Run flake8 python linter."""

    excludes = ['.git' ]
    if isinstance(envdir, str):
        excludes.append(str)
    else:
        for x in envdir:
            excludes.append(x)

    command = 'flake8 --jobs=1 --exclude ' + ','.join(excludes)

    if filename is not None:
        if noglob:
            templates = [filename]
        else:
            templates = [x for x in glob.glob(filename)]
            if len(templates) == 0:
                print("File `{0}` not found".format(filename))
                exit(1)

        command += ' ' + " ".join(templates)

    print("Running command: '" + command + "'")
    os.system(command)
