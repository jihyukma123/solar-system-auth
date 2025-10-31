"""
Main FastAPI application for OAuth2 server (In-Memory version)
"""
from fastapi import FastAPI, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import secrets
import hashlib
import base64
import jwt
import json
from datetime import datetime, timedelta

from config import settings
from storage import storage

import logging

# 모듈 레벨 logger 생성 (권장)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="OAuth2 server for MCP (Model Context Protocol) authentication - In-Memory Test Version"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} started (In-Memory Mode)")
    print(f"Server running on http://{settings.HOST}:{settings.PORT}")
    print("⚠️  데이터는 메모리에만 저장되며, 서버 재시작 시 모두 사라집니다.")
    
    # Auto-initialize data on startup (especially for Railway deployment)
    print("\n🔄 Auto-initializing data...")
    
    # Create admin user
    existing_user = storage.get_user_by_username(settings.ADMIN_USERNAME)
    if not existing_user:
        admin_user = storage.create_user(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            full_name="Administrator"
        )
        print(f"✓ Created admin user: {settings.ADMIN_USERNAME}")
    else:
        print(f"✓ Admin user already exists: {settings.ADMIN_USERNAME}")
    
    # Create fixed test client (with environment variable support)
    test_client_id = settings.TEST_CLIENT_ID
    existing_client = storage.get_client(test_client_id)
    
    if not existing_client:
        client = storage.create_client(
            client_id=test_client_id,
            client_secret=settings.TEST_CLIENT_SECRET,
            client_name=settings.TEST_CLIENT_NAME,
            redirect_uris=settings.TEST_CLIENT_REDIRECT_URIS,
            scope="openid profile email"
        )
        print(f"✓ Created test client: {test_client_id}")
        print(f"  Client Secret: {settings.TEST_CLIENT_SECRET}")
        print(f"  Redirect URIs: {', '.join(settings.TEST_CLIENT_REDIRECT_URIS)}")
    else:
        print(f"✓ Test client already exists: {test_client_id}")
    
    print("✅ Initialization complete!\n")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return f"""
    <html>
        <head>
            <title>{settings.APP_NAME}</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                h1 {{ color: #333; }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }}
                .endpoint {{ background: #f4f4f4; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                code {{ background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>🌌 {settings.APP_NAME}</h1>
            <p>Version: {settings.APP_VERSION}</p>
            <div class="warning">
                <strong>⚠️ In-Memory Test Mode</strong><br>
                모든 데이터는 메모리에만 저장됩니다. 서버를 재시작하면 데이터가 모두 사라집니다.
            </div>
            <h2>Available Endpoints:</h2>
            <div class="endpoint">
                <strong>GET /authorize</strong> - OAuth2 authorization endpoint
            </div>
            <div class="endpoint">
                <strong>POST /token</strong> - OAuth2 token endpoint
            </div>
            <div class="endpoint">
                <strong>GET /userinfo</strong> - Get user information
            </div>
            <div class="endpoint">
                <strong>POST /register</strong> - RFC 7591 Dynamic Client Registration (for ChatGPT, etc.)
            </div>
            <div class="endpoint">
                <strong>POST /register-client</strong> - Register new OAuth2 client (form-based)
            </div>
            <div class="endpoint">
                <strong>GET /.well-known/oauth-authorization-server</strong> - OAuth metadata
            </div>
            <div class="endpoint">
                <strong>GET /docs</strong> - API documentation
            </div>
            <h2>Quick Start:</h2>
            <ol>
                <li>Initialize data: <code>python init_db.py</code></li>
                <li>Register client or use test client</li>
                <li>Test OAuth flow: <code>python example_client.py</code></li>
            </ol>
        </body>
    </html>
    """


@app.get("/authorize", response_class=HTMLResponse)
async def authorize(
    request: Request,
    client_id: str,
    redirect_uri: str,
    response_type: str = "code",
    scope: Optional[str] = "",
    state: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
):
    """OAuth2 Authorization Endpoint"""
    # Validate client
    client = storage.get_client(client_id)
    if not client:
        raise HTTPException(status_code=400, detail="Invalid client_id")
    
    # Validate redirect_uri
    if redirect_uri not in client.redirect_uris:
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")
    
    # Validate response_type
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Unsupported response_type")
    
    # Return login/consent form
    return f"""
    <html>
        <head>
            <title>Authorization - {settings.APP_NAME}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    max-width: 500px; 
                    margin: 50px auto; 
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h2 {{ color: #333; margin-top: 0; }}
                .client-info {{ 
                    background: #f9f9f9; 
                    padding: 15px; 
                    margin: 20px 0;
                    border-radius: 5px;
                    border-left: 4px solid #4CAF50;
                }}
                input {{ 
                    width: 100%; 
                    padding: 10px; 
                    margin: 10px 0; 
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    box-sizing: border-box;
                }}
                button {{ 
                    width: 100%; 
                    padding: 12px; 
                    background: #4CAF50; 
                    color: white; 
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 10px;
                }}
                button:hover {{ background: #45a049; }}
                .deny {{ background: #f44336; }}
                .deny:hover {{ background: #da190b; }}
                .scope {{ margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🔐 Authorization Required</h2>
                <div class="client-info">
                    <strong>{client.client_name}</strong> is requesting access to your account.
                </div>
                
                <div class="scope">
                    <strong>Requested permissions:</strong><br>
                    {scope or "Basic profile information"}
                </div>
                
                <form method="post" action="/authorize/consent">
                    <input type="hidden" name="client_id" value="{client_id}">
                    <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                    <input type="hidden" name="response_type" value="{response_type}">
                    <input type="hidden" name="scope" value="{scope}">
                    <input type="hidden" name="state" value="{state or ''}">
                    <input type="hidden" name="code_challenge" value="{code_challenge or ''}">
                    <input type="hidden" name="code_challenge_method" value="{code_challenge_method or ''}">
                    
                    <h3>Login</h3>
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    
                    <button type="submit" name="action" value="allow">Authorize</button>
                    <button type="submit" name="action" value="deny" class="deny">Deny</button>
                </form>
                
                <p style="margin-top: 20px; font-size: 12px; color: #666;">
                    For testing, use username: <code>admin</code> and password: <code>admin123</code>
                </p>
            </div>
        </body>
    </html>
    """


@app.post("/authorize/consent")
async def authorize_consent(
    request: Request,
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    response_type: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    action: str = Form(...),
    scope: Optional[str] = Form(""),
    state: Optional[str] = Form(None),
    code_challenge: Optional[str] = Form(None),
    code_challenge_method: Optional[str] = Form(None),
):
    """Handle authorization consent"""
    # Check if user denied
    if action == "deny":
        error_params = f"error=access_denied&error_description=User+denied+authorization"
        if state:
            error_params += f"&state={state}"
        return RedirectResponse(url=f"{redirect_uri}?{error_params}")
    
    # Authenticate user
    user = storage.get_user_by_username(username)
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Validate client
    client = storage.get_client(client_id)
    if not client:
        raise HTTPException(status_code=400, detail="Invalid client_id")
    
    # Generate authorization code
    auth_code = storage.create_authorization_code(
        client_id=client_id,
        user_id=user.id,
        redirect_uri=redirect_uri,
        scope=scope,
        expires_in_minutes=settings.AUTHORIZATION_CODE_EXPIRE_MINUTES,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method
    )
    
    # Redirect back to client with code
    callback_params = f"code={auth_code.code}"
    if state:
        callback_params += f"&state={state}"
    
    return RedirectResponse(url=f"{redirect_uri}?{callback_params}")


@app.post("/token")
async def token(
    request: Request,
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
):
    """OAuth2 Token Endpoint"""
    # Authorization Code Grant
    if grant_type == "authorization_code":
        if not code or not redirect_uri or not client_id:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Validate client
        client = storage.get_client(client_id)
        if not client:
            raise HTTPException(status_code=400, detail="Invalid client")
        
        # Verify client secret (if not a public client)
        if client.client_secret and client.client_secret != client_secret:
            raise HTTPException(status_code=401, detail="Invalid client credentials")
        
        # Validate authorization code
        auth_code = storage.get_authorization_code(code)
        
        if not auth_code or auth_code.client_id != client_id:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        if auth_code.redirect_uri != redirect_uri:
            raise HTTPException(status_code=400, detail="Redirect URI mismatch")
        
        # PKCE verification
        if auth_code.code_challenge:
            if not code_verifier:
                raise HTTPException(status_code=400, detail="code_verifier required")
            
            # Verify code_challenge
            if auth_code.code_challenge_method == "S256":
                # SHA256 hash
                verifier_hash = hashlib.sha256(code_verifier.encode()).digest()
                verifier_challenge = base64.urlsafe_b64encode(verifier_hash).decode().rstrip('=')
                if verifier_challenge != auth_code.code_challenge:
                    raise HTTPException(status_code=400, detail="Invalid code_verifier")
            elif auth_code.code_challenge_method == "plain":
                if code_verifier != auth_code.code_challenge:
                    raise HTTPException(status_code=400, detail="Invalid code_verifier")
            else:
                raise HTTPException(status_code=400, detail="Unsupported code_challenge_method")
        
        # Mark code as used
        storage.mark_code_as_used(code)
        
        # Get user info for ID token
        user = storage.get_user_by_id(auth_code.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate tokens
        token_obj = storage.create_token(
            client_id=client_id,
            user_id=auth_code.user_id,
            scope=auth_code.scope,
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            include_refresh_token=True
        )
        
        # Generate ID token if openid scope is requested
        response = {
            "access_token": token_obj.access_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            "refresh_token": token_obj.refresh_token,
            "scope": auth_code.scope,
        }
        
        if "openid" in auth_code.scope:
            base_url = str(request.base_url).rstrip("/")
            id_token_payload = {
                "iss": base_url,
                "sub": str(user.id),
                "aud": client_id,
                "exp": int((datetime.utcnow() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)).timestamp()),
                "iat": int(datetime.utcnow().timestamp()),
                "email": user.email,
                "name": user.full_name,
            }
            id_token = jwt.encode(id_token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            response["id_token"] = id_token
        
        return response
    
    # Refresh Token Grant
    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Missing refresh_token")
        
        # Validate refresh token
        token_obj = storage.get_token_by_refresh(refresh_token)
        
        if not token_obj:
            raise HTTPException(status_code=400, detail="Invalid or expired refresh token")
        
        # Revoke old token
        storage.revoke_token(token_obj)
        
        # Generate new tokens
        new_token_obj = storage.create_token(
            client_id=token_obj.client_id,
            user_id=token_obj.user_id,
            scope=token_obj.scope,
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            include_refresh_token=True
        )
        
        return {
            "access_token": new_token_obj.access_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            "refresh_token": new_token_obj.refresh_token,
            "scope": token_obj.scope,
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant_type")


@app.get("/userinfo")
async def userinfo(request: Request):
    """Get user information from access token"""
    # Get access token from Authorization header
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    access_token = authorization.replace("Bearer ", "")
    
    # Validate token
    token_obj = storage.get_token(access_token)
    if not token_obj:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get user
    user = storage.get_user_by_id(token_obj.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }


@app.post("/register-client")
async def register_client(
    request: Request,
    client_name: str = Form(...),
    redirect_uris: str = Form(...),  # Comma-separated URIs
    grant_types: Optional[str] = Form("authorization_code,refresh_token"),
    scope: Optional[str] = Form("openid profile email"),
):
    """Register a new OAuth2 client"""
    # Generate client credentials
    client_id = f"client_{secrets.token_urlsafe(16)}"
    client_secret = secrets.token_urlsafe(32)
    
    # Parse redirect URIs
    uri_list = [uri.strip() for uri in redirect_uris.split(",")]
    
    # Create client
    client = storage.create_client(
        client_id=client_id,
        client_secret=client_secret,
        client_name=client_name,
        redirect_uris=uri_list,
        scope=scope
    )
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_name": client_name,
        "redirect_uris": uri_list,
        "message": "Client registered successfully. Save these credentials securely!"
    }


@app.post("/register")
async def dynamic_client_registration(request: Request):
    """
    RFC 7591 Dynamic Client Registration Endpoint
    Allows clients (like ChatGPT) to dynamically register themselves
    """
    try:
        # Parse JSON request body
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON in request body"
        )
    
    # Extract client metadata from request
    client_name = body.get("client_name", "Unnamed Client")
    redirect_uris = body.get("redirect_uris", [])
    
    # Validate redirect URIs
    if not redirect_uris or not isinstance(redirect_uris, list):
        raise HTTPException(
            status_code=400,
            detail="redirect_uris is required and must be a non-empty array"
        )
    
    # Optional fields
    grant_types = body.get("grant_types", ["authorization_code", "refresh_token"])
    response_types = body.get("response_types", ["code"])
    scope = body.get("scope", "openid profile email")
    token_endpoint_auth_method = body.get("token_endpoint_auth_method", "client_secret_basic")
    
    # Generate client credentials
    client_id = f"client_{secrets.token_urlsafe(16)}"
    client_secret = secrets.token_urlsafe(32)
    
    # Create client in storage
    client = storage.create_client(
        client_id=client_id,
        client_secret=client_secret,
        client_name=client_name,
        redirect_uris=redirect_uris,
        scope=scope
    )
    
    # Return RFC 7591 compliant response
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_id_issued_at": int(datetime.utcnow().timestamp()),
        "client_secret_expires_at": 0,  # 0 means it doesn't expire
        "client_name": client_name,
        "redirect_uris": redirect_uris,
        "grant_types": grant_types,
        "response_types": response_types,
        "token_endpoint_auth_method": token_endpoint_auth_method,
        "scope": scope,
    }


@app.get("/.well-known/jwks.json")
async def jwks():
    """JSON Web Key Set (JWKS) endpoint for token verification"""
    # Generate a simple JWK from the secret key
    # In production, use proper RSA keys
    key_id = hashlib.sha256(settings.SECRET_KEY.encode()).hexdigest()[:16]
    
    return {
        "keys": [
            {
                "kty": "oct",  # Symmetric key type
                "kid": key_id,
                "use": "sig",
                "alg": "HS256",
                "k": base64.urlsafe_b64encode(settings.SECRET_KEY.encode()).decode().rstrip("=")
            }
        ]
    }


@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata(request: Request):
    """OAuth 2.0 Authorization Server Metadata"""
    base_url = str(request.base_url).rstrip("/")

    logger.info(f"OAuth metadata: {base_url}")

    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/authorize",
        "token_endpoint": f"{base_url}/token",
        "userinfo_endpoint": f"{base_url}/userinfo",
        "jwks_uri": f"{base_url}/.well-known/jwks.json",
        "registration_endpoint": f"{base_url}/register",
        "response_types_supported": ["code", "token", "id_token", "code id_token"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "scopes_supported": ["openid", "profile", "email"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["HS256"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)