# Homework 1 (CS5830) 
# Daniel Speiser and Haiwei Su
from MyFeistel import MyFeistel, LengthPreservingCipher
import binascii
import pytest
import base64
import os
"""
    TestMyFeistel is a suite of unit tests that ensure
    the functionality of MyFeistel, and its functions.
"""
class TestMyFeistel:
    """
        test_Functionality tests the basic functionality of
        the feistel cipher implementation. It initializes an
        instance of MyFeistel, and tests 20 times that the
        decrypted(encrypted) text is the same as the original
        text.
    """
    def test_Functionality(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        feistel = MyFeistel(key, 10)
        for i in xrange(20):
            msg = os.urandom(40)
            assert feistel.decrypt(feistel.encrypt(msg)) == msg
    """
        test_AllLengthMessages tests different lengths of valid
        input, ranging from length 1 to 102. Asserts that the
        decrypted(encrypted) text is the same as the original text.
    """
    def test_AllLengthMessages(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        fstl = MyFeistel(key, 10)
        for i in xrange(101):
            txt = os.urandom(i+1)
            dtxt = fstl.decrypt(fstl.encrypt(txt))
            assert dtxt == txt
    """
        test_zeroLengthMessages tests an invalid input, or input of
        length zero. Asserts that the decrypted(encrypted)
        text is the same as the original text.
    """
    def test_zeroLengthMessage(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        feistel = MyFeistel(key, 10)
        msg = os.urandom(0)
        assert feistel.decrypt(feistel.encrypt(msg)) == msg
    """
        test_feistelRoundEncDec tests to ensure that each individual
        round of _feistel_round_end and _feistel_round_dec are working
        properly. It asserts that the decrypted(encrypted) text from 
        ONE round equals the original input text.
    """
    def test_feistelRoundEncDec(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        for i in xrange(10):
            feistel = MyFeistel(key, 10)
            msg = os.urandom(40)
            assert feistel._feistel_round_dec(feistel._feistel_round_enc(msg, i), i) == msg
    """
        test_varyingRoundsFeistel ensures the proper functionality of 
        MyFeistel regardless of the number of rounds of feistel it 
        iterates through. Asserts that the decrypted(encrypted)
        text is the same as the original text independent on how
        many rounds have passed.
    """
    def test_varyingRoundsFeistel(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        for i in xrange(4, 14):
            feistel = MyFeistel(key, i)
            msg = os.urandom(40)
            assert feistel.decrypt(feistel.encrypt(msg)) == msg
    """
        test_varyingLengthKey is expected to 'fail'. We are ensuring that we throw
        a ValueError, or AssertionError exception if the user attempts to use a
        key of any length other that 16. We try to create an instance of MyFeistel
        with keys of varying length. If an error is thrown (as we expect), then the
        test passes. Otherwise, we fail the test for allowing a length key other than 16.
    """
    def test_varyingLengthKey(self):
        for i in xrange(10, 20):
            key = base64.urlsafe_b64encode(os.urandom(i))
            try: 
                feistel = MyFeistel(key, 10)
            # expected to raise AssertionError, if so, pass the test and return
            except AssertionError:
                pass
                return
            # otherwise fail the test    
            pytest.fail("Did not raise key length error.")
    """
        test_msgNotEqualCtx tests the randomness of the encryption
        key generation, and ensures that the crypto message output is
        never the same as the original output. Since feistel is deterministic
        we cannot test that the output of each round varies while using the
        same input, this is only a simple test to ensure overall output never 
        equals the user's input.
    """
    def test_msgNotEqualCtx(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        feistel = MyFeistel(key, 10)
        for i in xrange(20):
            msg = os.urandom(40)
            assert feistel.encrypt(msg) != msg
    """
        There is no 'test_randomnessOfCtx' since the feistel cipher is deterministic.
        However, test_randomnessOfMsgAndIV can 'test' the randomness and repeat 
        frequency of messages and IVs to ensure that there are no repeats of output ctx
        at any round of feistel over a number of uses.
    """
    def test_randomnessOfMsgAndIV(self):
        ctxs = []
        for i in xrange(100):
            key = base64.urlsafe_b64encode(os.urandom(16))
            feistel = MyFeistel(key, 10)
            for j in xrange(10):
                msg = os.urandom(40)
                ctx = feistel._feistel_round_enc(msg, j)
                assert ctx not in ctxs
                ctxs.append(ctx)
    """
        test_padding tests the padding of messages to ensure that the input
        message is padded if it is of an odd length. We assert that the padded
        message is the same as the decoded hex version of the msg split in two,
        each half of which padded with a '0' (LHS).
    """
    def test_padding(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        feistel = MyFeistel(key, 10)
        msg = os.urandom(41)
        h_msg = msg.encode('hex')
        length = len(msg)
        L, R = '0' + h_msg[:length], '0' + h_msg[length:]
        assert feistel._pad_string(msg)[1] == (L + R).decode('hex')
    """
        test_paddingAndUnpadding ensures the functionality of both the padding 
        and unpadding functions within MyFeistel. We assert that the unpadded(padded(msg))
        is equal to the original message.
    """
    def test_paddingAndUnpadding(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        feistel = MyFeistel(key, 10)
        msg = os.urandom(41)
        assert feistel._unpad_string(True, feistel._pad_string(msg)[1]) == msg
"""
    TestLengthPreservingCipher is a suite of unit tests that ensure
    the functionality of LengthPreservingCipher, and its functions.
    LengthPreservingCipher is really just a wrapper class for MyFeistel
    to simplify the API and need for parameters for users. 
"""
class TestLengthPreservingCipher:
    """
        test_Functionality tests the basic functionality of the length 
        preserving feistel cipher implementation. It initializes an 
        instance of LengthPreservingCipher, and tests 20 times that 
        the decrypted(encrypted) text is the same as the original text.
    """
    def test_Functionality(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        lpc = LengthPreservingCipher(key, length=5)
        for i in xrange(20):
            msg = os.urandom(5)
            assert lpc.decrypt(lpc.encrypt(msg)) == msg
    """
        test_EnsureConsistentLength test is expected to 'fail'. The LengthPreservingCipher
        class takes in a length, and 'preserves' that length throughout each round of encryption.
        The length upon instantiation must be consistent with the length of the data/msg passed
        into the encrypt method. If not, we expect an AssertionError to be raised.
    """
    def test_EnsureConsistentLength(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        lpc = LengthPreservingCipher(key, length = 5)
        for i in xrange(1,20):
            msg = os.urandom(i)
            try: 
                lpc.encrypt(msg)
            # expected to raise AssertionError because the length is inconsistent.
            # if raise, pass the test and return
            except AssertionError:
                pass
                return
            # otherwise fail the test    
            pytest.fail("Data length must be consistent with the length given during the instantiation of LengthPreservingCipher.")
    """
        test_EnsureFeistelSecurity tests to ensure the safety of the feistel encryption
        that is happening under the hood (since this is a wrapper class). We assert that
        the LengthPreservingCipher to perform 10 or more rounds of feistel cipher.
    """    
    def test_EnsureFeistelSecurity(self):
        key = base64.urlsafe_b64encode(os.urandom(16))
        lpc = LengthPreservingCipher(key, length = 5)
        assert lpc._feistel._num_rounds >= 10
