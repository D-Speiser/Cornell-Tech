# Homework 5 (CS5830) 
# Daniel Speiser and Haiwei Su
import os
import pytest
from pkfernet import PKFernet
from base64 import urlsafe_b64encode, urlsafe_b64decode
"""
    TestPKFernet is a suite of unit tests that ensure
    the functionality of PKFernet, and its functions.
"""
pr_kr = {    
    "ecc.sect163r2.2.enc.priv": "-----BEGIN EC PRIVATE KEY-----\nMFMCAQEEFQG7DdpXIBcUzcMi8gFGVmyumrFPgaAHBgUrgQQAD6EuAywABALHCp4+\nsVawD1gHCXg3NB7fU6Eg3wJWZZpnhtLfjOi4HrvtA6KK+LHWIQ==\n-----END EC PRIVATE KEY-----",
    "ecc.sect163r2.2.sig.priv": "-----BEGIN EC PRIVATE KEY-----\nMFMCAQEEFQNGduZk1nDr/FgdxeYVEsJ5WDTInaAHBgUrgQQAD6EuAywABAQ98qHY\nPH1AaS+cosvDHhbnKPClRARtaasqhZnLhX7ZJFqqOcLPZwS0Nw==\n-----END EC PRIVATE KEY-----",
    "ecc.sect223k1.1.enc.priv": "-----BEGIN EC PRIVATE KEY-----\nMG0CAQEEHTfL8cuJ+IcGqUCf4NnHnMtGLYXWQLkUTfocWqjqoAcGBSuBBAAaoUAD\nPgAEALoiB5NAKUn5BB+X3a8qwM8cTQLx9UdLdp7RxHa2AKLyjxSyO10OECK7XZ22\n0yAiqhao1O3DY+op+/0r\n-----END EC PRIVATE KEY-----",
    "ecc.sect223k1.1.sig.priv": "-----BEGIN EC PRIVATE KEY-----\nMG0CAQEEHVvXQB+5iSIMCzn0sbpP1Q7HdU5mdTq7Lt1H+ptkoAcGBSuBBAAaoUAD\nPgAEAPrnwtrxdsat98FiF2rHLn7AqZ/diCHCVRg1WpnNAchbUX7anUWKBDTPh6z6\n05QG22/s7wf7xXk/unsN\n-----END EC PRIVATE KEY-----",
    "ecc.secp224r1.1.enc.priv": "-----BEGIN EC PRIVATE KEY-----\nMGgCAQEEHIy9A0wpj7UR6+9FgGJiBe+FsR714WXFmB2DAiOgBwYFK4EEACGhPAM6\nAAQ6wymm4zZWmmuAtaOvUd5vTik73HWRhH8SPGC+d5OaY05JGn4TkwWOEocuND0R\nqPAixpCXusAMxw==\n-----END EC PRIVATE KEY-----",
    "ecc.secp224r1.1.sig.priv": "-----BEGIN EC PRIVATE KEY-----\nMGgCAQEEHKDxHuvyYU93h7YxWekVhwfB3CvKvbPGS1YL95+gBwYFK4EEACGhPAM6\nAARa+QRxUyLy1XrpuPuuqA6rx06XsHlZZl2Yl3+hEG0eGMsHDIQtesVhhrZu6guB\no/i2yH/0k6Gw9A==\n-----END EC PRIVATE KEY-----",
    "ecc.sect571r1.1.enc.priv": "-----BEGIN EC PRIVATE KEY-----\nMIHuAgEBBEgCmpoLrYY2dVGFsC5npHTTUDx9fqsn2ZuDiFCcCPbZrv9aLn130iLv\nUski4EH2UQcZnuiQLzt1BNYShP8ApcKAoTulRHuHErSgBwYFK4EEACehgZUDgZIA\nBAJuiwyk1Ablmba5ka467lkiQy0//PCYScU3qzRCAfCwe1YdSOPQ+AmeD8JJpNIr\norT5+SSpnplSqPlsoGiNXCa0PHF91lllwwL10cNb5eHGzs5fYk7+va3CooGPo0lz\ns7WUnqzFjkkeOs//GIcP9YlBeORS559mvVq0YJ58dh5b3C6lmIpYCfG1Nt0e7Tn5\ntQ==\n-----END EC PRIVATE KEY-----",
    'ecc.sect571r1.1.sig.priv': "-----BEGIN EC PRIVATE KEY-----\nMIHtAgEBBEdMKzALb1qB4YzMYrerGLPSTqI24Hu0qvjp5I6A01x9odFscsAy2uPR\nfRhmVEKFSEq0PD059rIrZ0Bk8aIbcFnPj8EF0fzbtqAHBgUrgQQAJ6GBlQOBkgAE\nAg/InE0ogbFuZTbwA5jIjzNIsGWwdzK67En2ecdoZmecgH+1YEqwirb/uyBTTNlq\njDageG5ApJJK3ddwRrwEX+SuRHtTbs+fAZJ4Mf1i4kYYyus0wDew3zAaG+5Olqtz\nbEacghXR4i+Uy/v0aDE4tJoFf3Puspl6VoYPOMk0NgvPC0gAnYDZDzySyeJXeUoT\n-----END EC PRIVATE KEY-----",
    "rsa.2048.1.enc.priv": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDdLTii+lsZ+VLq\nke80iB83qjwdnKU5RE1pQwUDhPmkAR3gR31j03jQS5O9fydQt8iiDUfoNsU8c21p\nv5fihUvQlc1zUwjhbDGRyJzfT3hdiRmJPB4YqXqL+QkFjLxLgOAVazZwyEBzd6Z2\nC/GsDbZv9bht40Rj35am7s2Y/E8runHRLo4eBaPp798ik+jNPc+OueiKUt30Z26/\nZs7TitsVEYoXjXdSfZgGvEQDB4oi4UV/f+S6UlAnKFr0Xc2VzvzHEXm++/wI9Vmy\n35qVkSStuY/HbDwRwh6Y5nKMkv0RSeRC4T5xXn63TbQVgbNJUcf/khfhT8ETVpF2\nzTxOPS1TAgMBAAECggEAPtYJICxWU4PE7cV2GwuNKuhfWd5WBnYENCKJOx29Or3i\negR1eDXtPegq2gxU5BbCll+FjVB6Kpl0fTWkdgN+rYzRqLDvdfOiBZPkFYFjZdd8\nfMOqnUERAtFGoeAA4saDYzJpbhNGVEeq8CCmkUX4DcjWk8mcdW9hQp3XpV4RNA+l\nrIh0WrN/FxXeQBaZjhCAT5GFCkqxKc4xVZcRbtG3QcAMVzXmWR9Qy5zygQjfkFd4\nHICInnM3Dfei9smdLFlcR7UwjjGAdblvd2jZYnzATVZY4PKEcXCuMoW1hpMjp1la\nfppQ1wGDFklk6M3dof7rGcTfhXv4QdQdxjuJRjdsYQKBgQD9OzwXJA1zhKplhw6/\npo6mr9JPPe8VSPQhfuUoklF2grgUjNM3f0cvuaZlqXxBvQ+wQxMv+jncUaTx1nWe\nUsujrY8AfoO/03ovAS5dOMBN7t6qq7CkEgK9zTg74/Uw5N6sq+o9hwz/2EXMCAmx\ndwNM1r2iIKhsSE4oSWNb/qeykQKBgQDfmETdzlg+xPtD0gnf9DWcHgDD/ixTiCMV\n+34hF+tBBeivc2e+yWLmz27odLGmLe1LplBIzdjh0B0y1BCUtI/fOVxNPBi5EGaD\nNwCMjfDEkU7hw1+sdW1MmFBmlcxPAYxQaHCDwAi7hcbliKOSrF1JsYbauSPETbAv\nukWZLMZLowKBgBnRokzRtjVi/2SeophTyROhtZWywN+wsoN/xqmeUYP9y/r8aMSt\ny3pIOXkAENU7C5BzJk+r+Z5HDMRDk3ZzBqRHm973B0PVsg1811dV4/WON1G7c6Um\n2PS1KdihY2x6yWFdneJsFJ05VdR5tVNMyR9afbc8ETAJJz7gTKsiicKhAoGAdgMK\nJf+ot8iDzbHoIFnmibWUNd3LS3NJAWsxkQns0u7pduD0WtAz8Rp+sRYWRV1sJ0dq\njGKJG/YZ0x/2eGYsoWbG/sS/T74GPS8kjQrFjxoahjH2JzH7NDgYB2z83p40jqPw\n7rjGYyMibTeHDf0HZ8PZJ0wcQpm2ahpobYYiSv0CgYBk7AZkeMIMnboLV8gm7ef3\nSk4SIu2NkCf+xbgU9wUKU2BJ4/iJvm3JOOABgNPTDklEk6w9KculD7zHnrKS8nEV\nA/gMTx13neY3w+B+ce9Hjyd4BEFuMDvKwc/LkMo4kLYwQWrsMy304Qh080iYQonz\nxoKY9t5dhIxxtUFM1JXG0A==\n-----END PRIVATE KEY-----",
    "rsa.2048.1.sig.priv": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC9UU+nz6k+WT0F\nCLhzcVPYgisUaBOHCVjroGpZwIje5ICHckT+VRnKAIypMdNtJGB2L+3Qg2vBdWF1\nttPrc51VeJbe/VG1CMGFTfEQqYDd+0EIAqZTzvtZmmpxcJpqa4wA9GRoop9Jowpp\nVFKk43i8AqFi9UAyzIiQp/BQh+8cpmhj69oU10RSHJyE3RnORHCFprsBSZjXI9Q2\nl5fiNvhTuzLm1eZPKY2bhrlKKfK/jaPGgb0EdTJ5fYGFrpeLIJcHj/yMOljqKmNm\nR6lF8AtlTuZVhj4bxzZNNXbLeStHJPvxF/44AGDp+iDt8Fodg8vx/gwBBlwjwlh8\ngV7erZGTAgMBAAECggEBAIAKz4obDEeMCZYvCLmji2bi2wopPhPVwZtT2rorWycN\netSg94Lgwdl6t6fzeCDYOpmU3w5o5Gdq4WjBJ+GWR3I4ZioZQLrlWiWzynhPfEYm\nmhw11pLWae93XcittPKHHKDEqmiOnJcsO21zx5WX99+JE+gfIbV52l+kBggheBpy\nUlsQ/tSgXPVnlE1Bt7s085s9dk5BxUojEz4rQoViUgiyjP8bpxDJoghaTftvl37a\ngTjlO8ZNklt4Bqx7V7NUhcHXWsjWAj+yoXb7iYXXaVMC9Y0+Y8U4O+cK45foj2bf\nEmMW+mGIH9KYKik5FdPGeHi2A1XnPRMj2FBoOAVnH8kCgYEA9zDx4tyaRUELXNvg\nCtOnYLjeu8HuyOMVS0uOrxiF7sftGaNxdWyXv+YefTQs1NyyzqfkZXR6IBgtaxiE\n77kLtYJauzQnrZ+uJh8z6dDUe77RSDduC8QuG3DKuUdd8tBJfEAPT3AAdNJ1MJpV\nsPtk0+IcPbsI7+lhkDMnAXorn+0CgYEAxBBm8dJeVcail2Qn3eMwmTc/LvAFj/1v\nIk8L7oTsX2G+jYDc/g8xZkrOcTL3jK5iWswpH4T59Av+n3/tYw2qlPskvsUauzLM\n84s2AV8NI4HNjaruUvP534KY5QQYxpX5IyTF9JZH9VEnPnAyhCRR2ZPp2FLDFxJR\nytIOd1mYx38CgYEAz6ukG9cAGJyrwijLUe09WmoWXiFwzf7Rvf9NcVcl9lSqonaI\n9ID2AHeBN+jknTSJWEr+/CleDKajSa1AyfFpn+VS+qG3kAtuEIL4Z0BVs1y9kHFZ\nF7OKlO0us3f8uuk4Q5XCBxfumjbR07JluZmKvOPinA4NVRl6KN6Ar6IHEoUCgYA/\ndwe7s1rx7RBobPUyr/3lOqrrKKrER0cYFfpIxSI2Zc9mwpXGb2iQMhrNLbBQC4qu\n1XNiTosSYmeTfbd73sqe2wSz892JRxJsq11Z6Ei6e6Pr/a6Tj4IMxZt0VnUmoxk4\nNQkW+SZl1FUdsvfHKnKMOYLykSexai6rtn8URx5bRQKBgQC5J0+UVJYGnH2MmgNK\nwN+5VjbzOgqfLQocNycxCOAAuocB4LkFOTG9Wx7BYuTFtVa4vbOtyzttpv4NaQyH\n+nh4EMGmqxT7+NraHoaYmmk5+pfa8ZD2f4wivo95Ewb+aiAHxdP/s5N0lQaQE2/K\n5HK/08hKDXdDZL944AVS9rDx8w==\n-----END PRIVATE KEY-----"
}

pu_kr = {
    "dan_haiwei": {
        "ecc.sect163r2.2.enc.pub": "-----BEGIN PUBLIC KEY-----\nMFIwEAYHKoZIzj0CAQYFK4EEABoDPgAEALoiB5NAKUn5BB+X3a8qwM8cTQLx9UdL\ndp7RxHa2AKLyjxSyO10OECK7XZ220yAiqhao1O3DY+op+/0r\n-----END PUBLIC KEY-----",
        "ecc.sect163r2.2.sig.pub": "-----BEGIN PUBLIC KEY-----\nMEAwEAYHKoZIzj0CAQYFK4EEAA8DLAAEBD3yodg8fUBpL5yiy8MeFuco8KVEBG1p\nqyqFmcuFftkkWqo5ws9nBLQ3\n-----END PUBLIC KEY-----",
        "ecc.sect223k1.1.enc.pub": "-----BEGIN PUBLIC KEY-----\nMEAwEAYHKoZIzj0CAQYFK4EEAA8DLAAEAscKnj6xVrAPWAcJeDc0Ht9ToSDfAlZl\nmmeG0t+M6Lgeu+0Door4sdYh\n-----END PUBLIC KEY-----",
        "ecc.sect223k1.1.sig.pub": "-----BEGIN PUBLIC KEY-----\nMFIwEAYHKoZIzj0CAQYFK4EEABoDPgAEAPrnwtrxdsat98FiF2rHLn7AqZ/diCHC\nVRg1WpnNAchbUX7anUWKBDTPh6z605QG22/s7wf7xXk/unsN\n-----END PUBLIC KEY-----",
        "ecc.secp224r1.1.enc.pub": "-----BEGIN PUBLIC KEY-----\nME4wEAYHKoZIzj0CAQYFK4EEACEDOgAEOsMppuM2VpprgLWjr1Heb04pO9x1kYR/\nEjxgvneTmmNOSRp+E5MFjhKHLjQ9EajwIsaQl7rADMc=\n-----END PUBLIC KEY-----",
        "ecc.secp224r1.1.sig.pub": "-----BEGIN PUBLIC KEY-----\nME4wEAYHKoZIzj0CAQYFK4EEACEDOgAEWvkEcVMi8tV66bj7rqgOq8dOl7B5WWZd\nmJd/oRBtHhjLBwyELXrFYYa2buoLgaP4tsh/9JOhsPQ=\n-----END PUBLIC KEY-----",
        "ecc.sect571r1.1.enc.pub": "-----BEGIN PUBLIC KEY-----\nMIGnMBAGByqGSM49AgEGBSuBBAAnA4GSAAQCbosMpNQG5Zm2uZGuOu5ZIkMtP/zw\nmEnFN6s0QgHwsHtWHUjj0PgJng/CSaTSK6K0+fkkqZ6ZUqj5bKBojVwmtDxxfdZZ\nZcMC9dHDW+Xhxs7OX2JO/r2twqKBj6NJc7O1lJ6sxY5JHjrP/xiHD/WJQXjkUuef\nZr1atGCefHYeW9wupZiKWAnxtTbdHu05+bU=\n-----END PUBLIC KEY-----",
        "ecc.sect571r1.1.sig.pub": "-----BEGIN PUBLIC KEY-----\nMIGnMBAGByqGSM49AgEGBSuBBAAnA4GSAAQCD8icTSiBsW5lNvADmMiPM0iwZbB3\nMrrsSfZ5x2hmZ5yAf7VgSrCKtv+7IFNM2WqMNqB4bkCkkkrd13BGvARf5K5Ee1Nu\nz58Bkngx/WLiRhjK6zTAN7DfMBob7k6Wq3NsRpyCFdHiL5TL+/RoMTi0mgV/c+6y\nmXpWhg84yTQ2C88LSACdgNkPPJLJ4ld5ShM=\n-----END PUBLIC KEY-----",
        "rsa.2048.1.enc.pub": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3S04ovpbGflS6pHvNIgf\nN6o8HZylOURNaUMFA4T5pAEd4Ed9Y9N40EuTvX8nULfIog1H6DbFPHNtab+X4oVL\n0JXNc1MI4Wwxkcic3094XYkZiTweGKl6i/kJBYy8S4DgFWs2cMhAc3emdgvxrA22\nb/W4beNEY9+Wpu7NmPxPK7px0S6OHgWj6e/fIpPozT3PjrnoilLd9Gduv2bO04rb\nFRGKF413Un2YBrxEAweKIuFFf3/kulJQJyha9F3Nlc78xxF5vvv8CPVZst+alZEk\nrbmPx2w8EcIemOZyjJL9EUnkQuE+cV5+t020FYGzSVHH/5IX4U/BE1aRds08Tj0t\nUwIDAQAB\n-----END PUBLIC KEY-----",
        "rsa.2048.1.sig.pub": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvVFPp8+pPlk9BQi4c3FT\n2IIrFGgThwlY66BqWcCI3uSAh3JE/lUZygCMqTHTbSRgdi/t0INrwXVhdbbT63Od\nVXiW3v1RtQjBhU3xEKmA3ftBCAKmU877WZpqcXCaamuMAPRkaKKfSaMKaVRSpON4\nvAKhYvVAMsyIkKfwUIfvHKZoY+vaFNdEUhychN0ZzkRwhaa7AUmY1yPUNpeX4jb4\nU7sy5tXmTymNm4a5Sinyv42jxoG9BHUyeX2Bha6XiyCXB4/8jDpY6ipjZkepRfAL\nZU7mVYY+G8c2TTV2y3krRyT78Rf+OABg6fog7fBaHYPL8f4MAQZcI8JYfIFe3q2R\nkwIDAQAB\n-----END PUBLIC KEY-----"
    },
    "rahul": {
      "dsa.1024.1.sig.pub": "-----BEGIN PUBLIC KEY-----\nMIIBtzCCASsGByqGSM44BAEwggEeAoGBAK0wjowa0YhHl_wB8jgfN6sl4HeiCfSf\nE99DY7McBs7Op9L8qMTQt151fiIcaaQeAOpzUqI6ofk-1iaSK0iKTQ63t9QLl1mz\nbknp0vMny4IW2PqSkE14OZtqaDzRsWJqKAIb91BdKGyqdFNmRfHddpaPuDNawOge\ng8yIe6P4QBN1AhUAnbg5PlIuvavIX2g_YIC9uGbm1xkCgYBW93q4kiXqdPki7a5j\ngYSGD9uul58q6h361gl_BQcTwvf2VJioffL7HqfDS--jmS8_cZCJ3VPeXqUvDCOz\nLKnwl9Fc3s7xG8Ks0R0PyLp3RikUKWv1CtT6GmS81JrzWvPrgKBWbIrIruddLtvb\nFKX0l4BHV751QLLU7mmcPbcSFgOBhQACgYEAiKIEcb55nZF-_E38puoOeGqvv2sy\nTnE9Prek5kpAzqA9Q9VT4m4SmKlFAbE6qC_7IxgQTjoKs301EZSWeA15z6vcnOo-\nr-N5Z8Gn7qwJDzCL3NJpRhTQgBVL_Xh4xpJS-MM1EoEEqKBem8gCGFM-TGLdrx-K\nMDbcPF_UfT46rY0=\n-----END PUBLIC KEY-----\n", 
      "ecc.secp224r1.1.enc.pub": "-----BEGIN PUBLIC KEY-----\nME4wEAYHKoZIzj0CAQYFK4EEACEDOgAElFmWnRvIgK53WG088jVdDFhMgvfP7SHS\nNzPpLe4Y7NdvjawlwfTb5k3eIvT0hTRra431odw19fc=\n-----END PUBLIC KEY-----\n"
    },
    "asheesh_teja": {
        'ecc.sect571r1.1.enc.pub': '-----BEGIN PUBLIC KEY-----\nMIGnMBAGByqGSM49AgEGBSuBBAAnA4GSAAQDdFTVWAhIlyVYby0ghHva8IV9fGUD\nS4Lio7wLeAWnpVHpizPZJJ3178FbVUoRnOYEque22xt4bfcec6LBTymk8aKo6reM\nf5IDzowZ6l0Jgi6Hr6jT5Vp/5kWB3k/he3gdoQ4czSzcK5MLK8hSWtHrL5uWupIt\ntZyisEVzSD9FO6wp6L1sRq/eXGvcMIJc/os=\n-----END PUBLIC KEY-----\n',
        'ecc.secp256r1.1.sig.pub': '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEg9EPhZ7DIXVSs8VkmhgEHTDWUkzw\n5vfMDP75tWbjzZ99qfkT1xsED6X3aMzBLt8pcxlU2wxyBxRn2vkbBDwqjw==\n-----END PUBLIC KEY-----\n'
    },
    "joanna": {
        "ecc.secp224r1.1.enc.pub": "-----BEGIN PUBLIC KEY-----\nME4wEAYHKoZIzj0CAQYFK4EEACEDOgAEfJGjyYCKvmUnR4xBS0whcGOVoZZAMxNb\nzZpOyzABgJRMkdGRAuqp5WdzLkunoP7XMZRZ0gYK2_Y=\n-----END PUBLIC KEY-----\n",
        "ecc.secp224r1.1.sig.pub": "-----BEGIN PUBLIC KEY-----\nME4wEAYHKoZIzj0CAQYFK4EEACEDOgAEC5Ji9nM3FNIIEsYt9JRvw3xL-kc6ogS6\nr7ljm_33-CTLftzYUhlgmqp8SM11163IuRtBPlpdVis=\n-----END PUBLIC KEY-----\n",
        "rsa.2048.1.enc.pub": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyhLi_lY_lyj8ZyNW87uE\n-K4FWRI5-66Ka5duMzU7sE-tRgGfe1hUcsHfeZkd2GaujfeROTXPQlcrdUDoYBIi\nImL9PC0FccN2_gKKwfR-rmvAuM8JaGZg_e8M0twatZnj0TxNjTVmKCQn20XBYkou\nuDo2LtaLiYn9W3lEf-mrMXs_iQYCINpubNj9c9IfGuyF9s_Z-vuvwiY7T_DFjYDV\nRk0LsB8SAcRyjS67Nvlt45552DUicbF8jcsjbVRG2IHKVDrl0xKm6U4BuHw6mt55\n8TD22me-jFYVXTpahoVe_c3ETvXgK74kEXE6qFfYm0zIg7MDf15xNdinDaf0wufw\nKwIDAQAB\n-----END PUBLIC KEY-----\n",
        "rsa.2048.1.sig.pub": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqFqv4z8iCwyj_FOkUIvv\nDjgOA0piSW2NEe0Q0mFJ4-eKcKR98i_4X04OaL5wTiDHSFU66G3LJiMjLEk7J-Lp\nzmeF1K_S9f6uIZZdXmjJoaQfF7qYJKd6ktM_PMHHkmB0pl8ygOFYen9cPJWKwxeX\niia6NxfVRoHnZeGQ2fw7Oya8R_18OQAbTpJ9GuMfJDoxpd1d1ypmnxM4Sqi9cdCC\nopZN6djZwC_Ml25nDSycY-yl4ih0ZNEXwSatSD9Dex1DE6O1YmijOGBDdyMN22se\nZTplVbOWHzjPCFrsZhu93R-KzOivzqsiXU8b0bLD3CV7LCHgQIHU1wkT9ZOGTc_7\nxQIDAQAB\n-----END PUBLIC KEY-----\n",
        "dsa.1024.1.sig.pub": "-----BEGIN PUBLIC KEY-----\nMIIBtjCCASsGByqGSM44BAEwggEeAoGBAI57u-qVwCcMype4UTxArskRYDt1PPlB\nBk95k-UWh3gtetQtCA9-9DRPMTJ24JY5kUgvTWFNqdfyZjpYkAFMrObhsBve8MFd\nemayh7tRO972YrrE0CQhK1kHqdHyjNgO4GbUxRu0xdUSmqrHWsetMkKRaUgjCyZo\nfrAgtzYct9fnAhUAngwDdthFOjgtZDy9w2-ySytAoMUCgYB2Em1yDdlA8y4MT_gI\nMESmI2lXNJ1bkZ31t61BeDCjCngUK0HwIlRJCe0Tpj1vqqzPnipfTtlZsTuNRr3F\n_1UoVx-P-ZN-Mw1Jokk1W0wF_t3evk4Br1jTAeM6QoBGBhlUuqIuJvHJ9lECCc9x\nQUD0qs3clz3zVVEvxJD9W-O2ggOBhAACgYBFH6-SblZCePPZyIjePGB-o3cMM4Id\nSHzzlT40TBQJubax4rboZFx_ufYh9VzjAcT9YceqGgQPY0kb8nfvKDwqR9ZT744V\nA1HYvk_wy4slgVc2MM9xgfiys-ax3aSGzReFeo6zB-S0Cwvs1i68vJtrqfyrHPOO\nuWENg84BbtBY0g==\n-----END PUBLIC KEY-----\n"
    }
}

test_kr = {
    "test_1": {
        "1": "key_1"
    },
    "test_2": {
        "2": "key_2"
    },
    "test_3": {
        "3": "key_3"
    }
}

test_export = {
    "test_1": {
        "1": "key_1"
    },
    "test_3": {
        "3": "key_3"
    }
}

class TestPKFernet:
    # test roundtrip of ecc
    def test_ecc(self):
        pf = PKFernet(pr_kr, pu_kr)
        for i in xrange(20):
            msg = urlsafe_b64encode(os.urandom(40))
            adata = urlsafe_b64encode(os.urandom(40))
            ctx = pf.encrypt(msg, "dan_haiwei", "ecc.secp224r1.1.enc.pub", "ecdsa_with_sha256.secp224r1.1.sig.priv", adata, sign_also=True)
            deciphered_msg = pf.decrypt(ctx, "dan_haiwei", verify_also = True)
        assert deciphered_msg == msg
    # test roundtrip of rsa
    def test_rsa(self):
        pf = PKFernet(pr_kr, pu_kr)
        for i in xrange(20):
            msg = urlsafe_b64encode(os.urandom(40))
            adata = urlsafe_b64encode(os.urandom(40))
            ctx = pf.encrypt(msg, "dan_haiwei", "rsa.2048.1.enc.pub", "ecdsa_with_sha256.secp224r1.1.sig.priv", adata, sign_also = True)
            deciphered_msg = pf.decrypt(ctx, "dan_haiwei", verify_also = True)
        assert deciphered_msg == msg        
    # test roundtrip of varying length messages using ecc
    def test_varying_length_msg(self):
        pf = PKFernet(pr_kr, pu_kr)
        for i in xrange(50):
            msg = urlsafe_b64encode(os.urandom(i))
            ctx = pf.encrypt(msg, "dan_haiwei", "ecc.secp224r1.1.enc.pub", "ecdsa_with_sha256.secp224r1.1.sig.priv", "ADATA", sign_also=True)
            deciphered_msg = pf.decrypt(ctx, "dan_haiwei", verify_also = True)
            assert deciphered_msg == msg
    # test roundtrip of varying length adata using ecc
    def test_varying_length_adata(self):
        pf = PKFernet(pr_kr, pu_kr)
        for i in xrange(50):
            adata = urlsafe_b64encode(os.urandom(i))
            ctx = pf.encrypt("MESSAGE", "dan_haiwei", "ecc.secp224r1.1.enc.pub", "ecdsa_with_sha256.secp224r1.1.sig.priv", adata, sign_also=True)
            deciphered_msg = pf.decrypt(ctx, "dan_haiwei", verify_also = True)
            assert deciphered_msg == "MESSAGE"
    # test roundtrip of unsigned message
    def test_unsigned_message(self):
        pf = PKFernet(pr_kr, pu_kr)
        for i in xrange(20):
            msg = urlsafe_b64encode(os.urandom(40))
            adata = urlsafe_b64encode(os.urandom(40))
            ctx = pf.encrypt(msg, "dan_haiwei", "ecc.secp224r1.1.enc.pub", "ecdsa_with_sha256.secp224r1.1.sig.priv", adata, sign_also = False)
            deciphered_msg = pf.decrypt(ctx, "dan_haiwei", verify_also = False)
            assert deciphered_msg == msg
    # test roundtrip of unverified message
    def test_unverified(self):
        pf = PKFernet(pr_kr, pu_kr)
        for i in xrange(20):
            msg = urlsafe_b64encode(os.urandom(40))
            adata = urlsafe_b64encode(os.urandom(40))
            ctx = pf.encrypt(msg, "dan_haiwei", "ecc.secp224r1.1.enc.pub", "ecdsa_with_sha256.secp224r1.1.sig.priv", adata, sign_also = True)
            msg_and_sig = pf.decrypt(ctx, "dan_haiwei", verify_also = False)
            encoded_msg, sig_header, sig = msg_and_sig.split('|')
            deciphered_msg = urlsafe_b64decode(encoded_msg)
            assert deciphered_msg == msg
            assert sig_header and sig # ensure signatures exist, even if we don't check them
    # test raising error of invalid receiver
    def test_invalid_receiver(self):
            pf = PKFernet(pr_kr, pu_kr)
            msg = urlsafe_b64encode(os.urandom(40))
            adata = urlsafe_b64encode(os.urandom(40))
            with pytest.raises(AssertionError):
                ctx = pf.encrypt(msg, "invalid_group", "ecc.secp224r1.1.enc.pub", "ecdsa_with_sha256.secp224r1.1.sig.priv", adata, sign_also = True)
    # test raising error of invalid alias
    def test_invalid_alias(self):
        pf = PKFernet(pr_kr, pu_kr)
        msg = urlsafe_b64encode(os.urandom(40))
        adata = urlsafe_b64encode(os.urandom(40))
        with pytest.raises(AssertionError):
            ctx = pf.encrypt(msg, "dan_haiwei", "ecc.non-existent.1.enc.pub", "ecdsa_with_sha256.secp224r1.1.sig.priv", adata, sign_also = True)
    # test key import function to add new user public keys
    def test_pub_key_import(self):
        pf = PKFernet()

        assert not pf.pub_keyrings # assert empty
        
        rec = "test"
        kr = {"1": "key"}
        pf.import_pub_keys(rec, kr)

        pu_kr = {"test": {"1": "key"}}
        assert pf.pub_keyrings == pu_kr
    # test public key export function
    def test_export_pub_keys(self):
        pf = PKFernet(pr_kr, test_kr)
        assert pf.export_pub_keys(["test_1", "test_3"]) == test_export
        assert pf.export_pub_keys() == test_kr        
    # test example encryption given by rahul
    def test_rahul_enc_msg(self):
        pf = PKFernet(pr_kr, pu_kr)
        correct_msg = 'Hello from rahul to daniel and haiwei'
        rahul_ctx = '|ZWNjLnNlY3Q1NzFyMS4xLmVuYy5wdWI=|-----BEGIN PUBLIC KEY-----\nMIGnMBAGByqGSM49AgEGBSuBBAAnA4GSAAQFwCwWOH-JiYmwH2Cijob4gKSaz32a\nrCG83ffhPU9omLe08tAdTysSlW1cfjFY7TWwUNi2gP06XyW0P26_3HpsoNONvP-K\n2dUBnk5FaTQddfTxqhZvWEHW46c8tTXjFugHs_YSgoneQBC_uC24dyhs81Y38jvb\neBibEbxcyJhoXu8ERQwTGuNEmrXo0yPLoO8=\n-----END PUBLIC KEY-----\n|gbqziTAN4d1XX6kGJykgTmd86ChOO_R_EReptxCCFO-8sKibcVXSSyGn6exXE2ijDUYNVP4skLZXsmnlpmQy0r-lNPRfVKKeqScPOytE6MlTn6NedSbmBREOl5ugliFVl7rxHQ2Vg9lDtPKBhxDWaX8='
        msg = urlsafe_b64decode(pf.decrypt(rahul_ctx, "rahul", verify_also = False))
        assert msg == correct_msg
    # test different ecc curves. todo: add more from pub keys
    def test__ecc_curves(self):
        pf = PKFernet(pr_kr, pu_kr)
        for alias in ["ecc.secp224r1.1.enc.pub", "ecc.sect571r1.1.enc.pub"]:
            _, curve, ver, _, _ = alias.split('.')
            msg = urlsafe_b64encode(os.urandom(40))
            adata = urlsafe_b64encode(os.urandom(40))
            ctx = pf.encrypt(msg, "dan_haiwei", alias, "ecdsa_with_sha256.{0}.{1}.sig.priv".format(curve, ver), adata, sign_also=True)
            deciphered_msg = pf.decrypt(ctx, "dan_haiwei", verify_also = True)
        assert deciphered_msg == msg
