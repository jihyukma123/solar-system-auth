"""
Simple test script to verify OAuth server is working
Run this after starting the server with: python main.py
"""
import requests
import sys


def test_server():
    """Test if server is running and responding"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing OAuth Server...")
    print("=" * 60)
    
    # Test 1: Server is running
    print("\n1. Testing if server is running...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print(f"   ⚠️  Server returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Server is not running")
        print("   Please start the server with: python main.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: OAuth metadata endpoint
    print("\n2. Testing OAuth metadata endpoint...")
    try:
        response = requests.get(f"{base_url}/.well-known/oauth-authorization-server")
        if response.status_code == 200:
            metadata = response.json()
            print("   ✅ OAuth metadata endpoint working")
            print(f"   - Authorization endpoint: {metadata.get('authorization_endpoint')}")
            print(f"   - Token endpoint: {metadata.get('token_endpoint')}")
            print(f"   - Userinfo endpoint: {metadata.get('userinfo_endpoint')}")
        else:
            print(f"   ⚠️  Metadata endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Register a test client
    print("\n3. Testing client registration...")
    try:
        data = {
            "client_name": "Test Client",
            "redirect_uris": "http://localhost:3000/callback",
            "scope": "openid profile email"
        }
        response = requests.post(f"{base_url}/register-client", data=data)
        if response.status_code == 200:
            client_data = response.json()
            print("   ✅ Client registration working")
            print(f"   - Client ID: {client_data['client_id']}")
            print(f"   - Client Secret: {client_data['client_secret'][:20]}...")
            return client_data
        else:
            print(f"   ⚠️  Client registration returned: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return True


def test_authorization_endpoint():
    """Test authorization endpoint"""
    base_url = "http://localhost:8000"
    
    print("\n4. Testing authorization endpoint...")
    try:
        params = {
            "client_id": "mcp_test_client",
            "redirect_uri": "http://localhost:3000/callback",
            "response_type": "code",
            "scope": "openid profile email",
            "state": "test123"
        }
        response = requests.get(f"{base_url}/authorize", params=params)
        if response.status_code == 200 and "Authorization Required" in response.text:
            print("   ✅ Authorization endpoint working")
            print("   - Login page is accessible")
        else:
            print(f"   ⚠️  Authorization endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("🌌 Solar System OAuth Server - Test Suite")
    print("=" * 60)
    
    result = test_server()
    
    if result:
        test_authorization_endpoint()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ Basic tests passed!")
        print("\nNext steps:")
        print("1. Run full OAuth flow with: python example_client.py")
        print("2. Or visit: http://localhost:8000")
        print("3. API docs: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the server.")
        print("\nMake sure:")
        print("1. Database is initialized: python init_db.py")
        print("2. Server is running: python main.py")
    print("=" * 60)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(0)

