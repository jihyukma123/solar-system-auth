# 🚂 Railway 배포 가이드

Solar System OAuth Server를 Railway에 배포하는 방법입니다.

## 📋 사전 준비

1. [Railway](https://railway.app) 계정 (GitHub 연동 추천)
2. GitHub 저장소 (또는 Railway CLI)

## 🚀 배포 방법

### 방법 1: GitHub 연동 (추천)

#### 1. GitHub에 코드 푸시

```bash
# Git 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Initial commit: OAuth server for MCP"

# GitHub 저장소 생성 후
git remote add origin https://github.com/your-username/solar-system-auth.git
git push -u origin main
```

#### 2. Railway에서 프로젝트 생성

1. [Railway Dashboard](https://railway.app/dashboard) 접속
2. "New Project" 클릭
3. "Deploy from GitHub repo" 선택
4. 저장소 선택

#### 3. 환경 변수 설정

Railway Dashboard에서 Variables 탭:

```env
# 필수 설정
TEST_CLIENT_SECRET=your-secure-secret-here
ADMIN_PASSWORD=secure-admin-password

# MCP 서버 redirect_uri 설정 (쉼표로 구분)
TEST_CLIENT_REDIRECT_URIS=https://your-mcp-server.com/callback,http://localhost:3000/callback

# CORS 설정 (MCP 서버 도메인)
CORS_ORIGINS=https://your-mcp-server.com,http://localhost:3000

# 선택 사항
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_SECONDS=3600
```

#### 4. 배포 완료!

Railway가 자동으로 빌드하고 배포합니다.

배포 URL: `https://your-app-name.up.railway.app`

### 방법 2: Railway CLI

```bash
# Railway CLI 설치
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
railway init

# 환경 변수 설정
railway variables set TEST_CLIENT_SECRET="your-secure-secret"
railway variables set ADMIN_PASSWORD="secure-password"

# 배포
railway up
```

## 🔧 MCP 서버 연결 설정

Railway에 배포 후, MCP 서버 설정에 다음 정보를 입력:

```json
{
  "mcpServers": {
    "your-server": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "OAUTH_AUTH_URL": "https://your-app.up.railway.app/authorize",
        "OAUTH_TOKEN_URL": "https://your-app.up.railway.app/token",
        "OAUTH_USERINFO_URL": "https://your-app.up.railway.app/userinfo",
        "OAUTH_CLIENT_ID": "mcp_test_client",
        "OAUTH_CLIENT_SECRET": "your-secure-secret",
        "OAUTH_REDIRECT_URI": "https://your-mcp-server.com/callback"
      }
    }
  }
}
```

## ⚙️ Railway 환경 변수 상세

### 필수 변수

| 변수 | 설명 | 예시 |
|-----|------|------|
| `TEST_CLIENT_SECRET` | OAuth 클라이언트 시크릿 (고정값) | `my-secure-secret-123` |

### 권장 변수

| 변수 | 기본값 | 설명 |
|-----|--------|------|
| `ADMIN_PASSWORD` | `admin123` | 관리자 비밀번호 (보안상 변경 권장) |
| `TEST_CLIENT_REDIRECT_URIS` | `http://localhost:3000/callback,...` | 허용할 redirect URI (쉼표 구분) |
| `CORS_ORIGINS` | `*` | CORS 허용 도메인 (보안상 지정 권장) |
| `SECRET_KEY` | 자동 생성 | JWT 서명 키 |

### 선택 변수

| 변수 | 기본값 | 설명 |
|-----|--------|------|
| `ACCESS_TOKEN_EXPIRE_SECONDS` | `3600` | Access Token 만료 시간 (초) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh Token 만료 시간 (일) |
| `ADMIN_USERNAME` | `admin` | 관리자 사용자명 |
| `ADMIN_EMAIL` | `admin@example.com` | 관리자 이메일 |

## 🧪 배포 후 테스트

### 1. 서버 작동 확인

```bash
curl https://your-app.up.railway.app/
```

### 2. OAuth 메타데이터 확인

```bash
curl https://your-app.up.railway.app/.well-known/oauth-authorization-server
```

### 3. Authorization 플로우 테스트

브라우저에서:
```
https://your-app.up.railway.app/authorize?client_id=mcp_test_client&redirect_uri=http://localhost:3000/callback&response_type=code&scope=openid
```

로그인:
- Username: `admin`
- Password: 설정한 `ADMIN_PASSWORD` (기본값: `admin123`)

### 4. 토큰 교환 테스트

```bash
curl -X POST https://your-app.up.railway.app/token \
  -d "grant_type=authorization_code" \
  -d "code=받은_코드" \
  -d "redirect_uri=http://localhost:3000/callback" \
  -d "client_id=mcp_test_client" \
  -d "client_secret=설정한_TEST_CLIENT_SECRET"
```

## 📊 Railway 모니터링

Railway Dashboard에서 확인 가능:
- 📈 **Metrics**: CPU, 메모리 사용량
- 📝 **Logs**: 실시간 서버 로그
- 🔄 **Deployments**: 배포 히스토리

## ⚠️ In-Memory 주의사항

### Railway 자동 재시작

Railway는 다음 경우 컨테이너를 재시작합니다:
- 새 배포
- 메모리 초과
- 크래시 복구
- 일정 시간 후 자동 재시작

**재시작 시 영향:**
- ✅ **환경 변수로 설정된 클라이언트는 유지됨** (고정 시크릿)
- ✅ 관리자 계정 자동 재생성
- ❌ **발급된 토큰은 모두 무효화됨**
- ❌ 추가로 등록한 클라이언트는 사라짐

### 해결 방법

1. **고정 클라이언트 사용** (환경 변수)
   - `TEST_CLIENT_ID`와 `TEST_CLIENT_SECRET`을 고정
   - MCP 서버는 이 고정 값 사용

2. **토큰 만료 시 refresh token 사용**
   - Access token 만료 시 refresh token으로 갱신
   - Refresh token도 무효화되면 다시 인증

3. **추가 클라이언트는 코드에 하드코딩**
   - `main.py`의 `startup_event`에 추가 클라이언트 생성 코드 추가

## 🔒 보안 권장사항

### Railway 배포 시 꼭 설정하세요:

1. **강력한 시크릿**
```env
TEST_CLIENT_SECRET=$(openssl rand -base64 32)
ADMIN_PASSWORD=$(openssl rand -base64 16)
SECRET_KEY=$(openssl rand -hex 32)
```

2. **CORS 제한**
```env
CORS_ORIGINS=https://your-mcp-server.com
```

3. **HTTPS 사용**
- Railway는 자동으로 HTTPS 제공
- redirect_uri도 https로 설정

## 🐛 문제 해결

### 배포가 실패할 때

**로그 확인:**
```bash
railway logs
```

**일반적인 문제:**
- Python 버전: `runtime.txt` 추가 필요 시
- 패키지 설치 실패: `requirements.txt` 확인

### "Invalid client_secret" 에러

Railway 환경 변수와 MCP 설정의 시크릿이 일치하는지 확인:
```bash
railway variables
```

### CORS 에러

Railway Variables에서 `CORS_ORIGINS` 설정 확인:
```env
CORS_ORIGINS=https://your-mcp-domain.com,http://localhost:3000
```

### 재시작 후 토큰 무효화

정상입니다. In-memory 버전의 한계입니다.
- 사용자에게 다시 로그인 요청
- 또는 DB 버전으로 업그레이드 고려

## 📈 프로덕션으로 발전시키기

현재 In-Memory 버전의 한계를 극복하려면:

1. **Railway PostgreSQL 추가**
   ```bash
   railway add postgresql
   ```

2. **Storage를 Database로 교체**
   - `storage.py` → PostgreSQL 연결
   - SQLAlchemy 재도입
   - 마이그레이션 추가

3. **Redis 세션 저장소**
   - 토큰을 Redis에 캐싱
   - 재시작 시에도 유지

## 💡 팁

### Railway에서 로그 보기
```bash
railway logs --follow
```

### 환경 변수 일괄 설정
```bash
railway variables set TEST_CLIENT_SECRET="secret" \
  ADMIN_PASSWORD="password" \
  CORS_ORIGINS="https://yourdomain.com"
```

### Railway Domain 커스텀 설정
- Railway Dashboard → Settings → Domains
- 커스텀 도메인 추가 가능

## ✅ 체크리스트

Railway 배포 전:
- [ ] `TEST_CLIENT_SECRET` 환경 변수 설정
- [ ] `ADMIN_PASSWORD` 변경
- [ ] `CORS_ORIGINS` MCP 도메인으로 제한
- [ ] `TEST_CLIENT_REDIRECT_URIS`에 MCP callback URL 추가
- [ ] MCP 서버 설정에 Railway URL 입력

배포 후:
- [ ] `/` 접속하여 서버 작동 확인
- [ ] OAuth 메타데이터 확인
- [ ] 테스트 로그인 시도
- [ ] MCP 서버에서 OAuth 플로우 테스트

## 🎉 완료!

이제 Railway에서 OAuth 서버가 실행되고 있으며, MCP 서버와 연결할 수 있습니다!

Railway URL: `https://your-app.up.railway.app`

문제가 있다면:
1. Railway 로그 확인
2. 환경 변수 확인
3. CORS 설정 확인
4. MCP 서버 설정 확인

---

**Note**: 실제 프로덕션 환경에서는 데이터베이스를 사용하는 것을 강력히 권장합니다!



