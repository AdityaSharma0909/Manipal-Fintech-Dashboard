import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


from radian_backend.settings import BASE_DIR


def extract_cert_and_key_from_p12(p12_file, password):
    from cryptography.hazmat.primitives.serialization import pkcs12

    with open(p12_file, 'rb') as file:
        p12_data = file.read()

    p12 = pkcs12.load_key_and_certificates(p12_data, password, default_backend())
    print(p12)
    private_key = p12[0]
    certificate = p12[1]

    # Serialize the private key to PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize the public certificate to PEM format
    certificate_pem = certificate.public_bytes(
        encoding=serialization.Encoding.PEM
    )

    return private_key_pem, certificate_pem

def write_to_pem_files(private_key_pem, certificate_pem, private_key_file, certificate_file):
    with open(private_key_file, 'wb') as private_key_output:
        private_key_output.write(private_key_pem)

    with open(certificate_file, 'wb') as certificate_output:
        certificate_output.write(certificate_pem)

if __name__=='__main__':
    # Example usage
    p12_file_path = os.path.join(BASE_DIR, "keys/radian_new.p12")
    password = b'radian1234'
    private_key_file_path = os.path.join(BASE_DIR, "keys/client_private_key.pem")
    certificate_file_path = os.path.join(BASE_DIR, "keys/client_public_key.pem")

    private_key_pem, certificate_pem = extract_cert_and_key_from_p12(p12_file_path, password)

    write_to_pem_files(private_key_pem, certificate_pem, private_key_file_path, certificate_file_path)
