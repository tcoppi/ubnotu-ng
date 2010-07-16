#!/bin/sh
#Designed to be run from the toplevel source directory

PYTHONPATH="$PWD:$PYTHONPATH"

#configuration variables

SERVER="irc.freenode.net"
PORT="7000"
SSL="on"
NICK="ubnotung"
IDENT="ubnotu"
REALNAME="ubnotu-ng"
NICKSERVPASS="urmom"

`$PWD/ubnotu.py --server $SERVER --port $PORT --ssl $SSL --nick $NICK \
--ident $IDENT --realname $REALNAME --nickservepass = $NICKSERVPASS`
