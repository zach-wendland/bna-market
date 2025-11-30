"""
Test script for BNA Market API endpoints

Run this script to verify all API endpoints are working correctly.
Make sure the Flask app is running first: python web/web_app.py
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000/api"


def test_health_check():
    """Test the health check endpoint"""
    print("\n1. Testing Health Check Endpoint")
    print("-" * 50)
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_property_search():
    """Test the property search endpoint"""
    print("\n2. Testing Property Search Endpoint")
    print("-" * 50)

    # Test forsale properties
    print("\nSearching for-sale properties (price: $200k-$400k, 2+ beds):")
    try:
        params = {
            'property_type': 'forsale',
            'min_price': 200000,
            'max_price': 400000,
            'min_beds': 2,
            'page': 1,
            'per_page': 5
        }
        response = requests.get(f"{BASE_URL}/properties/search", params=params)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total properties found: {data['pagination']['total_count']}")
            print(f"Page: {data['pagination']['page']} of {data['pagination']['total_pages']}")
            print(f"Properties on this page: {len(data['properties'])}")
            if data['properties']:
                print(f"\nFirst property sample:")
                prop = data['properties'][0]
                print(f"  Address: {prop.get('address', 'N/A')}")
                print(f"  Price: ${prop.get('price', 0):,}")
                print(f"  Beds/Baths: {prop.get('bedrooms', 'N/A')}/{prop.get('bathrooms', 'N/A')}")
                print(f"  Sqft: {prop.get('livingArea', 'N/A')}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_rental_search():
    """Test rental property search"""
    print("\nSearching rental properties (price: $1500-$2500):")
    try:
        params = {
            'property_type': 'rental',
            'min_price': 1500,
            'max_price': 2500,
            'page': 1,
            'per_page': 5
        }
        response = requests.get(f"{BASE_URL}/properties/search", params=params)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total rentals found: {data['pagination']['total_count']}")
            print(f"Properties on this page: {len(data['properties'])}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_fred_metrics():
    """Test FRED metrics endpoint"""
    print("\n3. Testing FRED Metrics Endpoint")
    print("-" * 50)
    try:
        # Test getting all metrics
        print("\nFetching all FRED metrics:")
        response = requests.get(f"{BASE_URL}/metrics/fred")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total metrics records: {data['count']}")

            if data['metrics']:
                print(f"\nLatest metric sample:")
                metric = data['metrics'][0]
                print(f"  Date: {metric.get('date', 'N/A')}")
                print(f"  Metric: {metric.get('metric_name', 'N/A')}")
                print(f"  Value: {metric.get('value', 'N/A')}")

        # Test filtering by metric name
        print("\nFetching median_price metric:")
        params = {'metric_name': 'median_price'}
        response = requests.get(f"{BASE_URL}/metrics/fred", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"Median price records: {data['count']}")

        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_export_endpoint():
    """Test the export endpoint"""
    print("\n4. Testing Export Endpoint")
    print("-" * 50)
    try:
        print("\nTesting CSV export (forsale properties, $300k-$500k):")
        params = {
            'property_type': 'forsale',
            'min_price': 300000,
            'max_price': 500000
        }
        response = requests.get(f"{BASE_URL}/properties/export", params=params)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")

            # Count rows in CSV
            lines = response.text.strip().split('\n')
            print(f"CSV rows (including header): {len(lines)}")
            print(f"Properties exported: {len(lines) - 1}")

            # Show header
            if lines:
                print(f"\nCSV Header:\n  {lines[0]}")
        else:
            print(f"Error: {response.text}")

        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_error_handling():
    """Test error handling"""
    print("\n5. Testing Error Handling")
    print("-" * 50)
    try:
        # Test missing required parameter
        print("\nTesting missing property_type parameter:")
        response = requests.get(f"{BASE_URL}/properties/search")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        # Test invalid property_type
        print("\nTesting invalid property_type:")
        response = requests.get(f"{BASE_URL}/properties/search", params={'property_type': 'invalid'})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all API tests"""
    print("=" * 50)
    print("BNA Market API Test Suite")
    print("=" * 50)
    print("\nMake sure the Flask app is running:")
    print("  cd web && python web_app.py")
    print("\nOr from project root:")
    print("  python web/web_app.py")

    input("\nPress Enter to start tests...")

    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Property Search", test_property_search()))
    results.append(("Rental Search", test_rental_search()))
    results.append(("FRED Metrics", test_fred_metrics()))
    results.append(("Export Endpoint", test_export_endpoint()))
    results.append(("Error Handling", test_error_handling()))

    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    return 0 if total_passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
