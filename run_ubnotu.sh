#!/bin/sh
#Designed to be run from the toplevel source directory

PYTHONPATH="$PWD:$PYTHONPATH"

#configuration variables

SERVER="irc.freenode.net"
PORT="7000"
SSL="--ssl"
NICK="ubnotung"
IDENT="ubnotu"
REALNAME="ubnotu-ng"
NICKSERVPASS="urmom"
CHANNELS="#ubnotu-ng"

$PWD/ubnotu.py --server $SERVER --port $PORT $SSL --nickname $NICK \
--ident $IDENT --realname $REALNAME --nickservpass = $NICKSERVPASS \
--channels $CHANNELS
