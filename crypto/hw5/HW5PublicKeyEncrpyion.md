# Public-key encryption
<script type="text/javascript" src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML"></script>
```json
Deadline: 23:59:59, May 11, 2016 (Last day of classes)
```
We want to build an application layer public key encryption scheme that will allow users to send messages asynchronously with others without a pre-shared secret key.  A typical way to do this is using a hybrid of public-key and symmetric-key encryption schemes. The symmetric encryption portion of this can utilize  our existing Fernet2 encryption scheme. While for the public-key part of it, we shall use one or more asymmetric encryption schemes supported by the `cryptography` library. Let call this encryption scheme `PKFernet`.


### Functionality
We expect following basic functionalities from `PKFernet`.  
1.  The scheme allows users to `encrypt` and `decrypt` messages. The `encryption` routine should first sign the message using the sender’s secret key for signing, and then encrypt the signed message using the public key for encryption of the recipient. The recipient should be able `decrypt` and verify the message using his private key for encryption and public for signing of the sender respectively.  
2.  `PKFernet` should be cryptographically agile, i.e., it should be able to adapt to new cryptographic primitives. Users might choose to use different cryptographic primitives, and may or may not choose to be backward compatible. But the scheme should gracefully handle (process or reject) different versions of ciphertexts.


### Specification?
As this encryption scheme explicitly attempts to enable a global communication of encrypted messages, we have to decide on a global protocol and specification. We shall assume that we already have a medium of communication, and only need to decide on the specification of the encryption scheme. However, remember that the specification should be without ambiguities, should be democratically selected, and every one must follow it. *First part of this assignment is to come up with a common specification.* We will meet on Thursday, April 21 during the regular class time and discuss specification details, such as: the format of the ciphertext, the elliptic curve to use, the signature methods, etc.  A draft of the specification document (google doc) is shared among all of you; the link is given below. The second phase of the project will have individuals or groups of two write their own implementation independently of other groups. So the specification is shared, but the implementations will not.


The final implementations will be cross-tested, that is an encrypted message from one group will be decrypted using another group’s implementation.  I shall set up another shared Google spreadsheet for sample plaintext-ciphertexts pairs from each group.



### Shared documents
* [Specification doc](https://docs.google.com/document/d/1kyvwWRUt2RAXPuA_CyFqFkeAdzAi1gdOWHOJB4eBjFw/edit)  
Use this doc to discuss about the common specification for the encryption scheme. 

* [Sample plaintext-ciphertext pairs](https://docs.google.com/spreadsheets/d/1390RFGCC42hCuNKBgxoZUVVqksrP2IjVCmmIX6xNHWw/edit#gid=0)
This doc is to help your test your implementation against the implementations of other groups.
