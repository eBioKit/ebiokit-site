#!/bin/bash
HOST=$1
PASSWORD=$2
PLATFORM=$3
COMMAND=$4


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

if [[ "$PLATFORM" == "LINUX" ]]; then
    if [[ "$COMMAND" == "service status" ]]; then
        SERVICE=$5
        COMMAND="ids=\$(docker-compose -f /ebiokit_services/launchers/${SERVICE}/docker-compose.yml ps -q);  for id in \${ids[*]}; do docker inspect --format \"{{.Name}};{{.State.Status}};{{.Config.Image}}\" \$id; done"
        containers=$(sshpass -p $PASSWORD ssh ebiokit@${HOST} $COMMAND)
        RUNNING=0
        EXITED=0
        OTHER=0
        WARNING_MESSAGE=""

        for container in ${containers[*]}; do
              container=(${container//;/ });
              containerName=${container[0]};
              containerStatus=${container[1]};
              containerType=${container[2]};

              if [[ "$containerStatus" == "exited" ]]; then
                    if [[ "$containerType" != "busybox" ]]; then
                          EXITED=$((EXITED+1))
                          WARNING_MESSAGE="${WARNING_MESSAGE}Container $containerName is not running (current status is $containerStatus),";
                    fi
              elif [[ "$containerStatus" == "running" ]]; then
                    RUNNING=$((RUNNING+1))
              else
                    OTHER=$((OTHER+1))
                    WARNING_MESSAGE="${WARNING_MESSAGE}Container $containerName is not running (current status is $containerStatus),";
              fi
        done

        if [[ "$RUNNING" == 0 ]]; then
              echo "STOPPED";
        elif [[ "$EXITED" != 0 || "$OTHER" != 0 ]]; then
              echo "WARNING"
              echo ${WARNING_MESSAGE} >&2
        else
              echo "RUNNING";
        fi

    elif [[ "$COMMAND" == "service stop" ]]; then
        SERVICE=$5
        COMMAND="docker-compose -f /ebiokit_services/launchers/${SERVICE}/docker-compose.yml stop"
        sshpass -p $PASSWORD ssh ebiokit@${HOST} $COMMAND 2>> ../log/error.log >> ../log/services.log
    elif [[ "$COMMAND" == "service start" ]]; then
        SERVICE=$5
        COMMAND="docker-compose -f /ebiokit_services/launchers/${SERVICE}/docker-compose.yml up -d"
        sshpass -p $PASSWORD ssh ebiokit@${HOST} $COMMAND 2>> ../log/error.log >> ../log/services.log
    elif [[ "$COMMAND" == "service restart" ]]; then
        SERVICE=$5
        COMMAND="docker-compose -f /ebiokit_services/launchers/${SERVICE}/docker-compose.yml restart -d"
        sshpass -p $PASSWORD ssh ebiokit@${HOST} $COMMAND 2>> ../log/error.log >> ../log/services.log
      elif [[ "$COMMAND" == "service log" ]]; then
        LINES=$5
        SERVICE=$6
        COMMAND="docker-compose -f /ebiokit_services/launchers/${SERVICE}/docker-compose.yml logs | tail -$LINES"
        sshpass -p $PASSWORD ssh ebiokit@${HOST} $COMMAND
    else
        echo $COMMAND
        sshpass -p $PASSWORD ssh ebiokit@${HOST} $COMMAND
    fi
fi
