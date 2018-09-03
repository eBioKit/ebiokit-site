#!/bin/bash
PLATFORM=$1
COMMAND=$2


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

if [[ "$PLATFORM" == "LINUX" ]]; then
    if [[ "$COMMAND" == "service status" ]]; then
        SERVICE=$3
        DATA_LOCATION=$4
        containers=()
        ids=$(docker-compose -f ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}/docker-compose.yml ps -q);
        for id in ${ids[*]}; do
            containers+=($(docker inspect --format "{{.Name}};{{.State.Status}};{{.Config.Image}}" $id))
        done

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
        SERVICE=$3
        DATA_LOCATION=$4
        docker-compose -f ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}/docker-compose.yml stop 2>> ../../log/error.log >> ../../log/services.log
    elif [[ "$COMMAND" == "service start" ]]; then
        SERVICE=$3
        DATA_LOCATION=$4
        docker-compose -f ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}/docker-compose.yml up -d 2>> ../../log/error.log >> ../../log/services.log
    elif [[ "$COMMAND" == "service restart" ]]; then
        SERVICE=$3
        DATA_LOCATION=$4
        docker-compose -f ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}/docker-compose.yml restart -d 2>> ../../log/error.log >> ../../log/services.log
    elif [[ "$COMMAND" == "service log" ]]; then
        SERVICE=$3
        DATA_LOCATION=$4
        LINES=$5
        docker-compose -f ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}/docker-compose.yml logs | tail -$LINES
    elif [[ "$COMMAND" == "service rm" ]]; then
        SERVICE=$3
        DATA_LOCATION=$4
        docker-compose -f ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}/docker-compose.yml rm -f  2>> ../../log/error.log >> ../../log/services.log
    elif [[ "$COMMAND" == "service rmi" ]]; then
        SERVICE=$3
        DATA_LOCATION=$4
        docker-compose -f ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}/docker-compose.yml down --rmi all 2>> ../../log/error.log >> ../../log/services.log
    else
        echo "Unknown option "
        exit 1
    fi
fi
