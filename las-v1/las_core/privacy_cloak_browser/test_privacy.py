"""
Test suite for Privacy Cloak Browser.

Run comprehensive tests to verify fingerprint randomization, leak prevention,
and behavioral patterns.
"""

import asyncio
import sys
from typing import Dict, Any

from privacy_cloak_browser import PrivacyEngine
from privacy_cloak_browser.core.config import PrivacyConfig


class PrivacyTester:
    """Comprehensive privacy testing suite."""
    
    def __init__(self):
        self.test_results: Dict[str, Any] = {}
        self.passed_tests = 0
        self.failed_tests = 0
    
    async def test_fingerprint_randomization(self) -> bool:
        """Test that fingerprints are properly randomized."""
        print("\n🧪 Testing Fingerprint Randomization...")
        
        try:
            config = PrivacyConfig(randomize_fingerprint=True)
            engine = PrivacyEngine(config)
            await engine.initialize()
            
            # Generate two fingerprints
            profile1 = await engine.create_browser_session()
            await engine.rotate_identity()
            profile2 = await engine.create_browser_session()
            
            # Verify they're different
            checks = {
                'user_agent_different': profile1['user_agent'] != profile2['user_agent'],
                # Viewport might randomly be the same, so we check if AT LEAST one important thing changed
                'fingerprint_changed': (
                    profile1['user_agent'] != profile2['user_agent'] or
                    profile1['viewport'] != profile2['viewport']
                )
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                print("   ✅ Fingerprints properly randomized")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            else:
                print("   ❌ Fingerprint randomization failed")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            
            await engine.shutdown()
            return all_passed
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def test_network_anonymization(self) -> bool:
        """Test network anonymization (proxy simulation)."""
        print("\n🌐 Testing Network Anonymization...")
        
        try:
            # Test proxy configuration
            config = PrivacyConfig(
                use_proxy=True,
                proxy_url="http://example.com:8080"  # Simulated proxy
            )
            engine = PrivacyEngine(config)
            
            # Mock the verification to avoid actual network call failing
            async def mock_verify():
                return True
            
            engine.network_anonymizer._verify_proxy = mock_verify
            
            # Initialize (which sets proxy)
            await engine.initialize()
            
            # Check proxy config is properly set
            proxy_config = engine.network_anonymizer.get_proxy_config()
            
            if proxy_config and 'server' in proxy_config:
                print("   ✅ Proxy configuration properly set")
                print(f"      • Proxy: {proxy_config['server']}")
                return True
            else:
                print("   ❌ Proxy configuration failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def test_leak_prevention(self) -> bool:
        """Test leak prevention mechanisms."""
        print("\n🛡️ Testing Leak Prevention...")
        
        try:
            config = PrivacyConfig(
                block_webrtc=True,
                use_dns_over_https=True,
                block_media_device_enumeration=True,
            )
            engine = PrivacyEngine(config)
            await engine.initialize()
            
            # Create browser config and check protections applied
            browser_config = await engine.create_browser_session()
            
            # Check that leak prevention args are present
            args = browser_config.get('args', [])
            has_webrtc_block = any('--disable-webrtc' in arg for arg in args)
            has_doh = any('DnsOverHttps' in arg for arg in args)
            
            checks = {
                'webrtc_blocked': has_webrtc_block,
                'dns_over_https': has_doh,
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                print("   ✅ Leak prevention properly configured")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            else:
                print("   ⚠️ Some leak protections may be missing")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            
            await engine.shutdown()
            return all_passed
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def test_behavioral_patterns(self) -> bool:
        """Test behavioral obfuscation patterns."""
        print("\n🤖 Testing Behavioral Patterns...")
        
        try:
            config = PrivacyConfig(enable_human_behavior=True)
            engine = PrivacyEngine(config)
            
            behavior = engine.behavior_obfuscator
            
            # Test timing variations
            delays = [behavior.get_typing_delay() for _ in range(10)]
            clicks = [behavior.get_click_delay() for _ in range(10)]
            
            # Check that delays are randomized
            typing_varied = len(set(delays)) > 5  # At least 5 different values
            click_varied = len(set(clicks)) > 5
            
            # Test Bezier curve generation
            path = behavior.generate_bezier_curve_path((0, 0), (100, 100))
            path_valid = len(path) > 10 and path[0] == (0, 0) and path[-1] == (100, 100)
            
            checks = {
                'typing_delays_varied': typing_varied,
                'click_delays_varied': click_varied,
                'bezier_paths_generated': path_valid,
                'human_behavior_enabled': behavior.passes_human_test(),
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                print("   ✅ Behavioral patterns properly implemented")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            else:
                print("   ⚠️ Some behavioral patterns may need tuning")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            
            return all_passed
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def test_session_isolation(self) -> bool:
        """Test session isolation."""
        print("\n🔒 Testing Session Isolation...")
        
        try:
            config = PrivacyConfig(isolate_sessions=True)
            engine = PrivacyEngine(config)
            await engine.initialize()
            
            # Create isolated profile
            profile1 = await engine.create_browser_session()
            session_dir1 = engine.session_isolator.get_session_dir()
            
            # Rotate and create new profile
            await engine.rotate_identity()
            profile2 = await engine.create_browser_session()
            session_dir2 = engine.session_isolator.get_session_dir()
            
            checks = {
                'session_dir_exists': session_dir2 is not None and session_dir2.exists(),
                'profiles_different': profile1['user_data_dir'] != profile2['user_data_dir'],
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                print("   ✅ Session isolation working correctly")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            else:
                print("   ❌ Session isolation failed")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            
            await engine.shutdown()
            return all_passed
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def test_javascript_injection(self) -> bool:
        """Test JavaScript injection scripts."""
        print("\n💉 Testing JavaScript Injection...")
        
        try:
            config = PrivacyConfig(randomize_fingerprint=True)
            engine = PrivacyEngine(config)
            await engine.initialize()
            
            # Get injection scripts
            anti_detection = engine.fingerprint_randomizer.get_injection_script(
                engine.fingerprint_profile
            )
            leak_prevention = engine.leak_preventer.get_leak_prevention_script()
            
            checks = {
                'anti_detection_script_exists': len(anti_detection) > 100,
                'leak_prevention_script_exists': len(leak_prevention) > 100,
                'webdriver_removal': 'webdriver' in anti_detection,
                'canvas_noise': 'canvas' in anti_detection.lower(),
                'webgl_spoofing': 'WebGL' in anti_detection,
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                print("   ✅ JavaScript injection scripts ready")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            else:
                print("   ⚠️ Some injection scripts may be incomplete")
                for check, result in checks.items():
                    print(f"      • {check}: {result}")
            
            await engine.shutdown()
            return all_passed
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results."""
        print("=" * 60)
        print("PRIVACY CLOAK BROWSER - TEST SUITE")
        print("=" * 60)
        
        tests = [
            ("Fingerprint Randomization", self.test_fingerprint_randomization),
            ("Network Anonymization", self.test_network_anonymization),
            ("Leak Prevention", self.test_leak_prevention),
            ("Behavioral Patterns", self.test_behavioral_patterns),
            ("Session Isolation", self.test_session_isolation),
            ("JavaScript Injection", self.test_javascript_injection),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
                if result:
                    self.passed_tests += 1
                else:
                    self.failed_tests += 1
            except Exception as e:
                print(f"\n❌ {test_name} crashed: {e}")
                results[test_name] = False
                self.failed_tests += 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print("\n" + "-" * 60)
        print(f"Total: {self.passed_tests + self.failed_tests} tests")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        print("=" * 60 + "\n")
        
        return results


async def main():
    """Run test suite."""
    tester = PrivacyTester()
    results = await tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if tester.failed_tests > 0:
        sys.exit(1)
    else:
        print("🎉 All tests passed!\n")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
