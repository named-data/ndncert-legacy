import logging
from pyndn.name import Name
from pyndn.interest import Interest
from pyndn.data import Data
from pyndn.encoding.wire_format import WireFormat
from pyndn.util.blob import Blob
from pyndn.key_locator import KeyLocator, KeyLocatorType
from pyndn.security.security_exception import SecurityException
from pyndn.security.policy.policy_manager import PolicyManager
from pyndn.security.certificate.identity_certificate import IdentityCertificate

import base64

class OperatorVerifyPolicyManager(PolicyManager):
    def __init__(self, operator):
        cert = IdentityCertificate()
        cert.wireDecode(base64.b64decode(operator['key']))
        self.cert = cert

    def skipVerifyAndTrust(self, dataOrInterest):
        """
        Never skip verification.

        :param dataOrInterest: The received data packet or interest.
        :type dataOrInterest: Data or Interest
        :return: False.
        :rtype: boolean
        """
        return False

    def requireVerify(self, dataOrInterest):
        """
        Always return true to use the self-verification rule for the received
        data packet or signed interest.

        :param dataOrInterest: The received data packet or interest.
        :type dataOrInterest: Data or Interest
        :return: True.
        :rtype: boolean
        """
        return True

    def checkVerificationPolicy(self, dataOrInterest, stepCount, onVerified,
                                onVerifyFailed, wireFormat = None):

        if wireFormat == None:
            # Don't use a default argument since getDefaultWireFormat can change.
            wireFormat = WireFormat.getDefaultWireFormat()

        if isinstance(dataOrInterest, Data):
            data = dataOrInterest
            # wireEncode returns the cached encoding if available.
            if self._verify(data.getSignature(), data.wireEncode()):
                onVerified(data)
            else:
                onVerifyFailed(data)
        elif isinstance(dataOrInterest, Interest):
            interest = dataOrInterest
            signature = wireFormat.decodeSignatureInfoAndValue(interest.getName().get(-2).getValue().buf(), interest.getName().get(-1).getValue().buf())
            if self._verify(signature, interest.wireEncode()):
                onVerified(interest)
            else:
                onVerifyFailed(interest)
        else:
            raise RuntimeError(
              "checkVerificationPolicy: unrecognized type for dataOrInterest")

        # No more steps, so return a None.
        return None

    def checkSigningPolicy(self, dataName, certificateName):
        """
        Override to always indicate that the signing certificate name and data
        name satisfy the signing policy.

        :param Name dataName: The name of data to be signed.
        :param Name certificateName: The name of signing certificate.
        :return: True to indicate that the signing certificate can be used to
          sign the data.
        :rtype: boolean
        """
        return True

    def inferSigningIdentity(self, dataName):
        """
        Override to indicate that the signing identity cannot be inferred.

        :param Name dataName: The name of data to be signed.
        :return: An empty name because cannot infer.
        :rtype: Name
        """
        return Name()

    def _verify(self, signatureInfo, signedBlob):
        if not signatureInfo.getKeyLocator().getKeyName().isPrefixOf(self.cert.getName()):
            return False

        publicKeyDer = self.cert.getPublicKeyInfo().getKeyDer()
        return self.verifySignature(signatureInfo, signedBlob, publicKeyDer)
