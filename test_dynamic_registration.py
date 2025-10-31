"""
Test script for RFC 7591 Dynamic Client Registration
"""
import requests
import json

# Server URL (change this to your deployed URL)
SERVER_URL = "http://localhost:8000"

def test_oauth_metadata():
    """Test OAuth metadata endpoint"""
    print("\n🔍 Testing OAuth Metadata Endpoint...")
    print(f"GET {SERVER_URL}/.well-known/oauth-authorization-server")
    
    response = requests.get(
        f"{SERVER_URL}/.well-known/oauth-authorization-server",
        headers={"Accept": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        metadata = response.json()
        print("\n✅ OAuth Metadata:")
        print(json.dumps(metadata, indent=2))
        
        # Check for registration_endpoint
        if "registration_endpoint" in metadata:
            print(f"\n✅ registration_endpoint found: {metadata['registration_endpoint']}")
            return metadata
        else:
            print("\n❌ registration_endpoint NOT found in metadata!")
            return None
    else:
        print(f"❌ Failed to get metadata: {response.text}")
        return None


def test_dynamic_registration():
    """Test dynamic client registration"""
    print("\n🔍 Testing Dynamic Client Registration...")
    print(f"POST {SERVER_URL}/register")
    
    # Prepare registration request (RFC 7591 format)
    registration_data = {
        "client_name": "ChatGPT Test Client",
        "redirect_uris": [
            "https://chat.openai.com/aip/callback",
            "https://chatgpt.com/aip/callback"
        ],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "client_secret_basic",
        "scope": "openid profile email"
    }
    
    print("\nRequest body:")
    print(json.dumps(registration_data, indent=2))
    
    response = requests.post(
        f"{SERVER_URL}/register",
        json=registration_data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        client_info = response.json()
        print("\n✅ Client Registration Successful!")
        print(json.dumps(client_info, indent=2))
        
        print("\n📝 Save these credentials:")
        print(f"Client ID: {client_info.get('client_id')}")
        print(f"Client Secret: {client_info.get('client_secret')}")
        
        return client_info
    else:
        print(f"❌ Registration failed: {response.text}")
        return None


def test_authorization_flow(client_info):
    """Test that the registered client can start authorization flow"""
    if not client_info:
        print("\n⚠️  Skipping authorization flow test (no client info)")
        return
    
    print("\n🔍 Testing Authorization Flow with Registered Client...")
    
    client_id = client_info.get("client_id")
    redirect_uri = client_info.get("redirect_uris", [])[0]
    
    auth_url = (
        f"{SERVER_URL}/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid profile email"
        f"&state=test_state_123"
    )
    
    print(f"\nAuthorization URL:")
    print(auth_url)
    
    response = requests.get(auth_url, allow_redirects=False)
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Authorization endpoint accepts the registered client!")
        print("   (Login form should be displayed)")
    else:
        print(f"❌ Authorization failed: {response.status_code}")
        print(response.text[:500])


if __name__ == "__main__":
    print("=" * 60)
    print("RFC 7591 Dynamic Client Registration Test")
    print("=" * 60)
    
    # Test 1: Check OAuth metadata
    metadata = test_oauth_metadata()
    
    # Test 2: Register a new client dynamically
    client_info = test_dynamic_registration()
    
    # Test 3: Try to use the registered client
    test_authorization_flow(client_info)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    
    if metadata and client_info:
        print("\n🎉 Your OAuth server now supports RFC 7591 Dynamic Client Registration!")
        print("   ChatGPT and other services can now register themselves automatically.")

