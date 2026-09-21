"""
Competitor Filter Test Cases
-----------------------------
Validates that the competitor filter correctly identifies:
  - COMPETITORS (businesses that SELL the service)
  - CUSTOMERS (businesses that NEED the service)

Key Rule: "needs the service" ≠ "sells the service"

Usage:
    python examples/competitor_filter_test.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from intelligence.competitor_filter import CompetitorFilter


# ---------------------------------------------------------------------------
# Test Cases: Website Service
# ---------------------------------------------------------------------------

WEBSITE_COMPETITORS = [
    {
        "business_name": "WebDev Pro Agency",
        "industry": "Web Development Agency",
        "raw_snippet": "We build custom websites for businesses. Our portfolio includes 100+ clients.",
        "website": "https://webdevpro.com",
    },
    {
        "business_name": "Digital Solutions Studio",
        "industry": "Web Design Company",
        "raw_snippet": "Website design services. Get a quote for your new website today!",
        "website": "https://digitalsolutions.agency",
    },
    {
        "business_name": "TechCraft Web Solutions",
        "industry": "Software Development",
        "raw_snippet": "We create responsive websites and web applications for businesses.",
        "website": "https://techcraft-solutions.com",
    },
]

WEBSITE_CUSTOMERS = [
    {
        "business_name": "Royal Spice Restaurant",
        "industry": "Indian Restaurant",
        "raw_snippet": "Popular local restaurant. No website found. Call for reservations.",
        "website": None,
    },
    {
        "business_name": "Smile Dental Clinic",
        "industry": "Dental Clinic",
        "raw_snippet": "Family dentistry services. Open Mon-Fri 9am-6pm.",
        "website": None,
    },
    {
        "business_name": "Joe's Auto Repair",
        "industry": "Auto Repair Shop",
        "raw_snippet": "Honest auto repair since 1995. Call us for all your car needs.",
        "website": None,
    },
]


# ---------------------------------------------------------------------------
# Test Cases: SEO Service
# ---------------------------------------------------------------------------

SEO_COMPETITORS = [
    {
        "business_name": "SEO Masters Agency",
        "industry": "SEO Agency",
        "raw_snippet": "Professional SEO services. We rank your business on page 1. Free SEO audit!",
        "website": "https://seomasters.com",
    },
    {
        "business_name": "Growth Marketing Co",
        "industry": "Digital Marketing Agency",
        "raw_snippet": "Full-service digital marketing including SEO, PPC, and social media management.",
        "website": "https://growthmarketing.co",
    },
    {
        "business_name": "SearchBoost Consulting",
        "industry": "SEO Consultant",
        "raw_snippet": "SEO consulting and implementation. Improve your search rankings today.",
        "website": "https://searchboost.io",
    },
]

SEO_CUSTOMERS = [
    {
        "business_name": "Green Valley Landscaping",
        "industry": "Landscaping Services",
        "raw_snippet": "Professional landscaping services. Serving the local area for 20 years.",
        "website": "https://greenvalleylandscaping.com",
    },
    {
        "business_name": "Bella Salon & Spa",
        "industry": "Beauty Salon",
        "raw_snippet": "Full-service salon. Hair, nails, spa treatments. Walk-ins welcome.",
        "website": "https://bellasalon.com",
    },
]


# ---------------------------------------------------------------------------
# Test Cases: WhatsApp Bot Service
# ---------------------------------------------------------------------------

WHATSAPP_BOT_COMPETITORS = [
    {
        "business_name": "ChatBot Solutions Inc",
        "industry": "Chatbot Development",
        "raw_snippet": "We build WhatsApp bots and AI chatbots for businesses. Automate your customer service!",
        "website": "https://chatbotsolutions.com",
    },
    {
        "business_name": "AutoMate WhatsApp",
        "industry": "WhatsApp Automation",
        "raw_snippet": "WhatsApp Business API integration and bot development services.",
        "website": "https://automatewhatsapp.io",
    },
    {
        "business_name": "ConversAI Agency",
        "industry": "AI Automation Agency",
        "raw_snippet": "AI chatbot development for WhatsApp, Messenger, and web. Book a demo today!",
        "website": "https://conversai-agency.com",
    },
]

WHATSAPP_BOT_CUSTOMERS = [
    {
        "business_name": "Tasty Bites Cafe",
        "industry": "Cafe",
        "raw_snippet": "Local cafe. WhatsApp: +91 12345. Message us to place orders.",
        "website": None,
    },
    {
        "business_name": "QuickFix Plumbing",
        "industry": "Plumbing Services",
        "raw_snippet": "24/7 emergency plumbing. Contact us on WhatsApp for fast service.",
        "website": "https://quickfixplumbing.com",
    },
]


# ---------------------------------------------------------------------------
# Main Test Runner
# ---------------------------------------------------------------------------

def run_tests():
    """Run all competitor filter test cases."""
    
    print("=" * 80)
    print("COMPETITOR FILTER TEST SUITE")
    print("=" * 80)
    print()
    
    filter = CompetitorFilter()
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # ---------------------------------------------------------------------------
    # Test 1: Website Service - Competitors
    # ---------------------------------------------------------------------------
    print("─" * 80)
    print("TEST 1: Website Service - Should REJECT Competitors")
    print("─" * 80)
    
    for business in WEBSITE_COMPETITORS:
        total_tests += 1
        result = filter.analyze(business, "website")
        
        status = "✅ PASS" if result.is_competitor else "❌ FAIL"
        if result.is_competitor:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print(f"\n{status}: {business['business_name']}")
        print(f"  Industry: {business['industry']}")
        print(f"  Is Competitor: {result.is_competitor}")
        print(f"  Confidence: {result.confidence:.0%}")
        if result.evidence:
            print(f"  Evidence: {result.evidence[0]}")
    
    # ---------------------------------------------------------------------------
    # Test 2: Website Service - Customers
    # ---------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("TEST 2: Website Service - Should ACCEPT Customers")
    print("─" * 80)
    
    for business in WEBSITE_CUSTOMERS:
        total_tests += 1
        result = filter.analyze(business, "website")
        
        status = "✅ PASS" if not result.is_competitor else "❌ FAIL"
        if not result.is_competitor:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print(f"\n{status}: {business['business_name']}")
        print(f"  Industry: {business['industry']}")
        print(f"  Is Competitor: {result.is_competitor}")
        print(f"  Confidence: {result.confidence:.0%}")
    
    # ---------------------------------------------------------------------------
    # Test 3: SEO Service - Competitors
    # ---------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("TEST 3: SEO Service - Should REJECT Competitors")
    print("─" * 80)
    
    for business in SEO_COMPETITORS:
        total_tests += 1
        result = filter.analyze(business, "seo")
        
        status = "✅ PASS" if result.is_competitor else "❌ FAIL"
        if result.is_competitor:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print(f"\n{status}: {business['business_name']}")
        print(f"  Industry: {business['industry']}")
        print(f"  Is Competitor: {result.is_competitor}")
        print(f"  Confidence: {result.confidence:.0%}")
        if result.evidence:
            print(f"  Evidence: {result.evidence[0]}")
    
    # ---------------------------------------------------------------------------
    # Test 4: SEO Service - Customers
    # ---------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("TEST 4: SEO Service - Should ACCEPT Customers")
    print("─" * 80)
    
    for business in SEO_CUSTOMERS:
        total_tests += 1
        result = filter.analyze(business, "seo")
        
        status = "✅ PASS" if not result.is_competitor else "❌ FAIL"
        if not result.is_competitor:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print(f"\n{status}: {business['business_name']}")
        print(f"  Industry: {business['industry']}")
        print(f"  Is Competitor: {result.is_competitor}")
        print(f"  Confidence: {result.confidence:.0%}")
    
    # ---------------------------------------------------------------------------
    # Test 5: WhatsApp Bot Service - Competitors
    # ---------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("TEST 5: WhatsApp Bot Service - Should REJECT Competitors")
    print("─" * 80)
    
    for business in WHATSAPP_BOT_COMPETITORS:
        total_tests += 1
        result = filter.analyze(business, "whatsapp_bot")
        
        status = "✅ PASS" if result.is_competitor else "❌ FAIL"
        if result.is_competitor:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print(f"\n{status}: {business['business_name']}")
        print(f"  Industry: {business['industry']}")
        print(f"  Is Competitor: {result.is_competitor}")
        print(f"  Confidence: {result.confidence:.0%}")
        if result.evidence:
            print(f"  Evidence: {result.evidence[0]}")
    
    # ---------------------------------------------------------------------------
    # Test 6: WhatsApp Bot Service - Customers
    # ---------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("TEST 6: WhatsApp Bot Service - Should ACCEPT Customers")
    print("─" * 80)
    
    for business in WHATSAPP_BOT_CUSTOMERS:
        total_tests += 1
        result = filter.analyze(business, "whatsapp_bot")
        
        status = "✅ PASS" if not result.is_competitor else "❌ FAIL"
        if not result.is_competitor:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print(f"\n{status}: {business['business_name']}")
        print(f"  Industry: {business['industry']}")
        print(f"  Is Competitor: {result.is_competitor}")
        print(f"  Confidence: {result.confidence:.0%}")
    
    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    if failed_tests == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed_tests} tests failed - review results above")
    
    print()
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
