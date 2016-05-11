## Specification of Fernet2
```(By Rahul Chatterjee (rahul@cs.cornell.edu)```

Fernet2 is an symmetric-key authenticated encryption scheme, also called
authenticated encryption with associated date (AEAD). 


### Key format

Key can be any string with enough entropy. Key must be encoded in
urlsafe-base64 string.  Fernet2 will internally apply HKDF to generate
two independent keys-- 16-byte encryption key and 16-byte signing key.  

Note, Fernet2 also supports decrypting ciphertexts created using original
version of Fernet.

### Ciphertext format ###

The plaintext is encrypted using AES-block cipher in CBC mode.  The
*whole* ciphertext (including the other fields such as version, IV,
HMAC etc.) is encoded in `urlsafe-base64` format.

 
```
	<version> || <IV> || <ciphertext> || HMAC
```

*  `<version>`: 8-bit version number, its value should be `0x81`. 
*  `<IV>`: IV is 16-byte random number.
*  `<ciphertext>`: This field has variable size, but is always a
   multiple of 128 bits, the AES block size. It contains the original
   input message, padded and encrypted.
*  `HMAC`: 32-byte long SHA256-HMAC of `<version> || <associated_data> || <IV> ||
   <ciphertext>`


### API
```python
>>> from fernet2 import Fernet2 
>>> from base64 import urlsafe_b64encode
>>> key = urlsafe_b64encode("This is my super secure key!")
>>> adata = "Sample associated data" 
>>> fnt = Fernet2(key)
>>> ctxt = fnt.encrypt('Secret Message', associated_data=adata)
>>> ptxt = fnt.decrypt(ctxt, associated_data=adata)
```

The  `decrypt`   function  raises  `InvalidToken`  exception   if  the
decryption fails.  Any change  in ciphertext  or associated  data will
result in `InvalidToken` exception.

(Rest of the details you can find in [Fernet Spec](https://github.com/fernet/spec/blob/master/Spec.md))



