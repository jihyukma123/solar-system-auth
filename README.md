# 🌌 Solar System OAuth Server (In-Memory Test Version)

A lightweight OAuth 2.0 Authorization Server built with FastAPI, designed for testing MCP (Model Context Protocol) server authentication.

## ⚠️ Important Note

**This is an in-memory test version**. All data is stored in memory and will be lost when the server restarts. This version is perfect for:
- ✅ Development and testing
- ✅ Quick prototyping
- ✅ Learning OAuth 2.0 flows
- ✅ MCP server integration testing

For production use, consider implementing persistent storage (database).

## Features

- ✅ **OAuth 2.0 Authorization Code Flow** with PKCE support
- ✅ **Refresh Token Grant** for long-lived sessions
- ✅ **User Authentication** with bcrypt password hashing
- ✅ **Client Management** with dynamic client registration
- ✅ **In-Memory Storage** - no database required
- ✅ **Standards Compliant** with OAuth 2.0 RFC 6749
- ✅ **Built-in UI** for authorization consent
- ✅ **CORS Support** for cross-origin requests
- ✅ **Minimal Dependencies** - FastAPI, passlib, python-dotenv

## 🚂 Deploy to Railway (Recommended for MCP Integration)

Want to deploy this to Railway for use with your MCP server? **[See Railway Deployment Guide](RAILWAY_DEPLOY.md)**

Quick Railway deployment:
1. Push to GitHub
2. Connect to Railway
3. Set environment variables (`TEST_CLIENT_SECRET`, `ADMIN_PASSWORD`, etc.)
4. Deploy! Railway URL will be: `https://your-app.up.railway.app`

The server will **auto-initialize** on startup with your configured client credentials.

## Quick Start (Local Development)

### 1. Installation

All dependencies are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Initialize Data

Create test user and OAuth client:

```bash
python init_db.py
```

This creates:
- An admin user (default: `admin` / `admin123`)
- A sample OAuth2 client for testing
- **Save the client_secret - you'll need it!**

⚠️ **Remember**: You need to run this every time you restart the server.

### 3. Start the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`

### 4. Test the OAuth Flow

```bash
python example_client.py
```

## API Endpoints

### Core OAuth 2.0 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/authorize` | GET | OAuth2 authorization endpoint (user consent) |
| `/authorize/consent` | POST | Handle user authorization consent |
| `/token` | POST | Exchange code for tokens or refresh tokens |
| `/userinfo` | GET | Get user information (requires Bearer token) |
| `/.well-known/oauth-authorization-server` | GET | OAuth 2.0 metadata discovery |

### Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register-client` | POST | Register a new OAuth2 client |
| `/` | GET | API information and documentation |
| `/docs` | GET | Interactive API documentation (Swagger UI) |

## OAuth 2.0 Flow

### Authorization Code Flow

1. **Client initiates authorization** by redirecting user to:
   ```
   GET /authorize?
     client_id=YOUR_CLIENT_ID&
     redirect_uri=YOUR_REDIRECT_URI&
     response_type=code&
     scope=openid profile email&
     state=random_state_value
   ```

2. **User authenticates and authorizes** the application

3. **Server redirects back** with authorization code:
   ```
   YOUR_REDIRECT_URI?code=AUTHORIZATION_CODE&state=random_state_value
   ```

4. **Client exchanges code for tokens**:
   ```bash
   curl -X POST http://localhost:8000/token \
     -d "grant_type=authorization_code" \
     -d "code=AUTHORIZATION_CODE" \
     -d "redirect_uri=YOUR_REDIRECT_URI" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET"
   ```

5. **Response contains tokens**:
   ```json
   {
     "access_token": "...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "...",
     "scope": "openid profile email"
   }
   ```

### Refresh Token Flow

```bash
curl -X POST http://localhost:8000/token \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN"
```

### Get User Info

```bash
curl -X GET http://localhost:8000/userinfo \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## MCP Server Integration

### 1. Register Your MCP Server as a Client

```bash
curl -X POST http://localhost:8000/register-client \
  -d "client_name=My MCP Server" \
  -d "redirect_uris=http://localhost:3000/callback,http://127.0.0.1:3000/callback"
```

Save the returned `client_id` and `client_secret`.

### 2. Configure Your MCP Server

Add the OAuth configuration to your MCP server:

```json
{
  "oauth": {
    "authorization_endpoint": "http://localhost:8000/authorize",
    "token_endpoint": "http://localhost:8000/token",
    "userinfo_endpoint": "http://localhost:8000/userinfo",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uri": "http://localhost:3000/callback",
    "scopes": ["openid", "profile", "email"]
  }
}
```

### 3. Implement OAuth Flow in Your MCP Client

Your MCP client should:
1. Redirect users to the authorization endpoint
2. Handle the callback with the authorization code
3. Exchange the code for an access token
4. Use the access token to authenticate API requests

## Testing

### Quick Test

```bash
# Test server is running
python test_server.py

# Test full OAuth flow
python example_client.py
```

### Manual Test with cURL

1. **Get authorization URL** (open in browser):
   ```
   http://localhost:8000/authorize?client_id=mcp_test_client&redirect_uri=http://localhost:3000/callback&response_type=code&scope=openid%20profile%20email
   ```

2. **Login with credentials**:
   - Username: `admin`
   - Password: `admin123`

3. **Copy the code from redirect URL** and exchange for token:
   ```bash
   curl -X POST http://localhost:8000/token \
     -d "grant_type=authorization_code" \
     -d "code=YOUR_CODE_HERE" \
     -d "redirect_uri=http://localhost:3000/callback" \
     -d "client_id=mcp_test_client" \
     -d "client_secret=YOUR_CLIENT_SECRET"
   ```

## Configuration

Create a `.env` file to customize settings:

```env
# Application Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-change-this-in-production

# Token Expiration
ACCESS_TOKEN_EXPIRE_SECONDS=3600
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS Origins (comma-separated)
CORS_ORIGINS=*

# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com
```

## Project Structure

```
solar-system-auth/
├── main.py              # FastAPI application and routes
├── storage.py           # In-memory storage implementation
├── config.py            # Configuration and settings
├── init_db.py           # Data initialization script
├── example_client.py    # OAuth flow example
├── test_server.py       # Server test script
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── SETUP.md            # Quick setup guide (Korean)
```

## Architecture

```
┌─────────────────┐
│   MCP Client    │
│   (Your App)    │
└────────┬────────┘
         │
         │ 1. Redirect to /authorize
         ▼
┌─────────────────┐
│  OAuth Server   │◄──── User authenticates
│  (In-Memory)    │
└────────┬────────┘
         │
         │ 2. Return code
         ▼
┌─────────────────┐
│   MCP Client    │
│                 │◄──── 3. Exchange code for token
└─────────────────┘      4. Use token for API calls
```

## Security Considerations

### For Testing

- ✅ Use any credentials for development
- ✅ Test clients can have simple secrets
- ✅ HTTP is acceptable for localhost

### Moving to Production

If you want to use this in production:

1. **Implement Persistent Storage**: Replace in-memory storage with a database
2. **Use HTTPS**: Deploy behind a reverse proxy with SSL/TLS
3. **Strong Secrets**: Generate secure random keys
4. **Environment Variables**: Never commit `.env` files
5. **CORS**: Restrict `CORS_ORIGINS` to specific domains
6. **Rate Limiting**: Add rate limiting middleware
7. **Audit Logging**: Log all authentication attempts

## Troubleshooting

### Server won't start

```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
PORT=8080 python main.py
```

### "Invalid client_id" error

Run `python init_db.py` to initialize test data.

### "Invalid redirect_uri" error

- Ensure the redirect_uri matches exactly what was registered
- Include protocol (http:// or https://)
- Check for trailing slashes

### Token expired

- Access tokens expire after 1 hour by default
- Use refresh token to get a new access token

### Data lost after restart

This is expected! This is an in-memory version. Run `python init_db.py` again after restart.

## Limitations

As an in-memory test version:

- ❌ Data is lost on server restart
- ❌ No concurrent request handling for writes
- ❌ Not suitable for production
- ❌ No token revocation persistence

## Upgrading to Production

To upgrade this to a production-ready system:

1. Replace `storage.py` with database-backed storage (PostgreSQL, MySQL)
2. Add proper session management
3. Implement token blacklisting
4. Add rate limiting and request validation
5. Use proper secrets management
6. Add comprehensive logging
7. Implement proper error handling

## License

This project is provided as-is for testing MCP servers.

## Support

For issues and questions:
1. Check the interactive docs at `/docs`
2. Review the OAuth 2.0 RFC 6749 specification
3. Check MCP documentation for integration details

---

**Built with ❤️ for the MCP ecosystem**

🌌 May your authentication be secure and your tokens ever-refreshing!
