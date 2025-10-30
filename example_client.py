"""
Example OAuth2 Client

This demonstrates how an MCP server would interact with the OAuth server.
Run this after starting the OAuth server (python main.py).
"""
import requests
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import secrets


class OAuth2Client:
    """Simple OAuth2 client for testing"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        authorization_endpoint: str = "http://localhost:8000/authorize",
        token_endpoint: str = "http://localhost:8000/token",
        userinfo_endpoint: str = "http://localhost:8000/userinfo",
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.userinfo_endpoint = userinfo_endpoint
        
        self.access_token = None
        self.refresh_token = None
    
    def get_authorization_url(self, scope: str = "openid profile email", state: str = None):
        """Generate authorization URL"""
        if state is None:
            state = secrets.token_urlsafe(16)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
        }
        
        url = f"{self.authorization_endpoint}?{urlencode(params)}"
        return url, state
    
    def exchange_code_for_token(self, code: str):
        """Exchange authorization code for access token"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        response = requests.post(self.token_endpoint, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token")
        
        return token_data
    
    def refresh_access_token(self):
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        
        response = requests.post(self.token_endpoint, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token")
        
        return token_data
    
    def get_userinfo(self):
        """Get user information using access token"""
        if not self.access_token:
            raise ValueError("No access token available")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = requests.get(self.userinfo_endpoint, headers=headers)
        response.raise_for_status()
        
        return response.json()


def main():
    """Example usage"""
    print("=" * 60)
    print("OAuth2 Client Example")
    print("=" * 60)
    print()
    
    # Configuration
    # Replace these with your actual client credentials
    CLIENT_ID = "mcp_test_client"
    CLIENT_SECRET = input("Enter client_secret (from init_db.py output): ").strip()
    REDIRECT_URI = "http://localhost:3000/callback"
    
    # Create client
    client = OAuth2Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
    )
    
    # Step 1: Get authorization URL
    print("Step 1: Get authorization URL")
    auth_url, state = client.get_authorization_url()
    print(f"Authorization URL: {auth_url}")
    print()
    
    # Step 2: User authorizes (open browser)
    print("Step 2: Opening browser for authorization...")
    print("Please login and authorize the application")
    print("(Use username: admin, password: admin123)")
    print()
    webbrowser.open(auth_url)
    
    # Step 3: Get the redirect URL with code
    print("Step 3: After authorization, you'll be redirected to:")
    print(f"{REDIRECT_URI}?code=...&state={state}")
    print()
    redirect_url = input("Paste the full redirect URL here: ").strip()
    
    # Parse code from redirect URL
    parsed_url = urlparse(redirect_url)
    params = parse_qs(parsed_url.query)
    code = params.get("code", [None])[0]
    
    if not code:
        print("❌ No authorization code found in URL")
        return
    
    print(f"✓ Authorization code received: {code[:20]}...")
    print()
    
    # Step 4: Exchange code for token
    print("Step 4: Exchanging code for access token...")
    try:
        token_data = client.exchange_code_for_token(code)
        print("✓ Token received!")
        print(f"  Access Token: {token_data['access_token'][:20]}...")
        print(f"  Refresh Token: {token_data.get('refresh_token', 'N/A')[:20]}..." if token_data.get('refresh_token') else "")
        print(f"  Expires in: {token_data['expires_in']} seconds")
        print(f"  Scope: {token_data['scope']}")
        print()
    except Exception as e:
        print(f"❌ Error exchanging code: {e}")
        return
    
    # Step 5: Get user info
    print("Step 5: Getting user information...")
    try:
        userinfo = client.get_userinfo()
        print("✓ User info received!")
        print(f"  User ID: {userinfo['sub']}")
        print(f"  Username: {userinfo['username']}")
        print(f"  Email: {userinfo['email']}")
        print(f"  Full Name: {userinfo.get('full_name', 'N/A')}")
        print()
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return
    
    # Step 6: Refresh token (optional)
    if client.refresh_token:
        print("Step 6: Testing token refresh...")
        try:
            new_token_data = client.refresh_access_token()
            print("✓ Token refreshed!")
            print(f"  New Access Token: {new_token_data['access_token'][:20]}...")
            print()
        except Exception as e:
            print(f"❌ Error refreshing token: {e}")
    
    print("=" * 60)
    print("✅ OAuth2 flow completed successfully!")
    print("=" * 60)
    print()
    print("You can now use the access token to authenticate API requests.")
    print(f"Example: curl -H 'Authorization: Bearer {client.access_token}' http://localhost:8000/userinfo")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

