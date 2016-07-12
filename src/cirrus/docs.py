#!/usr/bin/env python
"""
_docs_

Implement git cirrus docs command


"""
from argparse import ArgumentParser
from cirrus.configuration import load_configuration
from cirrus.documentation_utils import (
    build_docs,
    build_doc_artifact,
    upload_documentation
)


def build_parser(argslist):
    """
    _build_parser_

    Set up command line parser for the docs command

    """
    parser = ArgumentParser(
        description='git cirrus docs command'
    )
    parser.add_argument('command', nargs='?')

    subparsers = parser.add_subparsers(dest='command')
    build_command = subparsers.add_parser(
        'build',
        help='Build Sphinx documentation by calling the make command'
    )
    build_command.add_argument(
        '--make',
        nargs='*',
        help=('generate documentation with Sphinx (Makefile path must be set '
              'in cirrus.conf) and create an artifact. Argument list is used '
              'to run the Sphinx make command. Default: clean html')
    )
    build_command.set_defaults(make=[])

    pack_command = subparsers.add_parser(
        'pack',
        help='Package documentation as a tarball'
    )

    upload_command = subparsers.add_parser(
        'upload',
        help='Upload documentation to a remote server'
    )
    upload_command.add_argument(
        '--file-server',
        action='store',
        dest='file_server',
        help='upload documentation to specified file server'
    )
    upload_command.add_argument(
        '--fs-sudo',
        action='store_true',
        dest='fs_sudo',
        help='use sudo to upload doc artifact to the file server'
    )
    upload_command.add_argument(
        '--no-fs-sudo',
        action='store_false',
        dest='fs_sudo',
        help='do not use sudo to upload doc artifact to the file server'
    )
    upload_command.set_defaults(fs_sudo=True)

    opts = parser.parse_args(argslist)
    return opts


def main():
    opts = build_parser(sys.argv)
    if opts.command == 'build':
        build_docs(make_opts=opts.make)

    if opts.command == 'pack':
        build_doc_artifact()

    if opts.command == 'upload':
        upload_documentation(opts)


if __name__ == '__main__':

    main()
