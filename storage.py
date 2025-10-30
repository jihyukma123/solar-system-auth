"""
In-memory storage for OAuth2 server
Simple dictionary-based storage for testing purposes
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User:
    """User model"""
    def __init__(self, user_id: int, username: str, email: str, hashed_password: str, full_name: str = ""):
        self.id = user_id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.is_active = True
        self.created_at = datetime.utcnow()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        # bcrypt has a 72 byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)


class OAuth2Client:
    """OAuth2 client model"""
    def __init__(self, client_id: str, client_secret: str, client_name: str, 
                 redirect_uris: List[str], scope: str = "openid profile email"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_name = client_name
        self.redirect_uris = redirect_uris
        self.scope = scope
        self.grant_types = ["authorization_code", "refresh_token"]
        self.response_types = ["code"]
        self.created_at = datetime.utcnow()


class AuthorizationCode:
    """Authorization code model"""
    def __init__(self, code: str, client_id: str, user_id: int, redirect_uri: str,
                 scope: str = "", expires_in_minutes: int = 10):
        self.code = code
        self.client_id = client_id
        self.user_id = user_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        self.used = False
        self.created_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if code is expired"""
        return datetime.utcnow() > self.expires_at


class Token:
    """Access and refresh token model"""
    def __init__(self, access_token: str, client_id: str, user_id: int, 
                 scope: str = "", expires_in_seconds: int = 3600,
                 refresh_token: Optional[str] = None, refresh_expires_in_days: int = 30):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.user_id = user_id
        self.scope = scope
        self.token_type = "Bearer"
        self.issued_at = datetime.utcnow()
        self.access_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        self.refresh_token_expires_at = None
        if refresh_token:
            self.refresh_token_expires_at = datetime.utcnow() + timedelta(days=refresh_expires_in_days)
        self.revoked = False
    
    def is_expired(self) -> bool:
        """Check if access token is expired"""
        return datetime.utcnow() > self.access_token_expires_at
    
    def is_refresh_token_expired(self) -> bool:
        """Check if refresh token is expired"""
        if not self.refresh_token_expires_at:
            return False
        return datetime.utcnow() > self.refresh_token_expires_at


class InMemoryStorage:
    """In-memory storage for OAuth2 data"""
    
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.users_by_username: Dict[str, User] = {}
        self.clients: Dict[str, OAuth2Client] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        self.tokens: Dict[str, Token] = {}  # key: access_token
        self.tokens_by_refresh: Dict[str, Token] = {}  # key: refresh_token
        self._user_id_counter = 1
    
    # User methods
    def create_user(self, username: str, email: str, password: str, full_name: str = "") -> User:
        """Create a new user"""
        user_id = self._user_id_counter
        self._user_id_counter += 1
        
        hashed_password = User.hash_password(password)
        user = User(user_id, username, email, hashed_password, full_name)
        
        self.users[user_id] = user
        self.users_by_username[username] = user
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users_by_username.get(username)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    # Client methods
    def create_client(self, client_id: str, client_secret: str, client_name: str,
                     redirect_uris: List[str], scope: str = "openid profile email") -> OAuth2Client:
        """Create a new OAuth2 client"""
        client = OAuth2Client(client_id, client_secret, client_name, redirect_uris, scope)
        self.clients[client_id] = client
        return client
    
    def get_client(self, client_id: str) -> Optional[OAuth2Client]:
        """Get client by client_id"""
        return self.clients.get(client_id)
    
    # Authorization code methods
    def create_authorization_code(self, client_id: str, user_id: int, redirect_uri: str,
                                 scope: str = "", expires_in_minutes: int = 10) -> AuthorizationCode:
        """Create a new authorization code"""
        code = secrets.token_urlsafe(32)
        auth_code = AuthorizationCode(code, client_id, user_id, redirect_uri, scope, expires_in_minutes)
        self.authorization_codes[code] = auth_code
        return auth_code
    
    def get_authorization_code(self, code: str) -> Optional[AuthorizationCode]:
        """Get authorization code"""
        auth_code = self.authorization_codes.get(code)
        if auth_code and not auth_code.is_expired() and not auth_code.used:
            return auth_code
        return None
    
    def mark_code_as_used(self, code: str):
        """Mark authorization code as used"""
        if code in self.authorization_codes:
            self.authorization_codes[code].used = True
    
    # Token methods
    def create_token(self, client_id: str, user_id: int, scope: str = "",
                    expires_in_seconds: int = 3600, include_refresh_token: bool = True) -> Token:
        """Create a new token"""
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32) if include_refresh_token else None
        
        token = Token(access_token, client_id, user_id, scope, expires_in_seconds, refresh_token)
        
        self.tokens[access_token] = token
        if refresh_token:
            self.tokens_by_refresh[refresh_token] = token
        
        return token
    
    def get_token(self, access_token: str) -> Optional[Token]:
        """Get token by access_token"""
        token = self.tokens.get(access_token)
        if token and not token.is_expired() and not token.revoked:
            return token
        return None
    
    def get_token_by_refresh(self, refresh_token: str) -> Optional[Token]:
        """Get token by refresh_token"""
        token = self.tokens_by_refresh.get(refresh_token)
        if token and not token.is_refresh_token_expired() and not token.revoked:
            return token
        return None
    
    def revoke_token(self, token: Token):
        """Revoke a token"""
        token.revoked = True


# Global storage instance
storage = InMemoryStorage()

