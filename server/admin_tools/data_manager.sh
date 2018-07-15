#!/bin/bash

COMMAND=$1

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

if [[ "$COMMAND" == "combine" ]]; then
    DESTINATION=$2
    CHUNKS_PREFIX=$3
    cat ${CHUNKS_PREFIX}.*_* > ${DESTINATION}
elif [[ "$COMMAND" == "extract" ]]; then
    DESTINATION=$2
    ORIGIN=$3
    COMPRESSED_FILE=$4
    docker run -it --rm -v ${ORIGIN}:/in -v ${DESTINATION}:/out ebiokit/ultraextract extract ${COMPRESSED_FILE}
fi
