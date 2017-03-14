# -*- coding: utf-8 -*-
"""zabbix2jira

Usage:
    zabbix2jira.py [options] <project> ACTION <subject> <message>
    zabbix2jira.py [options] clean
    zabbix2jira.py --version
    zabbix2jira.py -h

Arguments:
    ACTION    Use OK|PROBLEM to determine status
    clean     Remove all files from the cache

Examples:
    zabbix2jira.py INFRA PROBLEM "High Alarm" "Description of alarm"
    zabbix2jira.py INFRA OK "High Alarm" "Recover of alarm"

Options:
    -i, --event-id=<id>     Unique event ID from Zabbix (tracking)
    -t, --issue-type=<type> Issue Type from JIRA Project [default:
        Task]
    -p, --component=<name>  Component name from JIRA Project [default:
        False]
    -c, --config=<file>     Configuration file [default:
        /etc/zabbix/zabbix2jira.cfg]
    -o, --output=<file>     Log output to file [default:
        /var/log/zabbix2jira.log]
    -v, --verbose           Verbose output
    -d, --debug             Debug output
    -q, --quiet             Quiet output
    -h, --help              Show this screen.
    --quiet         Silent output
    --version       Show version.
"""
from inspect import getmembers, isclass
from docopt import docopt
import sys
import logging
import re
from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import commands

    options = docopt(
        __doc__,
        version="zabbix2jira %s" % (VERSION)
    )

    # intialize logging
    if options['--debug'] is True:
        log_level = logging.DEBUG
    elif options['--verbose'] is True:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    log = logging.getLogger("")
    log.setLevel(log_level)

    # stdout handler if needed
    if not (options['--quiet']):
        log_ch = logging.StreamHandler(sys.stdout)
        log_ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        log.addHandler(log_ch)

    # file handler if needed
    if (options['--output']):
        log_fh = logging.FileHandler(options['--output'])
        log_fh.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        log.addHandler(log_fh)

    # clean command
    if (options['clean']):
        module = getattr(commands, 'clean')

    # unknown command
    elif not (re.search(
        '(OK|PROBLEM)',
        options['ACTION'],
        re.IGNORECASE)
    ):
        log.critical(
           "zabbix2jira: unknown action %s" % options['ACTION'])
        sys.exit(1)

    # default command (ok/problem)
    else:
        module = getattr(commands, 'problem')

    commands = getmembers(module, isclass)
    command = [
        command[1] for command in commands if command[0] != 'Base'
    ][0]
    command = command(options)
    command.run(options['ACTION'])
