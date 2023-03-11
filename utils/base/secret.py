from cryptography.fernet import Fernet


class Secret:
    def __init__(self, secret_key: str):
        self.f = Fernet(secret_key.encode('utf-8'))

    def encrypt(self, string):
        """
        加密
        @param string:
        @return:
        """
        string_encrypt = self.f.encrypt(string.encode('utf-8')).decode('utf-8')
        return string_encrypt

    def decrypt(self, string):
        """
        解密
        @param string:
        @return:
        """
        string_decrypt = self.f.decrypt(string.encode('utf-8')).decode('utf-8')
        return string_decrypt


if __name__ == '__main__':
    secret = Secret('7JFhNlgARxgcc3753_iacXYlktR3Jc4Pvr7muyKzh4k=')
    password = '123456'
    encrypt_password = secret.encrypt(password)
    print('encrypt_password', encrypt_password)

    decrypt_password = secret.decrypt(encrypt_password)
    print('decrypt_password', decrypt_password)
