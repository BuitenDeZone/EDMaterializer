"""Configures all tasks to run with invoke."""

from invoke import task
import glob
import os
from version import VERSION

@task(
    aliases=["flake8", "pep8"],
    help={
        'filename': 'File(s) to lint. Supports globbing.',
        'envdir': 'Specify the python virtual env dir to ignore. Defaults to "venv".',
        'noglob': 'Disable globbing of filenames. Can give issues in virtual environments',
    },
)
def lint(ctx, filename=None, envdir=['env', 'venv'], noglob=False):
    """Run flake8 python linter.

    :param ctx: Invoke context
    :param filename: A filename to check.
    :param envdir: python environment dirs. We exclude these
    :param noglob: Disable globbing in the filename.
    """

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


@task(
    help={
        'out': 'Where to store the file',
    },
)
def release(ctx, out='out'):
    """Perform release task.

    Creates a zip with required files and prefix Materializer. Github auto packing includes the version
    number in the prefix.
    """

    command = 'git archive {} --prefix Materializer/ --format=zip --output {}/Materializer-{}.zip'.format(
        VERSION, out, VERSION)

    print("Running command: '" + command + "'")
    if not os.path.isdir(out):
        os.mkdir('out')

    os.system(command)