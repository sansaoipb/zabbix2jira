#!/bin/bash
#
# This wrapper is used when configuring zabbix2jira as a media type
# instead of a action remote command. Since we don't have all the
# macros in the message alert, this wrapper parses the messages and
# runs the zabbix2jira with proper parameters.
#

LOG_FILE="/var/log/zabbix2jira.log"

function msg() {
  echo "$(date +[%F\ %T]) $@" | tee -a $LOG_FILE
}

function PrintUsage() {
  echo "Usage: $(basename $0) [-c file] <project> <summary> <message>"
  echo
  echo "  -c <file>    Use a custom configuration file on zabbix2jira"
  echo
  exit 1
}

while getopts "c:h" OPTION
do
  case $OPTION in
    c) CMD_ARGS="-c $OPTARG"
       ;;
    h) PrintUsage
       ;;
    ?) PrintUsage
       ;;
  esac
done
shift $((OPTIND-1))

PROJECT="$1" # macro {ALERT.SENDTO}
SUMMARY="$2" # macro {ALERT.SUBJECT}
MESSAGE="$3" # macro {ALERT.MESSAGE}

# check summary for the alert status
echo "$SUMMARY" | grep " PROBLEM " 1> /dev/null 2>&1
if [ $? -eq 0 ]; then
  ACTION="PROBLEM"
else
  ACTION="OK"
fi

# check message for additional information
EVENT_ID=$(echo "$MESSAGE" | egrep -o "* Event ID: [0-9]+" | egrep -o "[0-9]+")
if [ -n "$EVENT_ID" ]; then
  CMD_ARGS="$CMD_ARGS -i $EVENT_ID"
fi

COMPONENT=$(echo "$MESSAGE" | egrep "* Component: " | sed -r 's/^\* Component: //' | egrep -o '[a-zA-Z0-9]+')
if [ -n "$COMPONENT" ]; then
  CMD_ARGS="$CMD_ARGS -p $COMPONENT"
  MESSAGE=$(echo "$MESSAGE" | sed '/\* Component: /d')
fi

LABELS=$(echo "$MESSAGE" | egrep "* Labels: " | sed -r 's/^\* Labels: //' | egrep -o '[a-zA-Z0-9,]+')
if [ -n "$LABELS" ]; then
  CMD_ARGS="$CMD_ARGS -L $LABELS"
  MESSAGE=$(echo "$MESSAGE" | sed '/\* Labels: /d')
fi

ISSUE_TYPE=$(echo "$MESSAGE" | egrep "* Issue Type: " | sed -r 's/^\* Issue Type: //' | egrep -o '[a-zA-Z0-9]+')
if [ -n "$ISSUE_TYPE" ]; then
  CMD_ARGS="$CMD_ARGS -t $ISSUE_TYPE"
  MESSAGE=$(echo "$MESSAGE" | sed '/\* Issue Type: /d')
fi

# run the utility
msg "Sending to JIRA Project ${PROJECT}: ${SUMMARY}"
zabbix2jira -v -o $LOG_FILE $CMD_ARGS "$PROJECT" $ACTION "$SUMMARY" "$MESSAGE"
msg "Done. JIRA Project ${PROJECT}: ${SUMMARY}"
