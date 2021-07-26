!/bin/bash

APP=$1
shift
PYTHONPATH=$(dirname $(readlink -f $0)) python ${APP} $@
