# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import base64
import binascii
import os
import struct
import time

import six

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf import hkdf
from fernet import Fernet

class InvalidToken(Exception):
    pass

debug = True

class Fernet2(object):
    def __init__(self, key, backend=None):
        if backend is None:
            backend = default_backend()
        try:
            self._fernet1 = Fernet(key, backend)
        except ValueError:
            self._fernet1 = None
        self._backend = backend

        key = base64.urlsafe_b64decode(key)
        hkey = hkdf.HKDF(algorithm=hashes.SHA256(), length=32,
                         salt='0'*16, info='', backend=backend)
        stretched_key = hkey.derive(key)
        self._signing_key, self._encryption_key = stretched_key[:16], stretched_key[16:]

    def SHA256hmac(self, key, data, sig=''):
        h = hmac.HMAC(key, hashes.SHA256(), backend=self._backend)
        h.update(data)
        if len(sig)>0:
            try:
                return h.verify(sig)
            except Exception as e:
                raise e
        else:
            return h.finalize()
        
    def _prf_hmac(self, key, data):
        out = self.SHA256hmac(key, data)
        while len(out)<len(data):
            out += self.SHA256hmac(key, out)
        return out[:len(data)]

    @classmethod
    def generate_key(cls):
        return base64.urlsafe_b64encode(os.urandom(32))

    def encrypt(self, data, associated_data=''):
        iv = os.urandom(16)
        return self._encrypt_from_parts(data, associated_data, iv)

    def _encrypt_from_parts(self, data, associated_data, iv):
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes.")

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encryptor = Cipher(
            algorithms.AES(self._encryption_key), modes.CBC(iv), self._backend
        ).encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # MAC:  version || ad || iv || ctx
        basic_parts = (
            b"\x81" + bytes(associated_data) + iv + ciphertext
        )

        tag = self.SHA256hmac(self._signing_key, basic_parts)

        # return: version || iv || ctx || tag
        return base64.urlsafe_b64encode(b"\x81" + iv + ciphertext + tag)

    def decrypt(self, ctxt, ttl=None, associated_data=''):
        if not isinstance(ctxt, bytes):
            raise TypeError("ctxt must be bytes.")

        try:
            data = base64.urlsafe_b64decode(ctxt)
        except (TypeError, binascii.Error):
            raise InvalidToken
        
        if not data:
            raise InvalidToken

        # return: version || iv || ctx || tag
        if six.indexbytes(data, 0) == 0x80:
            # This is a Fernet1 (old version) ctx, handle accordingly
            try:
                msg = self._fernet1.decrypt(ctxt, ttl=ttl)
            except Exception:
                raise InvalidToken
            return msg
        elif six.indexbytes(data, 0) != 0x81:
            raise InvalidToken
        assert not debug or not ttl, "You are calling new fernet with ttl values."

        # First, verify the tag
        basic_parts = (
            b"\x81" + bytes(associated_data) + data[1:-32]
        )

        try:
            self.SHA256hmac(self._signing_key, basic_parts, sig=data[-32:])
        except InvalidSignature:
            raise InvalidToken

        # Now decrypt the text
        # version (1-byte) || iv (16-byte) || ctx || tag (32-byte)
        iv = data[1:17]
        ciphertext = data[17:-32]
        decryptor = Cipher(
            algorithms.AES(self._encryption_key), modes.CBC(iv), self._backend
        ).decryptor()
        plaintext_padded = decryptor.update(ciphertext)
        try:
            plaintext_padded += decryptor.finalize()
        except ValueError:
            raise InvalidToken
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        unpadded = unpadder.update(plaintext_padded)
        try:
            unpadded += unpadder.finalize()
        except ValueError:
            raise InvalidToken
        return unpadded


class MultiFernet(object):
    def __init__(self, fernets):
        fernets = list(fernets)
        if not fernets:
            raise ValueError(
                "MultiFernet requires at least one Fernet instance"
            )
        self._fernets = fernets

    def encrypt(self, msg):
        return self._fernets[0].encrypt(msg)

    def decrypt(self, msg, ttl=None):
        for f in self._fernets:
            try:
                return f.decrypt(msg, ttl)
            except InvalidToken:
                pass
        raise InvalidToken
