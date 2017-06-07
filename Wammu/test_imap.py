# -*- coding: UTF-8 -*-
#
# Copyright © 2003 - 2017 Michal Čihař <michal@cihar.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# vim: expandtab sw=4 ts=4 sts=4:

from __future__ import unicode_literals

from unittest import TestCase
from Wammu.IMAP import decoder, encoder

TEST = 'Příšerně žluťoučký kůň úpěl ďábelské ódy'


class IMAPTest(TestCase):
    def test_encode(self):
        self.assertEqual(
            ('P&AVkA7QFh-ern&ARs- &AX4-lu&AWU-ou&AQ0-k&AP0- k&AW8BSA- &APo-p&ARs-l &AQ8A4Q-belsk&AOk- &APM-dy', 40),
            encoder(TEST)
        )

    def test_decode(self):
        self.assertEqual(
            TEST,
            decoder(encoder(TEST)[0])[0]
        )

    def test_codec(self):
        self.assertEqual(
            TEST,
            TEST.encode('imap4-utf-7').decode('imap4-utf-7')
        )
