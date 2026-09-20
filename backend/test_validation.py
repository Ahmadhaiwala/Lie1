"""
Test Lead Validation System
Tests the new 5-stage validation pipeline
"""
import asyncio
from automation.jobs import BaseLeadJob, WebsiteLeadJob


class TestValidation:
    """Test suite for lead validation"""
    
    def __init__(self):
        self.job = WebsiteLeadJob()
    
    def test_content_source_detection(self):
        """Test Stage 1: Content source detection"""
        print("\n" + "="*60)
        print("TEST 1: Content Source Detection")
        print("="*60)
        
        test_cases = [
            ("https://youtube.com/watch?v=123", True, "YouTube video"),
            ("https://reddit.com/r/smallbusiness/comments/abc", True, "Reddit post"),
            ("https://quora.com/How-can-I-improve-SEO", True, "Quora question"),
            ("https://example.com/blog/how-to-seo", True, "Blog article"),
            ("https://mariospizza.com", False, "Business website"),
            ("https://dentistclinic.com/contact", False, "Business contact page"),
        ]
        
        passed = 0
        failed = 0
        
        for url, expected_rejection, description in test_cases:
            is_content = self.job._is_content_source(url)
            status = "✅ PASS" if is_content == expected_rejection else "❌ FAIL"
            
            if is_content == expected_rejection:
                passed += 1
            else:
                failed += 1
            
            print(f"{status} | {description}")
            print(f"  URL: {url}")
            print(f"  Expected rejection: {expected_rejection}, Got: {is_content}")
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0
    
    def test_business_name_validation(self):
        """Test Stage 4: Business name validation"""
        print("\n" + "="*60)
        print("TEST 2: Business Name Validation")
        print("="*60)
        
        test_cases = [
            ("Mario's Pizza Chicago", True, "Valid: Specific business name"),
            ("Sunset Dental Clinic", True, "Valid: Dental clinic with name"),
            ("Green Leaf Spa Boston", True, "Valid: Spa with location"),
            ("Small businesses", False, "Invalid: Generic category"),
            ("Restaurants", False, "Invalid: Plural category"),
            ("How to build a website", False, "Invalid: Question/tutorial"),
            ("YouTube", False, "Invalid: Platform name"),
            ("Best SEO practices", False, "Invalid: Generic phrase"),
            ("null", False, "Invalid: Null value"),
            ("", False, "Invalid: Empty string"),
        ]
        
        passed = 0
        failed = 0
        
        for name, expected_valid, description in test_cases:
            is_valid = self.job._is_valid_business_name(name)
            status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
            
            if is_valid == expected_valid:
                passed += 1
            else:
                failed += 1
            
            print(f"{status} | {description}")
            print(f"  Name: '{name}'")
            print(f"  Expected valid: {expected_valid}, Got: {is_valid}")
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0
    
    def test_saas_agency_detection(self):
        """Test Stage 1: SaaS/Agency detection"""
        print("\n" + "="*60)
        print("TEST 3: SaaS/Agency Detection")
        print("="*60)
        
        test_cases = [
            (
                "https://whatsapp-bot-saas.com",
                "WhatsApp Bot Platform",
                "Get started with our WhatsApp automation platform. Pricing: Free trial, then $99/month. API documentation available. Sign up now!",
                True,
                "SaaS provider"
            ),
            (
                "https://web-design-agency.com",
                "WebDesign Pro",
                "We build beautiful websites for businesses. Our services include web design, development, and SEO. View our portfolio. Hire us today!",
                True,
                "Web agency"
            ),
            (
                "https://mariospizza.com",
                "Mario's Pizza",
                "Welcome to Mario's Pizza. We serve authentic Italian pizza. Call us at 555-1234 or visit us at 123 Main St.",
                False,
                "Regular business"
            ),
        ]
        
        passed = 0
        failed = 0
        
        for url, name, content, expected_rejection, description in test_cases:
            is_saas = self.job._is_saas_or_agency(url, name, content)
            status = "✅ PASS" if is_saas == expected_rejection else "❌ FAIL"
            
            if is_saas == expected_rejection:
                passed += 1
            else:
                failed += 1
            
            print(f"{status} | {description}")
            print(f"  Business: {name}")
            print(f"  Expected rejection: {expected_rejection}, Got: {is_saas}")
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0
    
    def test_search_queries(self):
        """Test that search queries are business-discovery focused"""
        print("\n" + "="*60)
        print("TEST 4: Search Query Quality")
        print("="*60)
        
        # Problem-focused (bad) keywords
        bad_keywords = ["need", "how to", "problem", "help", "looking for", "tutorial"]
        
        # Business-discovery (good) keywords
        good_keywords = ["directory", "listings", "contact", "local", "business"]
        
        website_job = WebsiteLeadJob()
        queries = website_job.search_queries
        
        print(f"Total queries: {len(queries)}")
        print("\nSample queries:")
        for i, query in enumerate(queries[:3], 1):
            print(f"  {i}. {query}")
        
        # Check for bad keywords
        bad_count = 0
        for query in queries:
            query_lower = query.lower()
            if any(keyword in query_lower for keyword in bad_keywords):
                bad_count += 1
                print(f"\n⚠️  Problem-focused query detected: {query}")
        
        # Check for good keywords
        good_count = 0
        for query in queries:
            query_lower = query.lower()
            if any(keyword in query_lower for keyword in good_keywords):
                good_count += 1
        
        print(f"\n📊 Analysis:")
        print(f"  Queries with business-discovery keywords: {good_count}/{len(queries)}")
        print(f"  Queries with problem-focused keywords: {bad_count}/{len(queries)}")
        
        # Pass if most queries are business-focused
        success = (good_count / len(queries)) > 0.5 and bad_count < len(queries) * 0.3
        
        if success:
            print(f"\n✅ PASS: Queries are mostly business-discovery focused")
        else:
            print(f"\n❌ FAIL: Too many problem-focused queries")
        
        return success
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("\n" + "="*60)
        print("LEAD VALIDATION SYSTEM - TEST SUITE")
        print("="*60)
        
        results = {}
        
        # Run tests
        results['content_source'] = self.test_content_source_detection()
        results['business_name'] = self.test_business_name_validation()
        results['saas_agency'] = self.test_saas_agency_detection()
        results['search_queries'] = self.test_search_queries()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(results)
        passed = sum(1 for result in results.values() if result)
        failed = total - passed
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} | {test_name}")
        
        print(f"\n{'='*60}")
        print(f"Total: {passed}/{total} tests passed")
        print(f"{'='*60}\n")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Validation system is working correctly.")
        else:
            print(f"⚠️  {failed} test(s) failed. Please review the implementation.")
        
        return passed == total


def main():
    """Run test suite"""
    tester = TestValidation()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
