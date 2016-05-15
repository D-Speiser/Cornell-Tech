# Homework 5 (CS5830) 
# Daniel Speiser and Haiwei Su
import os
import re
import json
from fernet2 import Fernet2 
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.backends import default_backend
import cryptography.hazmat.primitives.asymmetric as asym
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives.serialization import Encoding as encoding, PublicFormat as public_format

# HAZMAT WARNING. Use at your own risk! Research beforehand!
alg_switcher = {
    "ecdsa": asym.ec.ECDSA,
}

curve_switcher = {
    "secp192r1": asym.ec.SECP192R1,    
    "secp224r1": asym.ec.SECP224R1,    
    "secp256k1": asym.ec.SECP256K1,
    "secp256r1": asym.ec.SECP256R1,
    "secp384r1": asym.ec.SECP384R1,
    "secp521r1": asym.ec.SECP521R1,
    "sect163k1": asym.ec.SECT163K1,
    "sect163r2": asym.ec.SECT163R2,
    "sect233k1": asym.ec.SECT233K1,
    "sect571r1": asym.ec.SECT571R1,
    "sect571k1": asym.ec.SECT571K1,
}

hash_switcher = {
    "md5": hashes.MD5,
    "md160": hashes.RIPEMD160,
    "sha1": hashes.SHA1,
    "sha224": hashes.SHA224,
    "sha256": hashes.SHA256,
    "sha384": hashes.SHA384,
    "sha512": hashes.SHA512,
}

header_to_alias_mapper = {
    "ecdsa": "ecc", 
}

def get_switch_case(switcher, key):
    return switcher.get(key)

class PKFernet(object):
    def __init__(self, priv_keyring={}, public_keyrings={}):
        assert type(priv_keyring) is dict and type(public_keyrings) is dict, "Invalid parameter types, please pass JSON keyrings"
        self.priv_keyring = priv_keyring
        self.pub_keyrings = public_keyrings
    
    def url_safe_pem(self, pem_key, restore=False):
        key = re.findall("-----BEGIN PUBLIC KEY-----(.*)-----END PUBLIC KEY-----", pem_key, re.DOTALL)[0]
        if restore:
            key = key.replace("-", "+").replace("_", "/")
        else:
            key = key.replace("+", "-").replace("/", "_")
        pem_key = "-----BEGIN PUBLIC KEY-----" + key + "-----END PUBLIC KEY-----"
        return pem_key
    
    def export_pub_keys(self, key_alias_list=[]):
        if not key_alias_list:
            return self.pub_keyrings
        res = {}
        for k in key_alias_list:
            res[k] = self.pub_keyrings[k]
        return res
        
    def import_pub_keys(self, receiver_name, receiver_public_keyring, overwrite=False):
        if overwrite is False:
            assert receiver_name not in self.pub_keyrings, "A public keyring already exists for this user, pass overwrite=True to update existing keyring"
        self.pub_keyrings[receiver_name] = receiver_public_keyring
      
    def parse_header(self, header):
        arr = header.split('_')
        new_header = arr[0] + '.' + arr[2]
        # returns alg, hash, key_param, ver, usage, key_type
        return new_header.split('.')
    
    def header_to_alias(self, header):
        alg, _, key_param, ver, usage, key_type = self.parse_header(header)
        alg = get_switch_case(header_to_alias_mapper, alg)
        alias = '.'.join([alg, key_param, ver, usage, key_type])
        return alias
    
    def encrypt(self, msg, receiver_name, receiver_enc_pub_key_alias, sender_sign_header, adata='', sign_also=True):
        # ensure keyrings are populated with sender and receiver
#         and sender_sign_header in self.priv_keyring
        assert receiver_name in self.pub_keyrings, "Keys must exist for both the sender and receiver to encrypt."
        alg, key_param, ver, usage, key_type = receiver_enc_pub_key_alias.split(".")
    
        assert receiver_enc_pub_key_alias in self.pub_keyrings[receiver_name]
        rec_pub_key = load_pem_public_key(bytes(self.pub_keyrings[receiver_name][receiver_enc_pub_key_alias]), backend=default_backend())
    
        # generate ephemeral private key based on the given algorithm
        if alg == "ecc":
            curve = get_switch_case(curve_switcher, key_param)
            ephem_priv_key = asym.ec.generate_private_key(curve(), default_backend())
            
            ephem_public_key = ephem_priv_key.public_key()
            rpk = ephem_public_key.public_bytes(encoding.PEM, public_format.SubjectPublicKeyInfo)
            rpk = self.url_safe_pem(rpk)
            # exchange using ephemeral private key and the receiver's public key   
            shared_key = ephem_priv_key.exchange(asym.ec.ECDH(), rec_pub_key)
            
        elif alg == "rsa": 
            # For RSA, generate a secret key and encrypt under the receiver's public key.
            # Take the encrypted ciphertext at the place of ephemeral public key (after encoding in urlsafe-base64 format).
            shared_key = os.urandom(32)
            ephem_pub_key = rec_pub_key.encrypt(shared_key, 
                                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),
                                algorithm=hashes.SHA1(),
                                label=None)
                               )
            rpk = urlsafe_b64encode(ephem_pub_key)
                
        # sign if necessary using static sender's private key
        if sign_also:
            hdr_alg, hdr_hash, hdr_key_param, hdr_ver, hdr_usage, hdr_key_type = self.parse_header(sender_sign_header)
            
            send_priv_alias = self.header_to_alias(sender_sign_header)
            send_priv_key = load_pem_private_key(bytes(self.priv_keyring[send_priv_alias]), password=None, backend=default_backend())
            
            alg_instance = get_switch_case(alg_switcher, hdr_alg)
            hash_instance = get_switch_case(hash_switcher, hdr_hash)

            signer = send_priv_key.signer(alg_instance(hash_instance()))
            signer.update(msg)
            signature = signer.finalize()
            msg = urlsafe_b64encode(msg) + '|' + urlsafe_b64encode(sender_sign_header) + '|' + urlsafe_b64encode(signature)
        
        fern = Fernet2(urlsafe_b64encode(shared_key))
        f2_ctxt = fern.encrypt(msg, adata)

        return urlsafe_b64encode(adata) + "|" + urlsafe_b64encode(".".join(receiver_enc_pub_key_alias.split('.')[:3])) + "|" + rpk + "|" + f2_ctxt
    
    def decrypt(self, ctx, sender_name, verify_also=True):
        if len(ctx.split('|')) == 3:
            adata = ""
            alg_alias, rpk, f2_ctxt = ctx.split('|')
        else:
            adata, alg_alias, rpk, f2_ctxt = ctx.split('|')
        
        alg_alias = urlsafe_b64decode(alg_alias)
        adata = urlsafe_b64decode(adata)
        if "ecc" in alg_alias:
            rpk = self.url_safe_pem(rpk, restore=True)
            rpk = load_pem_public_key(rpk, backend=default_backend())

        alias_length = len(alg_alias.split('.'))
        if alias_length == 3:
            alg, key_param, ver = alg_alias.split('.')
        elif alias_length == 5:
            alg, key_param, ver, _, _ = alg_alias.split('.')
        else:
            raise ValueError('Encryption algorithm is not in the correct format')

        # use static private key for decryption
        for key in self.priv_keyring:
            if alg in key and key_param in key and 'enc' in key:
                rec_priv_key = load_pem_private_key(bytes(self.priv_keyring[key]), password=None, backend=default_backend())
                break
             
        assert 'rec_priv_key' in locals(), "Receiver does not have a corresponding {0} private key.".format(alg + '.' + key_param)
        
        if alg == "ecc":
            shared_key = rec_priv_key.exchange(asym.ec.ECDH(), rpk)
        elif alg == "rsa":
            shared_key = rec_priv_key.decrypt(urlsafe_b64decode(rpk),  padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
                
        fern = Fernet2(urlsafe_b64encode(shared_key))
        msg = fern.decrypt(f2_ctxt, associated_data=adata)
        
        if verify_also:
            if len(msg.split('|')) <= 1:
                raise ValueError('Message was not signed! Cannot verify unsigned message.')
            msg, sig_header, sig = msg.split('|')
            msg = urlsafe_b64decode(msg)
            sig_header = urlsafe_b64decode(sig_header)
            sig = urlsafe_b64decode(sig)            
            
            send_pub_keyring = self.pub_keyrings[sender_name]
            
            alias = self.header_to_alias(sig_header).replace("priv", "pub")
            
            send_pub_key = load_pem_public_key(bytes(send_pub_keyring[alias]), backend=default_backend())
            verifier = send_pub_key.verifier(sig, asym.ec.ECDSA(hashes.SHA256()))
            verifier.update(msg)
            verifier.verify() # throws error if verify is false
            
        return msg
