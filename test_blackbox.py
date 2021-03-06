#!/usr/bin/python
#
# Black box tests for JT65 stego
#
# Copyright 2014 - Paul Drapeau and Brent Dukes
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest
import random
import os
import string
import copy

import numpy as np
import jt65stego as jts
import jt65sound

MAX_COVER_NOISE = 5
STEG_DETECTION_ERROR_THRESHOLD = 17


class TestText(unittest.TestCase):

    def test_NoCipher_NoSteg(self):
        # Encode
        jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
        jt65data = jts.jt65encodemessages(jt65msgs, False)
        expectedresult = [np.array(
            [39, 19, 16, 44, 29, 13, 58, 19, 13, 14, 20, 44, 17, 20, 25, 31, 46, 2, 29, 35, 56, 17, 11, 20, 39,
             51, 7, 30, 26, 11, 17, 27, 21, 11, 30, 34, 46, 48, 15, 53, 14, 26, 12, 7, 5, 8, 42, 41, 37, 19,
             16, 35, 63, 20, 3, 12, 38, 26, 8, 37, 22, 23, 29]),
            np.array(
                [1, 22, 21, 42, 33, 8, 40, 58, 13, 54, 19, 19, 58, 6, 5, 10, 29, 24, 34, 1, 53, 33, 30, 43, 17,
                    51, 29, 38, 52, 58, 55, 9, 49, 50, 24, 61, 0, 52, 51, 20, 25, 58, 15, 41, 53, 48, 6, 57, 10, 25,
                    11, 30, 16, 20, 47, 6, 0, 43, 6, 18, 38, 3, 29])]
        self.assertEqual(len(expectedresult), len(jt65data))
        for i in range(len(expectedresult)):
            self.assertEqual(jt65data[i].tolist(), expectedresult[i].tolist())
        # Decode
        decodedjt65msgs = jts.decodemessages(jt65data, False)
        self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
        for i in range(len(jt65msgs)):
            self.assertEqual(jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())

    def test_NoCipher_WithSteg(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "BEACON FTW AND DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "none", "", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(stegdata, "none", "", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_NoCipher_WithSteg_Extra(self):
        for i in range(MAX_COVER_NOISE):
            # Encode with more JT65 msgs than necessary
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "BEACON FTW AND DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "none", "", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(stegdata, "none", "", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_XOR_6(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEFCON"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "XOR", "XOR rox and all that jazz", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "XOR", "XOR rox and all that jazz", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_XOR_8(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEFCON22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "XOR", "XOR rox and all that jazz", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "XOR", "XOR rox and all that jazz", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_XOR_10(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "XOR", "XOR rox and all that jazz", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "XOR", "XOR rox and all that jazz", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_XOR_16(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22 VEGAS"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "XOR", "XOR rox and all that jazz", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "XOR", "XOR rox and all that jazz", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_XOR_23(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = [
                "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44", "KB2BBC KA1AAB DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22 VEGAS NEVADA"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "XOR", "XOR rox and all that jazz", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "XOR", "XOR rox and all that jazz", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_XOR_Extra(self):
        for i in range(MAX_COVER_NOISE):
            # Encode with more JT65 msgs than necessary
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "XOR", "XOR rox and all that jazz", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalmsgscopy = copy.deepcopy(finalmsgs)
            jt65stegmsgs = []
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)

            for i in range(len(finalmsgscopy)):
                if jts.validatesteg(decodedjt65msgs[i], finalmsgscopy[i], hidekey, STEG_DETECTION_ERROR_THRESHOLD, False):
                    jt65stegmsgs.append(finalmsgscopy[i])
            stegdata = jts.retrievesteg(jt65stegmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "XOR", "XOR rox and all that jazz", "", False)

            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_ARC4(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "ARC4", "RC4 is the most secure algorithm in the world", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "ARC4", "RC4 is the most secure algorithm in the world", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_ARC4_Extra(self):
        for i in range(MAX_COVER_NOISE):
            # Encode with more JT65 msgs than necessary
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "ARC4", "RC4 is the most secure algorithm in the world", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalmsgscopy = copy.deepcopy(finalmsgs)
            jt65stegmsgs = []
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)

            for i in range(len(finalmsgscopy)):
                if jts.validatesteg(decodedjt65msgs[i], finalmsgscopy[i], hidekey, STEG_DETECTION_ERROR_THRESHOLD, False):
                    jt65stegmsgs.append(finalmsgscopy[i])
            stegdata = jts.retrievesteg(jt65stegmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "ARC4", "RC4 is the most secure algorithm in the world", "", False)

            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_AES_ECB(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "AES", "AES is totes secure, right? Yeah", "", "ECB", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "AES", "AES is totes secure, right? Yeah", "ECB", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_AES_ECB_Extra(self):
        for i in range(MAX_COVER_NOISE):
            # Encode with more JT65 msgs than necessary
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "AES", "AES is totes secure, right? Yeah", "", "ECB", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalmsgscopy = copy.deepcopy(finalmsgs)
            jt65stegmsgs = []
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)

            for i in range(len(finalmsgscopy)):
                if jts.validatesteg(decodedjt65msgs[i], finalmsgscopy[i], hidekey, STEG_DETECTION_ERROR_THRESHOLD, False):
                    jt65stegmsgs.append(finalmsgscopy[i])
            stegdata = jts.retrievesteg(jt65stegmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "AES", "AES is totes secure, right? Yeah", "ECB", False)

            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_AES_CBC(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "AES", "AES is totes secure, right? Yeah", "", "CBC", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "AES", "AES is totes secure, right? Yeah", "CBC", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_AES_CBC_Extra(self):
        for i in range(MAX_COVER_NOISE):
            # Encode with more JT65 msgs than necessary
            jt65msgs = [
                "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44", "KB2BBC KA1AAB DD44",
                "KA1AAB KB2BBC DD44", "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "AES", "AES is totes secure, right? Yeah", "", "CBC", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalmsgscopy = copy.deepcopy(finalmsgs)
            jt65stegmsgs = []
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)

            for i in range(len(finalmsgscopy)):
                if jts.validatesteg(decodedjt65msgs[i], finalmsgscopy[i], hidekey, STEG_DETECTION_ERROR_THRESHOLD, False):
                    jt65stegmsgs.append(finalmsgscopy[i])
            stegdata = jts.retrievesteg(jt65stegmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "AES", "AES is totes secure, right? Yeah", "CBC", False)

            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_AES_CFB(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "AES", "AES is totes secure, right? Yeah", "", "CFB", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "AES", "AES is totes secure, right? Yeah", "CFB", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_AES_CFB_Extra(self):
        for i in range(MAX_COVER_NOISE):
            # Encode with more JT65 msgs than necessary
            jt65msgs = [
                "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44", "KB2BBC KA1AAB DD44",
                "KA1AAB KB2BBC DD44", "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "AES", "AES is totes secure, right? Yeah", "", "CFB", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalmsgscopy = copy.deepcopy(finalmsgs)
            jt65stegmsgs = []
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)

            for i in range(len(finalmsgscopy)):
                if jts.validatesteg(decodedjt65msgs[i], finalmsgscopy[i], hidekey, STEG_DETECTION_ERROR_THRESHOLD, False):
                    jt65stegmsgs.append(finalmsgscopy[i])
            stegdata = jts.retrievesteg(jt65stegmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "AES", "AES is totes secure, right? Yeah", "CFB", False)

            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_OTP(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "BEACON FTW AND DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "OTP", "I LOVE SECURITY AND STUFF", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalresultmsgs = list(finalmsgs)
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "OTP", "I LOVE SECURITY AND STUFF", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_OTP_Extra(self):
        for i in range(MAX_COVER_NOISE):
            # Encode with more JT65 msgs than necessary
            jt65msgs = [
                "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44", "KB2BBC KA1AAB DD44",
                "KA1AAB KB2BBC DD44", "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "BEACON FTW AND DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "OTP", "I LOVE SECURITY AND STUFF", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)

            # Decode
            finalmsgscopy = copy.deepcopy(finalmsgs)
            jt65stegmsgs = []
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)

            for i in range(len(finalmsgscopy)):
                if jts.validatesteg(decodedjt65msgs[i], finalmsgscopy[i], hidekey, STEG_DETECTION_ERROR_THRESHOLD, False):
                    jt65stegmsgs.append(finalmsgscopy[i])
            stegdata = jts.retrievesteg(jt65stegmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "OTP", "I LOVE SECURITY AND STUFF", "", False)

            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

# Separate class since these tests take a long time to run
# You can exclude these tests if necessary


class TestWav(unittest.TestCase):

    def test_NoCipher_NoSteg_WAV(self):
        # Encode
        jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
        jt65data = jts.jt65encodemessages(jt65msgs, False)
        for index, value in enumerate(jt65data):
            tones = jt65sound.toneswithsync(value)
            jt65sound.outputwavfile(
                "test_output-00" + str(index) + ".wav", tones)

        # Decode
        result1 = jt65sound.inputwavfile("test_output-000.wav")
        result2 = jt65sound.inputwavfile("test_output-001.wav")
        symbols1, confidence1, wavmsg1, s2db, freq, a1, a2 = result1[0]
        symbols2, confidence2, wavmsg2, s2db, freq, a1, a2 = result2[0]
        os.remove("test_output-000.wav")
        os.remove("test_output-001.wav")
        resultjt65data = [symbols1, symbols2]
        decodedjt65msgs = jts.decodemessages(resultjt65data, False)
        self.assertEqual(len(result1), 1)
        self.assertEqual(len(result2), 1)
        self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
        for i in range(len(jt65msgs)):
            self.assertEqual(jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())

    def test_NoCipher_WithSteg_WAV(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "BEACON FTW AND DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "none", "", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)
            for index, value in enumerate(finalmsgs):
                tones = jt65sound.toneswithsync(value)
                jt65sound.outputwavfile(
                    "test_output-00" + str(index) + ".wav", tones)

            # Decode
            result1 = jt65sound.inputwavfile("test_output-000.wav")
            result2 = jt65sound.inputwavfile("test_output-001.wav")
            symbols1, confidence1, wavmsg1, s2db, freq, a1, a2 = result1[0]
            symbols2, confidence2, wavmsg2, s2db, freq, a1, a2 = result2[0]
            os.remove("test_output-000.wav")
            os.remove("test_output-001.wav")
            finalresultmsgs = [symbols1, symbols2]
            stegdata = jts.retrievesteg(finalresultmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(stegdata, "none", "", "", False)
            decodedjt65msgs = jts.decodemessages(finalresultmsgs, False)
            self.assertEqual(len(result1), 1)
            self.assertEqual(len(result2), 1)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_XOR_WAV(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "XOR", "XOR rox and all that jazz", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)
            for index, value in enumerate(finalmsgs):
                tones = jt65sound.toneswithsync(value)
                jt65sound.outputwavfile(
                    "test_output-00" + str(index) + ".wav", tones)

            # Decode
            result1 = jt65sound.inputwavfile("test_output-000.wav")
            result2 = jt65sound.inputwavfile("test_output-001.wav")
            symbols1, confidence1, wavmsg1, s2db, freq, a1, a2 = result1[0]
            symbols2, confidence2, wavmsg2, s2db, freq, a1, a2 = result2[0]
            os.remove("test_output-000.wav")
            os.remove("test_output-001.wav")
            finalresultmsgs = [symbols1, symbols2]
            stegdata = jts.retrievesteg(finalresultmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "XOR", "XOR rox and all that jazz", "", False)
            decodedjt65msgs = jts.decodemessages(finalresultmsgs, False)
            self.assertEqual(len(result1), 1)
            self.assertEqual(len(result2), 1)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_ARC4_WAV(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "ARC4", "RC4 is the most secure algorithm in the world", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)
            for index, value in enumerate(finalmsgs):
                tones = jt65sound.toneswithsync(value)
                jt65sound.outputwavfile(
                    "test_output-00" + str(index) + ".wav", tones)

            # Decode
            result1 = jt65sound.inputwavfile("test_output-000.wav")
            result2 = jt65sound.inputwavfile("test_output-001.wav")
            symbols1, confidence1, wavmsg1, s2db, freq, a1, a2 = result1[0]
            symbols2, confidence2, wavmsg2, s2db, freq, a1, a2 = result2[0]
            os.remove("test_output-000.wav")
            os.remove("test_output-001.wav")
            finalresultmsgs = [symbols1, symbols2]
            stegdata = jts.retrievesteg(finalresultmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "ARC4", "RC4 is the most secure algorithm in the world", "", False)
            decodedjt65msgs = jts.decodemessages(finalresultmsgs, False)
            self.assertEqual(len(result1), 1)
            self.assertEqual(len(result2), 1)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_AES_ECB_WAV(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "AES", "AES is totes secure, right? Yeah", "", "ECB", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)
            for index, value in enumerate(finalmsgs):
                tones = jt65sound.toneswithsync(value)
                jt65sound.outputwavfile(
                    "test_output-00" + str(index) + ".wav", tones)

            # Decode
            result1 = jt65sound.inputwavfile("test_output-000.wav")
            result2 = jt65sound.inputwavfile("test_output-001.wav")
            symbols1, confidence1, wavmsg1, s2db, freq, a1, a2 = result1[0]
            symbols2, confidence2, wavmsg2, s2db, freq, a1, a2 = result2[0]
            os.remove("test_output-000.wav")
            os.remove("test_output-001.wav")
            finalresultmsgs = [symbols1, symbols2]
            stegdata = jts.retrievesteg(finalresultmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "AES", "AES is totes secure, right? Yeah", "ECB", False)
            decodedjt65msgs = jts.decodemessages(finalresultmsgs, False)
            self.assertEqual(len(result1), 1)
            self.assertEqual(len(result2), 1)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_AES_CBC_WAV(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "AES", "AES is totes secure, right? Yeah", "", "CBC", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)
            for index, value in enumerate(finalmsgs):
                tones = jt65sound.toneswithsync(value)
                jt65sound.outputwavfile(
                    "test_output-00" + str(index) + ".wav", tones)

            # Decode
            result1 = jt65sound.inputwavfile("test_output-000.wav")
            result2 = jt65sound.inputwavfile("test_output-001.wav")
            result3 = jt65sound.inputwavfile("test_output-002.wav")
            result4 = jt65sound.inputwavfile("test_output-003.wav")
            symbols1, confidence1, wavmsg1, s2db, freq, a1, a2 = result1[0]
            symbols2, confidence2, wavmsg2, s2db, freq, a1, a2 = result2[0]
            symbols3, confidence3, wavmsg3, s2db, freq, a1, a2 = result3[0]
            symbols4, confidence4, wavmsg4, s2db, freq, a1, a2 = result4[0]
            os.remove("test_output-000.wav")
            os.remove("test_output-001.wav")
            os.remove("test_output-002.wav")
            os.remove("test_output-003.wav")
            finalresultmsgs = [symbols1, symbols2, symbols3, symbols4]
            stegdata = jts.retrievesteg(finalresultmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "AES", "AES is totes secure, right? Yeah", "CBC", False)
            decodedjt65msgs = jts.decodemessages(finalresultmsgs, False)
            self.assertEqual(len(result1), 1)
            self.assertEqual(len(result2), 1)
            self.assertEqual(len(result3), 1)
            self.assertEqual(len(result4), 1)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_AES_CFB_WAV(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "AES", "AES is totes secure, right? Yeah", "", "CFB", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)
            for index, value in enumerate(finalmsgs):
                tones = jt65sound.toneswithsync(value)
                jt65sound.outputwavfile(
                    "test_output-00" + str(index) + ".wav", tones)

            # Decode
            result1 = jt65sound.inputwavfile("test_output-000.wav")
            result2 = jt65sound.inputwavfile("test_output-001.wav")
            result3 = jt65sound.inputwavfile("test_output-002.wav")
            result4 = jt65sound.inputwavfile("test_output-003.wav")
            symbols1, confidence1, wavmsg1, s2db, freq, a1, a2 = result1[0]
            symbols2, confidence2, wavmsg2, s2db, freq, a1, a2 = result2[0]
            symbols3, confidence3, wavmsg3, s2db, freq, a1, a2 = result3[0]
            symbols4, confidence4, wavmsg4, s2db, freq, a1, a2 = result4[0]
            os.remove("test_output-000.wav")
            os.remove("test_output-001.wav")
            os.remove("test_output-002.wav")
            os.remove("test_output-003.wav")
            finalresultmsgs = [symbols1, symbols2, symbols3, symbols4]
            stegdata = jts.retrievesteg(finalresultmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "AES", "AES is totes secure, right? Yeah", "CFB", False)
            decodedjt65msgs = jts.decodemessages(finalresultmsgs, False)
            self.assertEqual(len(result1), 1)
            self.assertEqual(len(result2), 1)
            self.assertEqual(len(result3), 1)
            self.assertEqual(len(result4), 1)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())

    def test_OTP_WAV(self):
        for i in range(MAX_COVER_NOISE):
            # Encode
            jt65msgs = ["KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44",
                        "KB2BBC KA1AAB DD44", "KA1AAB KB2BBC DD44"]
            jt65data = jts.jt65encodemessages(jt65msgs, False)
            stegmsg = "BEACON FTW AND DEF CON 22"
            key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for n in xrange(random.randint(10, 30)))
            hidekey = jts.getnoisekey(key)
            cipherdata = jts.createciphermsgs(
                len(jt65data), stegmsg, "OTP", "I LOVE SECURITY AND STUFF", "", "", False)
            finalmsgs = jts.steginject(jt65data, i, cipherdata, hidekey, False)
            for index, value in enumerate(finalmsgs):
                tones = jt65sound.toneswithsync(value)
                jt65sound.outputwavfile(
                    "test_output-00" + str(index) + ".wav", tones)

            # Decode
            result1 = jt65sound.inputwavfile("test_output-000.wav")
            result2 = jt65sound.inputwavfile("test_output-001.wav")
            symbols1, confidence1, wavmsg1, s2db, freq, a1, a2 = result1[0]
            symbols2, confidence2, wavmsg2, s2db, freq, a1, a2 = result2[0]
            os.remove("test_output-000.wav")
            os.remove("test_output-001.wav")
            os.remove("test_output-002.wav")
            os.remove("test_output-003.wav")
            finalresultmsgs = [symbols1, symbols2]
            stegdata = jts.retrievesteg(finalmsgs, hidekey, False)
            resultstegmsg = jts.deciphersteg(
                stegdata, "OTP", "I LOVE SECURITY AND STUFF", "", False)
            decodedjt65msgs = jts.decodemessages(finalmsgs, False)
            self.assertEqual(len(result1), 1)
            self.assertEqual(len(result2), 1)
            self.assertEqual(len(decodedjt65msgs), len(jt65msgs))
            for i in range(len(jt65msgs)):
                self.assertEqual(
                    jt65msgs[i].rstrip(), decodedjt65msgs[i].rstrip())
            self.assertEqual(stegmsg.rstrip(), resultstegmsg.rstrip())
