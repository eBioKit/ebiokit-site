#!/bin/bash

PLATFORM=$1
COMMAND=$2

main(){
  DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  cd $DIR

  if [[ "$COMMAND" == "service_status" ]]; then
      SERVICE=$3
      DATA_LOCATION=$4

      if is_core_service "$SERVICE"; then
        check_core_service "$SERVICE" "$COMMAND"
        exit $?
      fi

      containers=()
      cd ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}
      ids=$(docker-compose ps -q);
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
                  if [[ "$containerType" != "busybox" ]]; then  # Ignore busybox containers usually used for data persistance
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
  elif [[ "$COMMAND" == "service_stop" ]]; then
      SERVICE=$3
      DATA_LOCATION=$4

      echo $SERVICE

      if is_core_service "$SERVICE"; then
        check_core_service "$SERVICE" "$COMMAND"
        exit $?
      fi
      cd ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}
      docker-compose stop 2>> ${DATA_LOCATION}/ebiokit-logs/error.log >> ${DATA_LOCATION}/ebiokit-logs/services.log
  elif [[ "$COMMAND" == "service_start" ]]; then
      SERVICE=$3
      DATA_LOCATION=$4

      if is_core_service "$SERVICE"; then
        check_core_service "$SERVICE" "$COMMAND"
        exit $?
      fi
      cd ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}
      docker-compose up -d 2>> ${DATA_LOCATION}/ebiokit-logs/error.log >> ${DATA_LOCATION}/ebiokit-logs/services.log
  elif [[ "$COMMAND" == "service_restart" ]]; then
      SERVICE=$3
      DATA_LOCATION=$4

      if is_core_service "$SERVICE"; then
        check_core_service "$SERVICE" "$COMMAND"
        exit $?
      fi

      cd ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}
      docker-compose restart -d 2>> ${DATA_LOCATION}/ebiokit-logs/error.log >> ${DATA_LOCATION}/ebiokit-logs/services.log
  elif [[ "$COMMAND" == "service_log" ]]; then
      LINES=$3
      SERVICE=$4
      DATA_LOCATION=$5

      if is_core_service "$SERVICE"; then
        check_core_service "$SERVICE" "$COMMAND" $LINES
        exit $?
      fi
      cd ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}
      docker-compose logs | tail -$LINES
  elif [[ "$COMMAND" == "service_rm" ]]; then
      SERVICE=$3
      DATA_LOCATION=$4

      if is_core_service "$SERVICE"; then
        echo "Not a valid option. Aborting."
        exit 1
      fi

      cd ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}
      docker-compose rm -f  2>> ${DATA_LOCATION}/ebiokit-logs/error.log >> ${DATA_LOCATION}/ebiokit-logs/services.log
  elif [[ "$COMMAND" == "service_rmi" ]]; then
      SERVICE=$3
      DATA_LOCATION=$4

      if is_core_service "$SERVICE"; then
        echo "Not a valid option. Aborting."
        exit 1
      fi

      cd ${DATA_LOCATION}/ebiokit-services/launchers/${SERVICE}
      docker-compose down --rmi all 2>> ${DATA_LOCATION}/ebiokit-logs/error.log >> ${DATA_LOCATION}/ebiokit-logs/services.log
  else
      echo "Unknown option "
      exit 1
  fi
}


is_core_service() {
  CORE_SERVICES="ebiokit-web ebiokit-queue docker-engine"
  [[ $CORE_SERVICES =~ (^|[[:space:]])$1($|[[:space:]]) ]] && return 0 || return 1
}


check_core_service(){
  SERVICE=$1
  COMMAND=$2

  if is_core_service "$SERVICE"; then
    if [[ "$COMMAND" == "service_status" ]]; then
      if [[ "$SERVICE" == "ebiokit-web" ]]; then
        # First check the status for NGINX service
        if [[ "$PLATFORM" == "LINUX" ]]; then
          sudo service nginx status > /dev/null
          if [[ "$?" == "0" ]]; then
            django_status="running"
          elif [[ "$?" == "3" ]]; then
            django_status="stopped"
          fi
        elif [[ "$PLATFORM" == "OSX" ]]; then
          nginx_status=$(sudo brew services list | grep nginx | cut -f2 -d" ")
        fi

        # Now check the status for Django service (UWSGI)
        if [ -f /tmp/ebiokit.pid ]; then
          ps -A | grep  `cat /tmp/ebiokit.pid` | head -1 | grep uwsgi.ini > /dev/null
          if [[ "$?" == "1" ]]; then
            django_status="stopped";
          fi
        else
          django_status="stopped";
        fi
        # Based on the status for both services, return the final status
        if [[ "$nginx_status" == "started" ]] && [[ "$django_status" != "stopped" ]]; then
          echo "RUNNING";
        elif [[ "$nginx_status" == "stopped" ]] && [[ "$django_status" == "stopped" ]]; then
          echo "STOPPED";
        elif [[ "$nginx_status" == "started" ]] && [[ "$django_status" == "stopped" ]]; then
          echo "WARNING"
          echo "NGINX service is running but Django seems to be stopped. Please restart the service." >&2
        elif [[ "$nginx_status" == "stopped" ]] && [[ "$django_status" != "stopped" ]]; then
          echo "WARNING"
          echo "Django service is running but NGINX seems to be stopped. Please restart the service." >&2
        else
          echo "WARNING"
          echo ${nginx_status} >&2
        fi
      elif [[ "$SERVICE" == "ebiokit-queue" ]]; then
        # Get the status for the queue based on the status of UWSGI
        if [ -f /tmp/ebiokit_queue.pid ]; then
          ps -A | grep  `cat /tmp/ebiokit_queue.pid` | head -1 | grep queue_uwsgi.ini > /dev/null
          status=$?
        fi
        if [[ "$status" == "0" ]]; then
           echo "RUNNING";
        else
           echo "STOPPED";
        fi
      elif [[ "$SERVICE" == "docker-engine" ]]; then
        sudo docker ps &> /dev/null
          status=$?
          if [[ "$status" == "0" ]]; then
             echo "RUNNING";
          else
             echo "STOPPED";
          fi
      fi
    elif [[ "$COMMAND" == "service_stop" ]]; then
        if [[ "$SERVICE" == "ebiokit-web" ]]; then
          if [[ "$PLATFORM" == "LINUX" ]]; then
            sudo service nginx stop
          elif [[ "$PLATFORM" == "OSX" ]]; then
            sudo brew services stop nginx
          fi
          sudo kill -9 `cat /tmp/ebiokit.pid`
          sudo rm /tmp/ebiokit.*
        elif [[ "$SERVICE" == "ebiokit-queue" ]]; then
          sudo kill -9 `cat /tmp/ebiokit_queue.pid`
          sudo rm /tmp/ebiokit_queue.*
        elif [[ "$SERVICE" == "docker-engine" ]]; then
          ebservice all stop
          if [[ "$PLATFORM" == "LINUX" ]]; then
            sudo service docker stop
          elif [[ "$PLATFORM" == "OSX" ]]; then
            sudo killall Docker
          fi
        fi
    elif [[ "$COMMAND" == "service_start" ]]; then
      if [[ "$SERVICE" == "ebiokit-web" ]]; then
        ebservice $SERVICE stop
        if [[ "$PLATFORM" == "LINUX" ]]; then
          sudo service nginx start
        elif [[ "$PLATFORM" == "OSX" ]]; then
          sudo brew services start nginx
        fi
        cd /data/ebiokit-data/nginx
        sudo uwsgi --ini uwsgi.ini
      elif [[ "$SERVICE" == "ebiokit-queue" ]]; then
        ebservice $SERVICE stop
        cd /data/ebiokit-data/nginx
        sudo uwsgi --ini queue_uwsgi.ini --enable-threads
      elif [[ "$SERVICE" == "docker-engine" ]]; then
        if [[ "$PLATFORM" == "LINUX" ]]; then
          sudo service docker start
        elif [[ "$PLATFORM" == "OSX" ]]; then
          open /Applications/Docker.app
        fi
      fi
    elif [[ "$COMMAND" == "service_restart" ]]; then
      ebservice $SERVICE stop
      ebservice $SERVICE start
    elif [[ "$COMMAND" == "service_log" ]]; then
      if [[ "$SERVICE" == "ebiokit-web" ]]; then
        echo "Unable to show the log for the web."
        if [[ "$PLATFORM" == "LINUX" ]]; then
          echo "You can find the complete log for this service at /var/log/nginx/ and at /var/log/uwsgi/ebiokit.log"
        elif [[ "$PLATFORM" == "OSX" ]]; then
          echo "You can find the complete log for this service at /usr/local/var/log/nginx/ and at /usr/local/var/log/uwsgi/ebiokit.log"
        fi
      elif [[ "$SERVICE" == "ebiokit-queue" ]]; then
        echo "Unable to show the log for the queue."
        if [[ "$PLATFORM" == "LINUX" ]]; then
          echo "You can find the complete log for this service at /var/log/uwsgi/ebiokit_queue.log"
        elif [[ "$PLATFORM" == "OSX" ]]; then
          echo "You can find the complete log for this service at /usr/local/var/log/uwsgi/ebiokit_queue.log"
        fi
      elif [[ "$SERVICE" == "docker-engine" ]]; then
        if [[ "$PLATFORM" == "LINUX" ]]; then
          echo "You can find the complete log for this service executing 'journalctl -u docker.service'"
        elif [[ "$PLATFORM" == "OSX" ]]; then
          echo "You can find the complete log for this service executing the following commands:"
          echo "pred='process matches \".*(ocker|vpnkit).*\" || (process in {\"taskgated-helper\", \"launchservicesd\", \"kernel\"} && eventMessage contains[c] \"docker\")' && /usr/bin/log stream --style syslog --level=debug --color=always --predicate \"\$pred\""
        fi
      fi
    else
      echo "Unknown option"
      return 1
    fi
  else
    echo "Unknown service"
    return 1
  fi
}

main $@
