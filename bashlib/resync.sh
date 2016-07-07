#!/bin/bash
# resync

# usage:
# resync source_dir target_ip_addr target_dir log_file

ARGS=4
E_BADARGS=85

if [ $# -ne "$ARGS" ]
then
  echo "Usage: 'basename $0' source_directory target_ip_address target_directory log_file"
  exit $E_BADARGS
fi

SOURCE_DIR=$1
TARGET_IP=$2
TARGET_DIR=$3
LOG_FILE=$4

resyncer () {
  while :
  do
    echo "
" 1>>$LOG_FILE
    date 1>>$LOG_FILE
    rsync -rtElv $SOURCE_DIR $TARGET_IP:$TARGET_DIR 1>>$LOG_FILE
    sleep 30m
  done
}

resyncer &
MYSELF=$!
touch $LOG_FILE
echo "PID for this process is $MYSELF.
" 1>$LOG_FILE

