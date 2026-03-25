import threading
import time
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.biometric_agent import BiometricGuard

class TestBiometricConcurrency(unittest.TestCase):
    @patch('agents.biometric_agent.DeepFace.verify')
    @patch('agents.biometric_agent.cv2.imwrite')
    @patch('agents.biometric_agent.os.remove')
    @patch('agents.biometric_agent.cv2.VideoCapture')
    def test_concurrent_verifications(self, mock_videocap, mock_remove, mock_imwrite, mock_verify):
        """Verify that multiple threads can call verify_identity without crashing."""
        
        # Mock DeepFace to simulate some processing time
        def slow_verify(*args, **kwargs):
            time.sleep(0.5)
            return {'verified': True, 'distance': 0.1, 'threshold': 0.68}
        
        mock_verify.side_effect = slow_verify
        
        # Mock camera
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())
        mock_videocap.return_value = mock_cap
        
        guard = BiometricGuard()
        
        results = []
        errors = []
        
        def call_verify():
            try:
                # Use a dummy frame to bypass camera opening for speed
                res = guard.verify_identity(frame=MagicMock())
                results.append(res)
            except Exception as e:
                errors.append(e)
        
        # Spawn 5 threads calling verify_identity simultaneously
        threads = []
        for _ in range(5):
            t = threading.Thread(target=call_verify)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        self.assertEqual(len(errors), 0, f"Concurrency errors detected: {errors}")
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))
        
        # Check that unique filenames were used (imwrite called 5 times with different paths)
        # and that the lock ensured sequential execution (verify called 5 times)
        self.assertEqual(mock_verify.call_count, 5)
        
        # Collect paths used in imwrite
        paths = [call.args[0] for call in mock_imwrite.call_args_list]
        self.assertEqual(len(set(paths)), 5, f"Expected 5 unique paths, got: {paths}")
        
    @patch('agents.biometric_agent.DeepFace.verify')
    @patch('agents.biometric_agent.cv2.imwrite')
    @patch('agents.biometric_agent.os.remove')
    def test_safe_remove_retries(self, mock_remove, mock_imwrite, mock_verify):
        """Verify that _safe_remove retries on PermissionError."""
        guard = BiometricGuard()
        
        # Mock os.remove to fail once with PermissionError then succeed
        mock_remove.side_effect = [PermissionError("Locked"), None]
        
        with patch('agents.biometric_agent.os.path.exists', return_value=True):
            with patch('time.sleep') as mock_sleep:
                guard._safe_remove("dummy_path", retries=2, delay=0.1)
                
                self.assertEqual(mock_remove.call_count, 2)
                mock_sleep.assert_called_with(0.1)

if __name__ == '__main__':
    unittest.main()
