# 🚀 빠른 시작 가이드 (In-Memory 버전)

Solar System OAuth Server를 빠르게 설정하고 실행하는 방법입니다.

## ⚠️ 중요한 안내

**이 버전은 In-Memory (메모리 기반) 테스트 버전입니다.**

- ✅ 데이터베이스가 필요 없습니다
- ✅ 설치와 설정이 매우 간단합니다
- ⚠️ 서버를 재시작하면 모든 데이터가 사라집니다
- ⚠️ 프로덕션 환경에는 적합하지 않습니다

테스트, 개발, 프로토타이핑에 완벽합니다!

---

## 🚂 Railway 배포 (MCP 서버 연동 추천!)

**Railway에 배포해서 MCP 서버와 연결하시나요?**

👉 **[Railway 배포 가이드 보기](RAILWAY_DEPLOY.md)**

간단 요약:
1. GitHub에 푸시
2. Railway에 연결
3. 환경 변수 설정 (`TEST_CLIENT_SECRET`, `ADMIN_PASSWORD` 등)
4. 자동 배포! → `https://your-app.up.railway.app`

서버는 시작 시 **자동으로 초기화**되어 설정한 클라이언트로 바로 사용 가능합니다.

---

## 📋 전제조건

- Python 3.8 이상
- pip (Python 패키지 관리자)

## 🎯 3분 안에 시작하기

### 1단계: 의존성 설치

requirements.txt의 패키지들이 설치되어 있지 않다면:

```bash
pip install -r requirements.txt
```

필요한 패키지:
- `fastapi` - 웹 프레임워크
- `uvicorn` - ASGI 서버
- `passlib[bcrypt]` - 비밀번호 해싱
- `bcrypt` - 암호화 라이브러리
- `python-multipart` - 폼 데이터 처리

### 2단계: 데이터 초기화

```bash
python init_db.py
```

이 명령은 메모리에 다음을 생성합니다:
- 관리자 계정 (username: `admin`, password: `admin123`)
- 테스트용 OAuth2 클라이언트

**중요**: `client_secret`을 화면에 출력하니 꼭 복사해두세요!

### 3단계: 서버 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload
```

서버가 `http://localhost:8000`에서 시작됩니다.

### 4단계: 테스트

```bash
# 기본 동작 확인
python test_server.py

# 전체 OAuth 플로우 테스트
python example_client.py
```

## 🧪 OAuth 플로우 테스트

### 방법 1: 예제 클라이언트 사용 (가장 쉬움!)

```bash
python example_client.py
```

프롬프트에 따라:
1. 2단계에서 받은 `client_secret` 입력
2. 브라우저가 자동으로 열리면 로그인 (admin/admin123)
3. 인증 후 리다이렉트 URL 복사해서 붙여넣기
4. 완료! 토큰과 사용자 정보를 확인할 수 있습니다

### 방법 2: 브라우저로 수동 테스트

#### 2-1. 브라우저에서 인증 페이지 열기

```
http://localhost:8000/authorize?client_id=mcp_test_client&redirect_uri=http://localhost:3000/callback&response_type=code&scope=openid%20profile%20email&state=test123
```

#### 2-2. 로그인
- Username: `admin`
- Password: `admin123`

#### 2-3. 코드를 토큰으로 교환

리다이렉트 URL에서 `code`를 복사한 후:

```bash
curl -X POST http://localhost:8000/token \
  -d "grant_type=authorization_code" \
  -d "code=받은_코드" \
  -d "redirect_uri=http://localhost:3000/callback" \
  -d "client_id=mcp_test_client" \
  -d "client_secret=받은_client_secret"
```

## 🔧 MCP 서버와 연동하기

### 1. MCP 서버를 OAuth2 클라이언트로 등록

```bash
curl -X POST http://localhost:8000/register-client \
  -d "client_name=My MCP Server" \
  -d "redirect_uris=http://localhost:3000/callback"
```

반환된 `client_id`와 `client_secret`을 저장하세요.

### 2. MCP 서버 설정 파일에 추가

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "OAUTH_AUTH_URL": "http://localhost:8000/authorize",
        "OAUTH_TOKEN_URL": "http://localhost:8000/token",
        "OAUTH_CLIENT_ID": "your_client_id",
        "OAUTH_CLIENT_SECRET": "your_client_secret",
        "OAUTH_REDIRECT_URI": "http://localhost:3000/callback"
      }
    }
  }
}
```

### 3. MCP 클라이언트에서 사용

```python
# Python 예제
from example_client import OAuth2Client

client = OAuth2Client(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:3000/callback",
    authorization_endpoint="http://localhost:8000/authorize",
    token_endpoint="http://localhost:8000/token"
)

# 인증 URL 생성
auth_url, state = client.get_authorization_url()
print(f"Visit: {auth_url}")

# 코드 받은 후 토큰으로 교환
token = client.exchange_code_for_token(code)

# API 요청 시 토큰 사용
headers = {"Authorization": f"Bearer {token['access_token']}"}
```

## 📚 주요 엔드포인트

| 엔드포인트 | 메소드 | 설명 |
|---------|-------|------|
| `/authorize` | GET | OAuth2 인증 페이지 |
| `/token` | POST | 토큰 발급/갱신 |
| `/userinfo` | GET | 사용자 정보 조회 |
| `/register-client` | POST | 새 클라이언트 등록 |
| `/.well-known/oauth-authorization-server` | GET | OAuth2 메타데이터 |
| `/docs` | GET | API 문서 (Swagger UI) |

## 🎨 설정 커스터마이징 (선택사항)

`config.py` 파일을 직접 수정해서 설정 변경 가능:

```python
class Settings:
    # 서버 설정
    HOST = "0.0.0.0"
    PORT = 8000
    
    # 토큰 만료 시간
    ACCESS_TOKEN_EXPIRE_SECONDS = 3600
    REFRESH_TOKEN_EXPIRE_DAYS = 30
    
    # CORS
    CORS_ORIGINS = ["*"]
    
    # 관리자 계정
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"
    ADMIN_EMAIL = "admin@example.com"
```

## ⚠️ In-Memory 버전 사용 시 주의사항

### 알아두어야 할 것들:

1. **서버 재시작 시 데이터 소실**
   - 모든 사용자, 클라이언트, 토큰이 사라집니다
   - `python init_db.py`를 다시 실행해야 합니다

2. **동시 요청 제한**
   - 많은 동시 요청을 처리하기 어렵습니다
   - 테스트/개발 용도로만 사용하세요

3. **프로덕션 부적합**
   - 실제 서비스에는 사용하지 마세요
   - 데이터베이스 버전이 필요합니다

### 이런 용도로 완벽합니다:

- ✅ MCP 서버 OAuth 통합 테스트
- ✅ OAuth 2.0 플로우 학습
- ✅ 빠른 프로토타이핑
- ✅ 로컬 개발 환경

## 🐛 문제 해결

### 서버가 시작되지 않음

```bash
# 포트가 사용 중인 경우
lsof -ti:8000 | xargs kill -9

# 또는 다른 포트 사용
PORT=8080 python main.py
```

### "Invalid client_id" 에러

```bash
# 데이터 초기화를 다시 실행
python init_db.py
```

### 서버 재시작 후 로그인 안 됨

정상입니다! In-memory 버전이므로:
```bash
python init_db.py  # 다시 실행
```

### "Invalid redirect_uri" 에러

- 클라이언트 등록 시 사용한 redirect_uri와 정확히 일치해야 함
- `http://` 또는 `https://` 포함 필수
- 마지막 슬래시(`/`) 확인

## 📖 더 자세한 정보

- **영문 문서**: [README.md](README.md)
- **API 문서**: http://localhost:8000/docs (서버 실행 후)
- **OAuth 2.0 스펙**: RFC 6749

## 🎉 완료!

이제 OAuth 서버가 실행 중입니다!

```bash
# 서버 상태 확인
python test_server.py

# OAuth 플로우 테스트
python example_client.py

# API 문서 확인
open http://localhost:8000/docs
```

## 💡 팁

1. **개발 중에는 --reload 옵션 사용**
   ```bash
   uvicorn main:app --reload
   ```

2. **로그 확인하고 싶다면**
   - 콘솔에 모든 요청이 출력됩니다

3. **여러 클라이언트 테스트**
   ```bash
   curl -X POST http://localhost:8000/register-client \
     -d "client_name=Test Client 2" \
     -d "redirect_uris=http://localhost:4000/callback"
   ```

4. **서버 재시작 시 자동 초기화**
   - 개발 중에는 startup 시 자동으로 초기화하도록 수정 가능
   - `main.py`의 `startup_event`에 `init_db.py` 코드 추가

즐거운 개발 되세요! 🚀

질문이 있으면:
- API 문서 확인: http://localhost:8000/docs
- README 참고: [README.md](README.md)
- OAuth 2.0 스펙: https://datatracker.ietf.org/doc/html/rfc6749
