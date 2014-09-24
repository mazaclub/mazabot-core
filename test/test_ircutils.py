###
# Copyright (c) 2002-2005, Jeremiah Fincher
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###


from supybot.test import *

import copy
import random

import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils

# The test framework used to provide these, but not it doesn't.  We'll add
# messages to as we find bugs (if indeed we find bugs).
msgs = []
rawmsgs = []

class FunctionsTestCase(SupyTestCase):
    hostmask = 'foo!bar@baz'
    def testHostmaskPatternEqual(self):
        for msg in msgs:
            if msg.prefix and ircutils.isUserHostmask(msg.prefix):
                s = msg.prefix
                self.failUnless(ircutils.hostmaskPatternEqual(s, s),
                                '%r did not match itself.' % s)
                banmask = ircutils.banmask(s)
                self.failUnless(ircutils.hostmaskPatternEqual(banmask, s),
                                '%r did not match %r' % (s, banmask))
        s = 'supybot!~supybot@dhcp065-024-075-056.columbus.rr.com'
        self.failUnless(ircutils.hostmaskPatternEqual(s, s))
        s = 'jamessan|work!~jamessan@209-6-166-196.c3-0.' \
            'abr-ubr1.sbo-abr.ma.cable.rcn.com'
        self.failUnless(ircutils.hostmaskPatternEqual(s, s))

    def testIsUserHostmask(self):
        self.failUnless(ircutils.isUserHostmask(self.hostmask))
        self.failUnless(ircutils.isUserHostmask('a!b@c'))
        self.failIf(ircutils.isUserHostmask('!bar@baz'))
        self.failIf(ircutils.isUserHostmask('!@baz'))
        self.failIf(ircutils.isUserHostmask('!bar@'))
        self.failIf(ircutils.isUserHostmask('!@'))
        self.failIf(ircutils.isUserHostmask('foo!@baz'))
        self.failIf(ircutils.isUserHostmask('foo!bar@'))
        self.failIf(ircutils.isUserHostmask(''))
        self.failIf(ircutils.isUserHostmask('!'))
        self.failIf(ircutils.isUserHostmask('@'))
        self.failIf(ircutils.isUserHostmask('!bar@baz'))

    def testIsChannel(self):
        self.failUnless(ircutils.isChannel('#'))
        self.failUnless(ircutils.isChannel('&'))
        self.failUnless(ircutils.isChannel('+'))
        self.failUnless(ircutils.isChannel('!'))
        self.failUnless(ircutils.isChannel('#foo'))
        self.failUnless(ircutils.isChannel('&foo'))
        self.failUnless(ircutils.isChannel('+foo'))
        self.failUnless(ircutils.isChannel('!foo'))
        self.failIf(ircutils.isChannel('#foo bar'))
        self.failIf(ircutils.isChannel('#foo,bar'))
        self.failIf(ircutils.isChannel('#foobar\x07'))
        self.failIf(ircutils.isChannel('foo'))
        self.failIf(ircutils.isChannel(''))

    def testBold(self):
        s = ircutils.bold('foo')
        self.assertEqual(s[0], '\x02')
        self.assertEqual(s[-1], '\x02')

    def testUnderline(self):
        s = ircutils.underline('foo')
        self.assertEqual(s[0], '\x1f')
        self.assertEqual(s[-1], '\x1f')

    def testReverse(self):
        s = ircutils.reverse('foo')
        self.assertEqual(s[0], '\x16')
        self.assertEqual(s[-1], '\x16')

    def testMircColor(self):
        # No colors provided should return the same string
        s = 'foo'
        self.assertEqual(s, ircutils.mircColor(s))
        # Test positional args
        self.assertEqual('\x0300foo\x03', ircutils.mircColor(s, 'white'))
        self.assertEqual('\x031,02foo\x03',ircutils.mircColor(s,'black','blue'))
        self.assertEqual('\x0300,03foo\x03', ircutils.mircColor(s, None, 'green'))
        # Test keyword args
        self.assertEqual('\x0304foo\x03', ircutils.mircColor(s, fg='red'))
        self.assertEqual('\x0300,05foo\x03', ircutils.mircColor(s, bg='brown'))
        self.assertEqual('\x036,07foo\x03',
                         ircutils.mircColor(s, bg='orange', fg='purple'))

# Commented out because we don't map numbers to colors anymore.
##     def testMircColors(self):
##         # Make sure all (k, v) pairs are also (v, k) pairs.
##         for (k, v) in ircutils.mircColors.items():
##             if k:
##                 self.assertEqual(ircutils.mircColors[v], k)

    def testStripBold(self):
        self.assertEqual(ircutils.stripBold(ircutils.bold('foo')), 'foo')

    def testStripColor(self):
        self.assertEqual(ircutils.stripColor('\x02bold\x0302,04foo\x03bar\x0f'),
                         '\x02boldfoobar\x0f')
        self.assertEqual(ircutils.stripColor('\x03foo\x03'), 'foo')
        self.assertEqual(ircutils.stripColor('\x03foo\x0F'), 'foo\x0F')
        self.assertEqual(ircutils.stripColor('\x0312foo\x03'), 'foo')
        self.assertEqual(ircutils.stripColor('\x0312,14foo\x03'), 'foo')
        self.assertEqual(ircutils.stripColor('\x03,14foo\x03'), 'foo')
        self.assertEqual(ircutils.stripColor('\x03,foo\x03'), ',foo')
        self.assertEqual(ircutils.stripColor('\x0312foo\x0F'), 'foo\x0F')
        self.assertEqual(ircutils.stripColor('\x0312,14foo\x0F'), 'foo\x0F')
        self.assertEqual(ircutils.stripColor('\x03,14foo\x0F'), 'foo\x0F')
        self.assertEqual(ircutils.stripColor('\x03,foo\x0F'), ',foo\x0F')

    def testStripReverse(self):
        self.assertEqual(ircutils.stripReverse(ircutils.reverse('foo')), 'foo')

    def testStripUnderline(self):
        self.assertEqual(ircutils.stripUnderline(ircutils.underline('foo')),
                         'foo')

    def testStripFormatting(self):
        self.assertEqual(ircutils.stripFormatting(ircutils.bold('foo')), 'foo')
        self.assertEqual(ircutils.stripFormatting(ircutils.reverse('foo')),
                         'foo')
        self.assertEqual(ircutils.stripFormatting(ircutils.underline('foo')),
                         'foo')
        self.assertEqual(ircutils.stripFormatting('\x02bold\x0302,04foo\x03'
                                                  'bar\x0f'),
                         'boldfoobar')
        s = ircutils.mircColor('[', 'blue') + ircutils.bold('09:21')
        self.assertEqual(ircutils.stripFormatting(s), '[09:21')

    def testSafeArgument(self):
        s = 'I have been running for 9 seconds'
        bolds = ircutils.bold(s)
        colors = ircutils.mircColor(s, 'pink', 'orange')
        self.assertEqual(s, ircutils.safeArgument(s))
        self.assertEqual(bolds, ircutils.safeArgument(bolds))
        self.assertEqual(colors, ircutils.safeArgument(colors))

    def testSafeArgumentConvertsToString(self):
        self.assertEqual('1', ircutils.safeArgument(1))
        self.assertEqual(str(None), ircutils.safeArgument(None))

    def testIsNick(self):
        try:
            original = conf.supybot.protocols.irc.strictRfc()
            conf.supybot.protocols.irc.strictRfc.setValue(True)
            self.failUnless(ircutils.isNick('jemfinch'))
            self.failUnless(ircutils.isNick('jemfinch0'))
            self.failUnless(ircutils.isNick('[0]'))
            self.failUnless(ircutils.isNick('{jemfinch}'))
            self.failUnless(ircutils.isNick('[jemfinch]'))
            self.failUnless(ircutils.isNick('jem|finch'))
            self.failUnless(ircutils.isNick('\\```'))
            self.failUnless(ircutils.isNick('`'))
            self.failUnless(ircutils.isNick('A'))
            self.failIf(ircutils.isNick(''))
            self.failIf(ircutils.isNick('8foo'))
            self.failIf(ircutils.isNick('10'))
            self.failIf(ircutils.isNick('-'))
            self.failIf(ircutils.isNick('-foo'))
            conf.supybot.protocols.irc.strictRfc.setValue(False)
            self.failUnless(ircutils.isNick('services@something.undernet.net'))
        finally:
            conf.supybot.protocols.irc.strictRfc.setValue(original)

    def testIsNickNeverAllowsSpaces(self):
        try:
            original = conf.supybot.protocols.irc.strictRfc()
            conf.supybot.protocols.irc.strictRfc.setValue(True)
            self.failIf(ircutils.isNick('foo bar'))
            conf.supybot.protocols.irc.strictRfc.setValue(False)
            self.failIf(ircutils.isNick('foo bar'))
        finally:
            conf.supybot.protocols.irc.strictRfc.setValue(original)

    def testStandardSubstitute(self):
        # Stub out random msg and irc objects that provide what
        # standardSubstitute wants
        msg = ircmsgs.IrcMsg(':%s PRIVMSG #channel :stuff' % self.hostmask)
        class Irc(object):
            nick = 'bob'
        irc = Irc()

        f = ircutils.standardSubstitute
        vars = {'foo': 'bar', 'b': 'c', 'i': 100,
                'f': lambda: 'called'}
        self.assertEqual(f(irc, msg, '$foo', vars), 'bar')
        self.assertEqual(f(irc, msg, '${foo}', vars), 'bar')
        self.assertEqual(f(irc, msg, '$b', vars), 'c')
        self.assertEqual(f(irc, msg, '${b}', vars), 'c')
        self.assertEqual(f(irc, msg, '$i', vars), '100')
        self.assertEqual(f(irc, msg, '${i}', vars), '100')
        self.assertEqual(f(irc, msg, '$f', vars), 'called')
        self.assertEqual(f(irc, msg, '${f}', vars), 'called')
        self.assertEqual(f(irc, msg, '$b:$i', vars), 'c:100')

    def testBanmask(self):
        for msg in msgs:
            if ircutils.isUserHostmask(msg.prefix):
                banmask = ircutils.banmask(msg.prefix)
                self.failUnless(ircutils.hostmaskPatternEqual(banmask,
                                                              msg.prefix),
                                '%r didn\'t match %r' % (msg.prefix, banmask))
        self.assertEqual(ircutils.banmask('foobar!user@host'), '*!*@host')
        self.assertEqual(ircutils.banmask('foobar!user@host.tld'),
                         '*!*@host.tld')
        self.assertEqual(ircutils.banmask('foobar!user@sub.host.tld'),
                         '*!*@*.host.tld')
        self.assertEqual(ircutils.banmask('foo!bar@2001::'), '*!*@2001::*')

    def testSeparateModes(self):
        self.assertEqual(ircutils.separateModes(['+ooo', 'x', 'y', 'z']),
                         [('+o', 'x'), ('+o', 'y'), ('+o', 'z')])
        self.assertEqual(ircutils.separateModes(['+o-o', 'x', 'y']),
                         [('+o', 'x'), ('-o', 'y')])
        self.assertEqual(ircutils.separateModes(['+s-o', 'x']),
                         [('+s', None), ('-o', 'x')])
        self.assertEqual(ircutils.separateModes(['+sntl', '100']),
                        [('+s', None),('+n', None),('+t', None),('+l', 100)])

    def testNickFromHostmask(self):
        self.assertEqual(ircutils.nickFromHostmask('nick!user@host.domain.tld'),
                         'nick')

    def testToLower(self):
        self.assertEqual('jemfinch', ircutils.toLower('jemfinch'))
        self.assertEqual('{}|^', ircutils.toLower('[]\\~'))

    def testReplyTo(self):
        prefix = 'foo!bar@baz'
        channel = ircmsgs.privmsg('#foo', 'bar baz', prefix=prefix)
        private = ircmsgs.privmsg('jemfinch', 'bar baz', prefix=prefix)
        self.assertEqual(ircutils.replyTo(channel), channel.args[0])
        self.assertEqual(ircutils.replyTo(private), private.nick)

    def testJoinModes(self):
        plusE = ('+e', '*!*@*ohio-state.edu')
        plusB = ('+b', '*!*@*umich.edu')
        minusL = ('-l', None)
        modes = [plusB, plusE, minusL]
        self.assertEqual(ircutils.joinModes(modes),
                         ['+be-l', plusB[1], plusE[1]])

    def testDccIpStuff(self):
        def randomIP():
            def rand():
                return random.randrange(0, 256)
            return '.'.join(map(str, [rand(), rand(), rand(), rand()]))
        for _ in range(100): # 100 should be good :)
            ip = randomIP()
            self.assertEqual(ip, ircutils.unDccIP(ircutils.dccIP(ip)))


class IrcDictTestCase(SupyTestCase):
    def test(self):
        d = ircutils.IrcDict()
        d['#FOO'] = 'bar'
        self.assertEqual(d['#FOO'], 'bar')
        self.assertEqual(d['#Foo'], 'bar')
        self.assertEqual(d['#foo'], 'bar')
        del d['#fOO']
        d['jemfinch{}'] = 'bar'
        self.assertEqual(d['jemfinch{}'], 'bar')
        self.assertEqual(d['jemfinch[]'], 'bar')
        self.assertEqual(d['JEMFINCH[]'], 'bar')

    def testKeys(self):
        d = ircutils.IrcDict()
        self.assertEqual(d.keys(), [])

    def testSetdefault(self):
        d = ircutils.IrcDict()
        d.setdefault('#FOO', []).append(1)
        self.assertEqual(d['#foo'], [1])
        self.assertEqual(d['#fOO'], [1])
        self.assertEqual(d['#FOO'], [1])

    def testGet(self):
        d = ircutils.IrcDict()
        self.assertEqual(d.get('#FOO'), None)
        d['#foo'] = 1
        self.assertEqual(d.get('#FOO'), 1)

    def testContains(self):
        d = ircutils.IrcDict()
        d['#FOO'] = None
        self.failUnless('#foo' in d)
        d['#fOOBAR[]'] = None
        self.failUnless('#foobar{}' in d)

    def testGetSetItem(self):
        d = ircutils.IrcDict()
        d['#FOO'] = 12
        self.assertEqual(12, d['#foo'])
        d['#fOOBAR[]'] = 'blah'
        self.assertEqual('blah', d['#foobar{}'])

    def testCopyable(self):
        d = ircutils.IrcDict()
        d['foo'] = 'bar'
        self.failUnless(d == copy.copy(d))
        self.failUnless(d == copy.deepcopy(d))


class IrcSetTestCase(SupyTestCase):
    def test(self):
        s = ircutils.IrcSet()
        s.add('foo')
        s.add('bar')
        self.failUnless('foo' in s)
        self.failUnless('FOO' in s)
        s.discard('alfkj')
        s.remove('FOo')
        self.failIf('foo' in s)
        self.failIf('FOo' in s)

    def testCopy(self):
        s = ircutils.IrcSet()
        s.add('foo')
        s.add('bar')
        s1 = copy.deepcopy(s)
        self.failUnless('foo' in s)
        self.failUnless('FOO' in s)
        s.discard('alfkj')
        s.remove('FOo')
        self.failIf('foo' in s)
        self.failIf('FOo' in s)
        self.failUnless('foo' in s1)
        self.failUnless('FOO' in s1)
        s1.discard('alfkj')
        s1.remove('FOo')
        self.failIf('foo' in s1)
        self.failIf('FOo' in s1)


class IrcStringTestCase(SupyTestCase):
    def testEquality(self):
        self.assertEqual('#foo', ircutils.IrcString('#foo'))
        self.assertEqual('#foo', ircutils.IrcString('#FOO'))
        self.assertEqual('#FOO', ircutils.IrcString('#foo'))
        self.assertEqual('#FOO', ircutils.IrcString('#FOO'))
        self.assertEqual(hash(ircutils.IrcString('#FOO')),
                         hash(ircutils.IrcString('#foo')))

    def testInequality(self):
        s1 = 'supybot'
        s2 = ircutils.IrcString('Supybot')
        self.failUnless(s1 == s2)
        self.failIf(s1 != s2)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
