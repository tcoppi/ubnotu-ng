#!/usr/bin/env python2.6

import irclib
import optparse

opt = optparse.OptionParser()

opt.add_option("-s", "--server", dest="server", default="localhost",
        help="Server to connect to")
opt.add_option("-p", "--port", dest="port", default="6667",
        help="Port to connect to on the server")
opt.add_option("", "--ssl", dest="ssl", default="off", help="Use SSL or not")
opt.add_option("-n", "--nickname", dest="nick", default="testbot", help="Bot \
        nickname")
opt.add_option("-i", "--ident", dest="ident", default="test", help="Bot ident")
opt.add_option("-r", "--realname", dest="rname", default="ubnotu IRC Bot",
        help="Bot real name")
opt.add_option("-j", "--nickservpass", dest="npass", default="", help="Bot \
        nickserv password")
opt.add_option("-v", "--verbose", dest="verbosity", action="count", default=0)

opts, args = opt.parse_args()

