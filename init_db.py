"""
In-memory storage initialization script

This script initializes the in-memory storage with:
1. An admin user
2. A sample OAuth2 client for testing
"""
import sys
from storage import storage
from config import settings
import secrets


def create_admin_user():
    """Create admin user"""
    existing_user = storage.get_user_by_username(settings.ADMIN_USERNAME)
    
    if existing_user:
        print(f"✓ Admin user '{settings.ADMIN_USERNAME}' already exists")
        return existing_user
    
    admin_user = storage.create_user(
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        password=settings.ADMIN_PASSWORD,
        full_name="Administrator"
    )
    
    print(f"✓ Created admin user: {settings.ADMIN_USERNAME}")
    print(f"  Email: {settings.ADMIN_EMAIL}")
    print(f"  Password: {settings.ADMIN_PASSWORD}")
    print(f"  ⚠️  CHANGE THE PASSWORD IN PRODUCTION!")
    
    return admin_user


def create_sample_client():
    """Create a sample OAuth2 client for testing"""
    client_id = "mcp_test_client"
    
    existing_client = storage.get_client(client_id)
    
    if existing_client:
        print(f"✓ Sample client '{client_id}' already exists")
        print(f"  Client Secret: {existing_client.client_secret}")
        return existing_client
    
    client_secret = secrets.token_urlsafe(32)
    
    client = storage.create_client(
        client_id=client_id,
        client_secret=client_secret,
        client_name="MCP Test Client",
        redirect_uris=[
            "http://localhost:3000/callback",
            "http://127.0.0.1:3000/callback",
            "http://localhost:8080/callback"
        ],
        scope="openid profile email"
    )
    
    print(f"✓ Created sample OAuth2 client:")
    print(f"  Client ID: {client_id}")
    print(f"  Client Secret: {client_secret}")
    print(f"  Redirect URIs: http://localhost:3000/callback, http://127.0.0.1:3000/callback, http://localhost:8080/callback")
    print(f"  ⚠️  Save these credentials - you'll need them for testing!")
    
    return client


def main():
    """Main initialization function"""
    print("=" * 60)
    print("🌌 Solar System OAuth Server - In-Memory Initialization")
    print("=" * 60)
    print()
    
    try:
        # Create admin user
        print("Setting up admin user...")
        create_admin_user()
        print()
        
        # Create sample client
        print("Setting up sample OAuth2 client...")
        create_sample_client()
        print()
        
        print("=" * 60)
        print("✅ Initialization completed successfully!")
        print("=" * 60)
        print()
        print("⚠️  IMPORTANT: 이 설정은 메모리에만 저장됩니다.")
        print("   서버를 재시작할 때마다 이 스크립트를 다시 실행해야 합니다.")
        print()
        print("Next steps:")
        print("1. Start the server: python main.py")
        print("2. Visit: http://localhost:8000")
        print("3. Test the OAuth flow: python example_client.py")
        print()
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
