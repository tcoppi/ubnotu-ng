#!/usr/bin/env python2.6

import irclib
import optparse
import sys
import datetime
import time
import binascii
import hashlib

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
            print datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + str(level) + " ",

            print msg

    def __init__(self, options):
        self.options = options
        self.pprint("Starting ubnotu-ng...")

    def run(self):
        #connect

        self.pprint("Connecting to IRC server %s" % self.options.server)
        self.irc = irclib.IRC()
        self.factchar = '!'
        self.cmdchar = '@'
        self.rand = open("/dev/urandom", "r")
        self.identified = {} # maps nicks to names of users:capability they are identified for

        try:
            self.c = self.irc.server().connect(server = self.options.server,
                    port = int(self.options.port), nickname = self.options.nick,
                    username = self.options.ident, ircname =
                    self.options.rname, ssl=self.options.ssl)
        except irclib.ServerConnectionError, x:
            self.pprint(x)
            sys.exit(-1)

        self.c.add_global_handler("welcome", self.on_connect)
        self.c.add_global_handler("privmsg", self.on_privmsg)
        self.c.add_global_handler("pubmsg", self.on_pubmsg)

        #point of no return
        self.pprint("Going into the rabbit hole", level=1)

        try:
            self.irc.process_forever()
        except KeyboardInterrupt:
            self.quit("Keyboard Interrupt")
            sys.exit(-1)

        self.pprint("Shouldn't ever happen.... something is wrong")

    def quit(self, msg):
        self.c.quit(message=msg)
        self.c.close()

    #implements rate limiting and such TODO
    def msg(self, target, msg):
        self.c.privmsg(target, msg)

    #Event Handlers
    def on_connect(self, c, event):
        self.pprint("Connection Successful!")
        map(c.join, self.options.channels.split(","))

    #messages said in PM
    def on_privmsg(self, c, eventlist):
        self.on_pubmsg(c, eventlist, ispubmsg=False)

    #messages said in a public channel
    def on_pubmsg(self, c, eventlist, ispubmsg=True):
        arg = eventlist.arguments()[0]

        nick = irclib.nm_to_n(eventlist.source())
        user = irclib.nm_to_u(eventlist.source())
        host = irclib.nm_to_h(eventlist.source())

        if arg[0] == self.cmdchar:
            cmd = arg[1:].split(' ')[0]

            info = {
                    "nick": nick,
                    "user": user,
                    "host": host,
                    "pubmsg": ispubmsg,
                    "target": eventlist.target(),
                    "source": eventlist.source(),
                    "args": arg[1:].split(' ')[1:]
                    }

            builtins = {
                        "register": self.cmd_register,
                        "identify": self.cmd_identify,
                        "seen": self.cmd_seen
                       }

            builtins.get(cmd, self.dispatch)(info)

        #update the seen database
        seen = open("Seen.db", "r")

        lines = []
        updated = False

        for line in seen.read().split('\n'):
            parsed = line.split(',')

            if parsed[0] == eventlist.target():
                if parsed[1] == nick:
                    t = datetime.datetime.now()

                    nline = eventlist.target() + "," + nick + "," + \
                    str(time.mktime(t.timetuple()) + 1e-6*t.microsecond) + "," + "<" \
                    + nick + "> " + arg

                    updated = True


            if updated is True:
                lines.append(nline)
            else:
                lines.append(line)

        if updated is False:
            #add a new line
            t = datetime.datetime.now()
            nline = eventlist.target() + "," + nick + "," + str(time.mktime(t.timetuple()) +
                    1e-6*t.microsecond) + "," + "<" + nick + "> " + arg

            lines.append(nline)

        seen.close()

        #Yes this is not the most efficient way to do this by far, but
        #everything is in memory so I defy someone to come up with a way that
        #is significantly faster in practice
        seen = open("Seen.db", "w")
        seen.writelines(lines)
        seen.close()

    def cmd_register(self, info):

        passwd = open("passwd", "rw+")

        if info['pubmsg'] is True:
            self.msg(info['target'], "Registration only works in PM.")
            return

        self.pprint("Registering a new user.", level=1)

        #check that the username doesn't already exist
        for line in passwd.read().split('\n'):
            if info['args'][0] == line.split(':')[0]:
                self.pprint(info['nick'] + " is trying to register username " \
                + info['args'][0] + ", but it already exists.")
                self.msg(info['nick'], "Username already exists.")
                return

        #create our salt
        salt = self.rand.read(16)

        hash = hashlib.sha256(salt + info['args'][1]).hexdigest()

        outstring = info['args'][0] + ":" + binascii.hexlify(salt) + "|" + hash \
                + "/" + "USER"

        passwd.write(outstring + "\n")

        self.msg(info['nick'], "Registration successful!")
        self.pprint(info['nick'] + " registered new user " + info['args'][0])

        passwd.close()

    def cmd_identify(self, info):
        passwd = open("passwd", "rw+")

        if info['pubmsg'] is True:
            self.msg(info['target'], "Identifying only works in PM.")
            return

        self.pprint("Identifying a user.", level=1)

        #check for the username
        for line in passwd.read().split('\n'):
            if info['args'][0] == line.split(':')[0]:
                rest = line.split(':')[1].split('|')
                salt = binascii.unhexlify(rest[0])
                hash = rest[1].split('/')[0]
                cap = rest[1].split('/')[1]

                hashed = hashlib.sha256(salt + info['args'][1]).hexdigest()

                if hashed == hash:
                    self.msg(info['nick'], "Identification OK")
                    self.pprint(info['nick'] + " successfully identified for \
user " + info['args'][0])

                    #mark nick as identified for user
                    self.identified.setdefault(info['nick'])
                    self.identified[info['nick']] = info['args'][0] + ":" + cap
                else:
                    self.msg(info['nick'], "Identification FAILED")
                    self.pprint(info['nick'] + " FAILED to identify for user "
                            + info['args'][0])

        passwd.close()

    def cmd_seen(self, info):
        #supybot format Seen.db
        seen = open("Seen.db", "r")

        found = False

        #take different arguments if it is sent to a channel or in PM
        if info['target'][0] == '#':
            for line in seen.read().split('\n'):
                parsed = line.split(',')

                if parsed[0] == info['target']:
                    if parsed[1] == info['args'][0]:

                        #calculate the time
                        a = datetime.datetime.fromtimestamp(float(parsed[2]))

                        diff = datetime.datetime.now() - a

                        self.msg(info['target'], info['nick'] + ": " + \
                                info['args'][0] + " was last seen in " + \
                                info['target'] + " " + str(diff) + " ago: " + parsed[-1])

                        found = True

        if found is False:
            self.msg(info['target'], info['nick'] + ": I have not seen " +
                    info['args'][0])

        seen.close()

    def dispatch(self, info):
        self.pprint("Not builtin command, dispatching to plugins.", level=1)

if __name__ == "__main__":
    opts, args = opt.parse_args()
    bot = ubnotu_ng(opts)

    bot.run()

