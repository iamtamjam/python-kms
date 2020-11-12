# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and


# [START kms_sign_asymmetric]
def sign_asymmetric(project_id, location_id, key_ring_id, key_id, version_id, message):
    """
    Sign a message using the public key part of an asymmetric key.

    Args:
        project_id (string): Google Cloud project ID (e.g. 'my-project').
        location_id (string): Cloud KMS location (e.g. 'us-east1').
        key_ring_id (string): ID of the Cloud KMS key ring (e.g. 'my-key-ring').
        key_id (string): ID of the key to use (e.g. 'my-key').
        version_id (string): Version to use (e.g. '1').
        message (string): Message to sign.

    Returns:
        AsymmetricSignResponse: Signature.

    """

    # Import the client library.
    from google.cloud import kms

    # Import base64 for printing the ciphertext.
    import base64

    # Import hashlib for calculating hashes.
    import hashlib

    # Create the client.
    client = kms.KeyManagementServiceClient()

    # Build the key version name.
    key_version_name = client.crypto_key_version_path(project_id, location_id, key_ring_id, key_id, version_id)

    # Convert the message to bytes.
    message_bytes = message.encode('utf-8')

    # Calculate the hash.
    hash_ = hashlib.sha256(message_bytes).digest()

    # Build the digest.
    #
    # Note: Key algorithms will require a varying hash function. For
    # example, EC_SIGN_P384_SHA384 requires SHA-384.
    digest = {'sha256': hash_}

    # Optional, but recommended: compute digest's CRC32C.
    # See crc32c() function defined below.
    digest_crc32c = crc32c(hash_)

    # Call the API
    sign_response = client.asymmetric_sign(
        request={'name': key_version_name, 'digest': digest, 'digest_crc32c': digest_crc32c})

    # Optional, but recommended: perform integrity verification on sign_response.
    # For more details on ensuring E2E in-transit integrity to and from Cloud KMS visit:
    # https://cloud.google.com/kms/docs/data-integrity-guidelines
    if not sign_response.verified_digest_crc32c:
        raise Exception('The request sent to the server was corrupted in-transit.')
    if not sign_response.name == key_version_name:
        raise Exception('The request sent to the server was corrupted in-transit.')
    if not sign_response.signature_crc32c == crc32c(sign_response.signature):
        raise Exception('The response received from the server was corrupted in-transit.')
    # End integrity verification

    print('Signature: {}'.format(base64.b64encode(sign_response.signature)))
    return sign_response


def crc32c(data):
    """
    Calculates the CRC32C checksum of the provided data.
    Args:
        data: the bytes over which the checksum should be calculated.
    Returns:
        An int representing the CRC32C checksum of the provided bytes.
    """
    import crcmod
    import six
    crc32c_fun = crcmod.predefined.mkPredefinedCrcFun('crc-32c')
    return crc32c_fun(six.ensure_binary(data))
# [END kms_sign_asymmetric]
