# Homework 1 (CS5830) 
# Daniel Speiser and Haiwei Su
from cryptography.hazmat.primitives import hashes, padding, ciphers
from cryptography.hazmat.backends import default_backend
import base64
import binascii
import os

def xor(a,b):
    """
    xors two raw byte streams.
    """
    assert len(a) == len(b), "Lengths of two strings are not same. a = {}, b = {}".format(len(a), len(b))
    return ''.join(chr(ord(ai)^ord(bi)) for ai,bi in zip(a,b))

"""
Part 2: Why Feistel encryption needs a minimum of four rounds

Solution:
For 1 round of Feistel, after encryption the new left portion of the output ciphertext is the same as the right portion of the original text. This - in plain text - reveals the input.

For 2 rounds of Feistel, let's look at the process of each round:
L'  <- R
R'  <- L + f(R)
L'' <- R'
R'' <- L' + f(R')

where f() is a round function. We can see that two messages with the same right half such that m1 = L1 * R, m2 = L2 * R. We also notice that for 2nd round Feistel, L1'' = L1 + f(R), and L2'' = L2 + f(R). Therefore, we have L1'' + L2'' = L1 + L2 which is equivalent to saying use a one time pad on the left side.

For 3 rounds of Feistel, let function F be the following algorithm:
(1). F get input L1 and R1 from input data, and put them into the encrypt function encrypt(L1, R1) to get encrypted ciphertext, S1, and T1 respectively. 
(2). F then chooses an element L2 != L1 and get encrypted text such that encrypt(L2, R1) to get corresponding encrypted cipher text S2 and T2. 
(3). Finally, we perform a decrypt where decrypt(S2, T2 + L1 + L2)  to S3 and T3. If we test if R3 = S2 + S1 + R1 and this is always true if only 3 round.

References:
1) https://courses.cs.washington.edu/courses/cse599b/06wi/lecture4.pdf
2) https://eprint.iacr.org/2008/036.pdf

-------- Note: + is a bitwise xor, and * is string concatenation --------
Attacks for 4, 5, and 6 rounds of feistel (6th round in O(2^(2n))) exist, but we could not 'decipher' how to apply them.
Link to description of these attacks can be found here:
https://www.iacr.org/archive/asiacrypt2001/22480224.pdf
"""
class MyFeistel:
    def __init__(self, key, num_rounds, backend=None):
        if backend is None:
            backend = default_backend()

        key = base64.urlsafe_b64decode(key)
        assert len(key) == 16, "Key must be 16 url-safe base64-encoded bytes. Got: {} ({})".format(key, len(key))
        self._num_rounds = num_rounds
        self._encryption_key = key
        self._backend = backend
        self._round_keys = [self._encryption_key \
                            for _ in xrange(self._num_rounds)]
        for i  in xrange(self._num_rounds):
            if i==0: continue
            self._round_keys[i] = self._SHA256hash(self._round_keys[i-1])
        self._iv = os.urandom(16)

    def _SHA256hash(self, data):
        h = hashes.Hash(hashes.SHA256(), self._backend)
        h.update(data)
        return h.finalize()

    def _pad_string(self, data):
        """Pad @data if required, returns a tuple containing a boolean
        (whether it is padded), and the padded string.
        """
        h_data = data.encode('hex')
        n = len(data)
        if n%2 == 0:
            return False, data
        l,r = h_data[:n], h_data[n:]
        # pad at the beginning
        # can be done at the end as well
        l = '0' + l
        r = '0' + r
        return True, (l+r).decode('hex')

    def _unpad_string(self, is_padded, padded_str): # Not tested!
        if not is_padded:
            return padded_str
        n = len(padded_str)
        assert n % 2 == 0, "Padded string must of even length. You are probably passing faulty data."
        l, r = padded_str[:n/2], padded_str[n/2:]
        return (l.encode('hex')[1:] + r.encode('hex')[1:]).decode('hex')
    """
        The Function instantiates AES in CBC mode with a static IV 
        to act as a round function, a.k.a. pseudorandom function generator.
    """
    def _prf(self, key, data):
        padder = padding.PKCS7(ciphers.algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encryptor = ciphers.Cipher(ciphers.algorithms.AES(key),
                                   ciphers.modes.CBC(self._iv),
                                   self._backend).encryptor()
        return  (encryptor.update(padded_data) + encryptor.finalize())[:len(data)]

    # Can also instantiate the round function using a SHA256 hash function.
    def _prf_hash(self, key, data):
        """Just FYI, you can also instantiate round function ushig SHA256 hash
        function. You don't have to use this function.
        """
        out = self.SHA256hash(data+key)
        while len(out)<len(data):
            out += self.SHA256hash(out+key)
        return out[:len(data)]

    def _clear_most_significant_four_bits(self, s):
        """
        Clear the first four bits of s and set it to 0.
        e.g, 0xa1 --> 0x01, etc.
        """
        assert len(s) == 1, "You called _clear_most_significant_four_bits function, but I only work with 1 byte."
        return ('0' + s.encode('hex')[1]).decode('hex')
    """
        For each round of encryption we check whether the given data needs to get padded.
        The function self._pad_string handles both cases (even length not needing padding,
        and odd length cases which need padding). We call self._feistel_round_enc for self._num_rounds
        times, which encrypts and unpads the message each time before beginning next round of encryption. 
        We iterate until we the number of rounds required defined by self._num_rounds.
    """
    def encrypt(self, data):
        ctx = data
        for i in range(self._num_rounds):
            is_padded, padded_data = self._pad_string(ctx)
            ctx = self._feistel_round_enc(padded_data, i)
            ctx = self._unpad_string(is_padded, ctx)
        return ctx
    """
        The decrypt function has a similar algorithm to that of the encrypt function.
        The only difference is that the iteration is done in the reverse order as that
        of encrypt, since we need to use the opposide order that the encryption keys were 
        given in, in order to use the correct one for the corresponding round. The logic
        otherwise is the same.
    """
    def decrypt(self, ctx):
        data = ctx
        for i in range(self._num_rounds - 1, -1, -1):
            is_padded, padded_ctx = self._pad_string(data)
            data = self._feistel_round_dec(padded_ctx, i)
            data = self._unpad_string(is_padded, data)
        return data
    """
        According to the definition of a Feistel cipher, we first divide the input data 
        into left and right portions of equal length. Next, we xor the left hand side of the
        data with the right hand side of the data combined with the _prf (round function). Finally
        the new left hand portion of the data is the xor data calculated (as stated above) and the 
        right hand portion is the original left hand of the data. We return their concatenation as
        the encrypted data from this round.
    """
    def _feistel_round_enc(self, data, round_num):
        """This function implements one round of Fiestel encryption block.
        """
        mid = len(data) / 2
        L, R = data[:mid], data[mid:]
        Ri = xor(L, self._prf(self._round_keys[round_num], R))
        
        print "ENC Round {0} key: {1}".format(round_num, binascii.b2a_hex(self._round_keys[round_num]))
        print "ENC Round {0} ctx: {1}".format(round_num, binascii.b2a_hex(Ri + R))
        
        return Ri + R
    """
        Decrypt is similar to encrypt, without loss of generality.
    """
    def _feistel_round_dec(self, data, round_num):
        """This function implements one round of Fiestel decryption block.
        """
        mid = len(data) / 2
        Ri = data[mid:]
        Li = xor(data[:mid], self._prf(self._round_keys[round_num], Ri))

        print "DEC Round {0} key: {1}".format(round_num, binascii.b2a_hex(self._round_keys[round_num]))
        print "DEC Round {0} ctx: {1}".format(round_num, binascii.b2a_hex(Li + Ri))

        return Li + Ri
"""
    This class is a simplified wrapper class of what we've implemented above. We do 
    not allow a user to change the number of rounds, or the length of the data in order
    to prevent them from instantiating a cryptographic primitive in an insecure way.
"""
class LengthPreservingCipher(object):
    def __init__(self, key, length=5):
        self._length = length
        self._num_rounds = 10 # Hard code this. Don't leave this kind
                              # of parameter upto the developers.
        self._feistel = MyFeistel(key, self._num_rounds)
    # Calls MyFeistel's encrypt method.
    def encrypt(self, data):
        assert len(data) == self._length, "Data size must equal the length defined in the instantiation of LengthPreservingCipher."
        return self._feistel.encrypt(data)
    # Calls MyFeistel's decrypt method.
    def decrypt(self, data):
        assert len(data) == self._length, "Data size must equal the length defined in the instantiation of LengthPreservingCipher."
        return self._feistel.decrypt(data)
