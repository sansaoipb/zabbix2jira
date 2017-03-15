# -*- coding: utf-8 -*-
"""The problem command."""


from .base import Base
import sys


class Problem(Base):
    """Create an issue on a JIRA project"""

    def run(self, action):
        backends = self._get_enabled_backends()

        # jira backend is mandatory
        if not (backends['jira']):
            self.log.error("At least the JIRA backend must be working.")
            sys.exit(2)

        event_id = self.options['--event-id']

        # problem generator
        if (action.lower() == 'problem'):
            # create issue
            issue_id = self._create_issue(backends['jira'])
            # create acknowledge if zabbix is enabled
            if (issue_id and backends['zabbix']):
                self._ack_alert(backends['zabbix'], event_id, issue_id)

        # recovery generator
        elif (action.lower() == 'ok'):
            # close issue
            self._close_issue(backends['jira'], event_id)

    def _create_issue(self, jira_api):
        # get the meta from JIRA (issue type)
        try:
            meta = jira_api.createmeta(
                projectKeys=self.options['<project>'],
                issuetypeNames=self.options['--issue-type']
            )
        except Exception, e:
            self.log.error("Error while getting createmeta issue.")
            self.log.debug(e)
            sys.exit(1)

        issuetype_name = self.options['--issue-type']
        issuetype_id = meta['projects'][0]['issuetypes'][0]['id']

        issue = {
            'project': {'key': self.options['<project>']},
            'summary': self.options['<subject>'],
            'description': self.options['<message>'],
            'issuetype': {'id': issuetype_id, 'name': issuetype_name}
        }

        # optional component
        issue_component_name = self.options['--component']
        if (issue_component_name):
            issue['components'] = [{'name': issue_component_name}]

        # create the issue
        try:
            issue = jira_api.create_issue(issue)
        except Exception, e:
            self.log.error("Error while creating issue.")
            self.log.debug(e)
            sys.exit(1)

        self.log.info("Created issue %s" % issue.key)

        # if we have event id, let's track the event / issue
        if (self.options['--event-id']):
            self.log.debug("Zabbix event ID detected. Writing issue to cache.")
            self._set_event(
                self.options['--event-id'],
                issue.key
            )

        return issue.key

    def _close_issue(self, jira_api, event_id=False):
        # try to get issue key from cache
        if (event_id):
            self.log.debug("Zabbix event ID detected. Reading from cache.")
            issue_id = self._get_event(event_id)
            if (issue_id):
                issue = self._search_issue_by_id(jira_api, issue_id)
            else:
                self.log.warning("Can't find an issue key from cache.")
                self.log.warning("Searching on JIRA API with summary.")
                issue = self._search_issue_by_summary(
                    jira_api,
                    self.options['<project>'],
                    self.options['<subject>']
                )
        else:
            self.log.debug("Zabbix event ID not found.")
            self.log.warning("Searching on JIRA API with summary.")
            issue = self._search_issue_by_summary(
                jira_api,
                self.options['<project>'],
                self.options['<subject>']
            )

        if (issue):
            self.log.debug("Issue Key Found: %s" % issue.key)
            # close issue
            close_transition = self._get_config_str(
                'JIRA',
                'JIRA_CLOSE_TRANSITION'
            )
            try:
                jira_api.transition_issue(
                    issue.key,
                    close_transition,
                    comment=self.options['<message>'],
                )
            except Exception, e:
                self.log.error("Error while closing issue %s" % issue.key)
                self.log.debug(e)
                sys.exit(1)

        else:
            self.log.error("Could not find Issue Key. Can't close issue.")

    def _search_issue_by_summary(self, jira_api, project, summary):
        open_res = self._get_config_str(
            'JIRA',
            'JIRA_OPEN_RESOLUTION')
        search_str = ("project = \"%s\" AND resolution = \"%s\" AND "
                      "summary ~ '\"%s\"'") % (project, open_res, summary)
        try:
            search = jira_api.search_issues(
                search_str,
                startAt=0,
                maxResults=1
            )
        except:
            return False

        if len(search) > 0:
            return search[0]
        else:
            self.log.debug("Can't find any open issue for the alarm.")
            return False

    def _search_issue_by_id(self, jira_api, issue_id):
        try:
            issue = jira_api.issue(issue_id)
        except:
            self.log.debug("Can't find issues for key %s" % issue_id)
            return False

        if issue:
            return issue
        else:
            return False

    def _ack_alert(self, zabbix_api, event_id, issue_id):
        jira_url = self._get_config_str('JIRA', 'JIRA_URL')
        issue_url = jira_url + "browse/%s" % issue_id

        try:
            zabbix_api.event.acknowledge(
                eventids=event_id,
                message="Acknowledged by JIRA: %s" % issue_url
            )
        except Exception, e:
            self.log.error("Error while ack'ing zabbix alert %s" % event_id)
            self.log.debug(e)
            return False

        return True
