#!/usr/bin/env python2.6

import irclib
import optparse
import sys

opt = optparse.OptionParser()

opt.add_option("-s", "--server", dest="server", default="localhost",
        help="Server to connect to")
opt.add_option("-p", "--port", dest="port", default="6667",
        help="Port to connect to on the server")
opt.add_option("", "--ssl", dest="ssl", action="store_true", default=False,
        help="Use SSL or not")
opt.add_option("-n", "--nickname", dest="nick", default="testbot", help="Bot \
nickname")
opt.add_option("-i", "--ident", dest="ident", default="test", help="Bot ident")
opt.add_option("-r", "--realname", dest="rname", default="ubnotu IRC Bot",
        help="Bot real name")
opt.add_option("-j", "--nickservpass", dest="npass", default="", help="Bot \
nickserv password")
opt.add_option("-v", "--verbose", dest="verbosity", action="count", default=0)
opt.add_option("", "--channels", dest="channels", default="", help="Comma \
separated list of channels to join")

class ubnotu_ng:
    def pprint(self, msg, level=0):
        """ Print a message if the specified level is at least the level of
        verbosity. Levels of 0 are always printed. """
        if(level <= self.options.verbosity):
            print msg

    def __init__(self, options):
        self.options = options
        self.pprint("Starting ubnotu-ng...")

    def run(self):
        #connect

        self.pprint("Connecting to IRC server %s" % self.options.server)
        self.irc = irclib.IRC()

        try:
            self.c = self.irc.server().connect(server = self.options.server,
                    port = int(self.options.port), nickname = self.options.nick,
                    username = self.options.ident, ircname =
                    self.options.rname, ssl=self.options.ssl)
        except irclib.ServerConnectionError, x:
            self.pprint(x)
            sys.exit(-1)

        self.pprint("Connection Successful!")

        for c in self.options.channels.split(","):
            self.c.join(c)

        #point of no return
        self.pprint("Going into the rabbit hole", level=1)
        self.irc.process_forever()
        self.pprint("Shouldn't ever happen.... something is wrong")

if __name__ == "__main__":
    opts, args = opt.parse_args()
    bot = ubnotu_ng(opts)

    bot.run()

