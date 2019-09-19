#!/bin/bash

COMMAND=${1}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

if [[ "$COMMAND" == "combine" ]]; then
    DESTINATION=${2}
    CHUNKS_PREFIX=${3}
    cat ${CHUNKS_PREFIX}.*_* > ${DESTINATION}
elif [[ "$COMMAND" == "extract" ]]; then
    DESTINATION=${2}
    ORIGIN=${3}
    COMPRESSED_FILE=${4}
    docker run --rm -v ${ORIGIN}:/in -v ${DESTINATION}:/out ebiokit/ultraextract extract ${COMPRESSED_FILE} > /tmp/extract.o 2> /tmp/extract.e
elif [[ "$COMMAND" == "remove" ]]; then
      PARENT_DIR=$(cd ${2}/../../; pwd)
      TARGET=$(basename ${2})

      parent_name=$(basename $PARENT_DIR)
      if [[ "$parent_name" == "ebiokit_components" ]]; then
        docker run -it --rm -v ${PARENT_DIR}:/in ebiokit/ultraextract remove ebiokit-data/${TARGET}
      else
        echo "Invalid path. Unable to remove directory."
        exit 1
      fi
fi
