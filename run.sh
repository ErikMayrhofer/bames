#!/bin/bash

PYTHONPATH=$(dirname $(readlink -f $0)) python $1
