# -*- coding: utf-8 -*-
"""The base command class, with shared options from all other commands."""


import ConfigParser
import logging
import os
import json


class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

        # load configuration
        self.conf = ConfigParser.ConfigParser()
        self.conf.optionxform = str
        self.conf.read(self.options['--config'])

        # load logging
        self.log = logging.getLogger("")

    def _get_config_bool(self, section, option):
        return self.conf.getboolean(section, option)

    def _get_config_int(self, section, option):
        return self.conf.getint(section, option)

    def _get_config_float(self, section, option):
        return self.conf.getfloat(section, option)

    def _get_config_str(self, section, option):
        return self.conf.get(section, option)

    def _get_config_items(self, section):
        return self.conf.items(section)

    def _get_config_all(self):
        list = []
        for s in self.conf.sections():
            new_list = self._get_config_items(s)
            list = list + new_list
        return list

    def _get_enabled_backends(self):
        backends = {}

        # check for jira support
        if (self._get_config_bool('JIRA', 'ENABLE_JIRA')):
            self.log.info("Using JIRA backend")
            import jira

            jira_url = self._get_config_str(
                'JIRA', 'JIRA_URL')
            jira_user = self._get_config_str(
                'JIRA', 'JIRA_USERNAME')
            jira_password = self._get_config_str(
                'JIRA', 'JIRA_PASSWORD')

            self.log.debug(
                "Loading JIRA API (url: %s, username: %s)" % (
                    jira_url, jira_user)
            )

            try:
                backends['jira'] = jira.JIRA(
                    jira_url,
                    basic_auth=(jira_user, jira_password)
                )
            except Exception, e:
                self.log.error("Error connecting to JIRA API. Disabling it.")
                self.log.debug(e)
                backends['jira'] = False

        else:
            self.log.debug("JIRA backend is disabled.")
            backends['jira'] = False

        # check for zabbix support
        if (self._get_config_bool('Zabbix', 'ENABLE_ZABBIX')):
            self.log.info("Using Zabbix backend")
            from pyzabbix import ZabbixAPI

            zabbix_url = self._get_config_str(
                'Zabbix', 'ZABBIX_URL')
            zabbix_user = self._get_config_str(
                'Zabbix', 'ZABBIX_USERNAME')
            zabbix_password = self._get_config_str(
                'Zabbix', 'ZABBIX_PASSWORD')

            self.log.debug(
                "Loading Zabbix API (url: %s, username: %s)" % (
                    zabbix_url, zabbix_user)
            )

            try:
                backends['zabbix'] = ZabbixAPI(
                    url=zabbix_url,
                    user=zabbix_user,
                    password=zabbix_password
                )
            except Exception, e:
                self.log.error("Error connecting to Zabbix API. Disabling it.")
                self.log.debug(e)
                backends['zabbix'] = False

        else:
            self.log.debug("Zabbix backend is disabled.")
            backends['zabbix'] = False

        return backends

    def _set_event(self, event_id, issue):
        cache_dir = self._get_config_str('Main', 'CACHE_DIRECTORY')
        cache_file = os.path.join(cache_dir, event_id + ".json")
        self.log.debug("Writing to cache file %s" % cache_file)

        try:
            with open(cache_file, 'w') as fp:
                json.dump(issue, fp)
                fp.close()
        except Exception, e:
            self.log.debug(
                "Error writing cache file %s. Skipping." % cache_file)
            self.log.debug(e)
            return False

        return True

    def _get_event(self, event_id):
        cache_dir = self._get_config_str('Main', 'CACHE_DIRECTORY')
        cache_file = os.path.join(cache_dir, event_id + ".json")
        self.log.debug("Using cache file %s" % cache_file)

        try:
            fp = open(cache_file)
            event = json.load(fp)
            fp.close()
        except (IOError, EOFError):
            return False

        # remove file since we got it
        try:
            os.unlink(cache_file)
        except Exception, e:
            self.log.error("Error removing cache file %s." % cache_file)
            self.log.debug(e)

        return event

    def run(self):
        raise NotImplementedError(
            'You must implement the run() method yourself!')
