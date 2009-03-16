#!/usr/bin/env python

from circuits import Component, Debugger
from circuits.lib.sockets import TCPClient, Connect
from circuits.lib.irc import IRC, Message, User, Nick

class Bot(Component):

    def __init__(self, host, port=6667, channel=None):
        super(Bot, self).__init__(channel=channel)
        self += TCPClient(channel=channel) + IRC(channel=channel)
        self.push(Connect(host, port), "connect")

    def connected(self, host, port):
        self.push(User("test", host, host, "Test Bot"), "USER")
        self.push(Nick("test"), "NICK")

    def numeric(self, source, target, numeric, args, message):
        if numeric == 433:
            self.push(Nick("%s_" % self("getNick")), "NICK")

    def message(self, source, target, message):
        self.push(Message(source[0], message), "PRIVMSG")

bot = Bot("irc.freenode.net", channel="bot") + Debugger()
bot.run()
