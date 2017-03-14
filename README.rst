zabbix2jira
===========

*Creates or updates a ticket on JIRA from Zabbix alarms*

Purpose
-------

zabbix2jira is a simple command line program that receives an action from
Zabbix (or any other script) and creates (or updates) a ticket on a project
inside a JIRA installation.

Installation
------------

Use the following command under the program directory::

    $ pip install -e .

We recommend using virtualenv to setup a self-contained app directory. In this
case, you should use::

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -e .

If you want to see which libraries this application uses, please check the
``requirements.txt`` file.

Usage
-----

Default paths:

- Configuration: */etc/zabbix/zabbix2jira.cfg*
- Log: */var/log/zabbix2jira.log*
- Cache Directory: */var/cache/zabbix2jira*

To run it, activate virtualenv first::

    $ source env/bin/activate
    $ zabbix2jira -h

Configuration
-------------

The command itself uses some default configuration, but you will want
to configure a file to configure your jira url, username and password.

Simply copy the ``sample-config.cfg`` file to the default configuration
path (*/etc/zabbix/zabbix2jira.cfg*) or copy to any location and use the
``-c`` parameter at the CLI call.

The file itself is self-explanatory.

Zabbix Integration
------------------

Create an action that calls the script with the proper variables.

We create a action named ``Zabbix2Dashboard`` with the conditions:

* A Maintenance status not in maintenance
* B Trigger value = PROBLEM
* C Trigger value = OK

And with calculation: ``A and (B or C)``. Pay attention to the
``(B or C)`` because we want to run the action both on alarm and recovery.

*Note: this changed on Zabbix 3.2. You can skip and B and C conditions
because on this version, problem and recovery operations are separate.*

Then on the *Operations* Tab, create a step that executes a ``Custom script``
on the Zabbix Server with the following commands::

    zabbix2jira -v -i {EVENT.ID} {TRIGGER.STATUS} "[Zabbix Alert] {HOSTNAME} - {TRIGGER.NAME}" "Alert Details"

You can also use the script as a user media and send a message to it.

Note that if using a *virtualenv* setup, activate it before the previous command::

    source /opt/z2d/env/bin/activate

Examples
--------

Here are some examples for running zabbix2jira.

Create an issue with component ``Alert``::

    zabbix2jira -v -p Alert PROBLEM "[Zabbix Alert] PROBLEM" "Alert Details"

With the zabbix backend enabled, track the event id (123) to acknowledge it::

    zabbix2jira -v -i 123 PROBLEM "[Zabbix Alert] PROBLEM" "Alert Details"

Recover the previous issue::

    zabbix2jira -v -i 123 OK "[Zabbix Alert] PROBLEM "Alert Details"

Create an issue with type ``Bug``::

    zabbix2jira -v -t Bug PROBLEM "[Zabbix Alert] PROBLEM" "Alert Details"
