import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure the project root is in sys.path for imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.biometric_agent import BiometricGuard

class TestBiometricGuard(unittest.TestCase):
    @patch('agents.biometric_agent.DeepFace.verify')
    @patch('agents.biometric_agent.os.getenv')
    @patch('agents.biometric_agent.cv2.VideoCapture')
    @patch('agents.biometric_agent.cv2.imwrite')
    @patch('agents.biometric_agent.os.path.exists')
    def test_relaxed_security_allows_higher_distance(self, mock_exists, mock_imwrite, mock_videocap, mock_getenv, mock_verify):
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'RELAXED_SECURITY': 'true',
            'BIOMETRIC_THRESHOLD': '0.68',
            'SECURITY_BYPASS': 'false'
        }.get(key, default)
        # Mock DeepFace result with distance higher than default but below relaxed limit
        mock_verify.return_value = {
            'verified': False,
            'distance': 0.80,
            'threshold': 0.68
        }
        # Mock webcam capture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, 'dummy_frame')
        mock_videocap.return_value = mock_cap
        mock_exists.return_value = False
        guard = BiometricGuard()
        result = guard.verify_identity()
        self.assertTrue(result, "Relaxed security should accept distance 0.80")

    @patch('agents.biometric_agent.DeepFace.verify')
    @patch('agents.biometric_agent.os.getenv')
    @patch('agents.biometric_agent.cv2.VideoCapture')
    @patch('agents.biometric_agent.cv2.imwrite')
    @patch('agents.biometric_agent.os.path.exists')
    def test_strict_security_fails_high_distance(self, mock_exists, mock_imwrite, mock_videocap, mock_getenv, mock_verify):
        mock_getenv.side_effect = lambda key, default=None: {
            'RELAXED_SECURITY': 'false',
            'BIOMETRIC_THRESHOLD': '0.68',
            'SECURITY_BYPASS': 'false'
        }.get(key, default)
        mock_verify.return_value = {
            'verified': False,
            'distance': 0.80,
            'threshold': 0.68
        }
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, 'dummy_frame')
        mock_videocap.return_value = mock_cap
        mock_exists.return_value = False
        guard = BiometricGuard()
        result = guard.verify_identity()
        self.assertFalse(result, "Strict security should reject distance 0.80")

    @patch('agents.biometric_agent.DeepFace.verify')
    @patch('agents.biometric_agent.os.getenv')
    @patch('agents.biometric_agent.cv2.VideoCapture')
    @patch('agents.biometric_agent.cv2.imwrite')
    @patch('agents.biometric_agent.os.path.exists')
    def test_custom_threshold_overrides_default(self, mock_exists, mock_imwrite, mock_videocap, mock_getenv, mock_verify):
        mock_getenv.side_effect = lambda key, default=None: {
            'RELAXED_SECURITY': 'false',
            'BIOMETRIC_THRESHOLD': '0.85',
            'SECURITY_BYPASS': 'false'
        }.get(key, default)
        mock_verify.return_value = {
            'verified': False,
            'distance': 0.80,
            'threshold': 0.68
        }
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, 'dummy_frame')
        mock_videocap.return_value = mock_cap
        mock_exists.return_value = False
        guard = BiometricGuard()
        result = guard.verify_identity()
        self.assertTrue(result, "Custom threshold 0.85 should accept distance 0.80")

    @patch('agents.biometric_agent.DeepFace.verify')
    @patch('agents.biometric_agent.cv2.imwrite')
    @patch('agents.biometric_agent.os.path.exists')
    @patch('agents.biometric_agent.cv2.VideoCapture')
    def test_verify_identity_with_provided_frame(self, mock_videocap, mock_exists, mock_imwrite, mock_verify):
        # Mock DeepFace result
        mock_verify.return_value = {'verified': True, 'distance': 0.1, 'threshold': 0.68}
        mock_exists.return_value = False
        
        guard = BiometricGuard()
        dummy_frame = MagicMock()
        
        result = guard.verify_identity(frame=dummy_frame)
        
        # Ensure it didn't try to open the camera
        mock_videocap.assert_not_called()
        # Ensure it used imwrite to save the provided frame
        mock_imwrite.assert_called_once()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
