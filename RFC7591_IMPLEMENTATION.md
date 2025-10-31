# RFC 7591 Dynamic Client Registration 구현

## 📋 개요

이 문서는 Solar System OAuth Server에 RFC 7591 Dynamic Client Registration을 구현한 내용을 설명합니다.

## 🎯 문제점

ChatGPT 커넥터가 OAuth 서버에 연결하려고 할 때 다음 오류가 발생했습니다:

```
registration_endpoint를 찾을 수 없음
```

**원인**: OAuth 서버가 동적 클라이언트 등록(RFC 7591)을 지원하지 않아, ChatGPT가 자동으로 클라이언트를 등록할 수 없었습니다.

## ✅ 해결 방법

### 1. 새로운 엔드포인트 추가: `/register`

**위치**: `main.py` 446-503번 줄

RFC 7591 표준을 따르는 동적 클라이언트 등록 엔드포인트를 구현했습니다.

**요청 형식**:
```json
POST /register
Content-Type: application/json

{
  "client_name": "ChatGPT",
  "redirect_uris": ["https://chat.openai.com/aip/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "scope": "openid profile email"
}
```

**응답 형식**:
```json
{
  "client_id": "client_xxx",
  "client_secret": "yyy",
  "client_id_issued_at": 1234567890,
  "client_secret_expires_at": 0,
  "client_name": "ChatGPT",
  "redirect_uris": ["https://chat.openai.com/aip/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "client_secret_basic",
  "scope": "openid profile email"
}
```

### 2. OAuth 메타데이터 업데이트

**위치**: `main.py` 506-524번 줄

`/.well-known/oauth-authorization-server` 엔드포인트에 `registration_endpoint`를 추가했습니다:

```json
{
  "issuer": "https://your-server.up.railway.app",
  "authorization_endpoint": "https://your-server.up.railway.app/authorize",
  "token_endpoint": "https://your-server.up.railway.app/token",
  "userinfo_endpoint": "https://your-server.up.railway.app/userinfo",
  "registration_endpoint": "https://your-server.up.railway.app/register",  // ← 새로 추가
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
  "code_challenge_methods_supported": ["S256", "plain"],
  "scopes_supported": ["openid", "profile", "email"]
}
```

### 3. 테스트 스크립트 추가

**파일**: `test_dynamic_registration.py`

동적 클라이언트 등록을 테스트하는 스크립트를 추가했습니다:

```bash
python test_dynamic_registration.py
```

이 스크립트는 다음을 테스트합니다:
1. OAuth 메타데이터에 `registration_endpoint`가 있는지 확인
2. 새 클라이언트를 동적으로 등록
3. 등록된 클라이언트로 인증 플로우 시작

## 🔧 구현 세부사항

### 엔드포인트 기능

1. **JSON 요청 파싱**: `Content-Type: application/json` 필수
2. **필수 필드 검증**: `redirect_uris`는 필수, 배열 형식이어야 함
3. **자동 credential 생성**: `client_id`와 `client_secret` 자동 생성
4. **RFC 7591 준수**: 표준 응답 형식 반환

### 보안 고려사항

- `client_id`: `client_` 접두사 + 16바이트 URL-safe 랜덤 문자열
- `client_secret`: 32바이트 URL-safe 랜덤 문자열
- 모든 클라이언트는 in-memory 저장소에 저장 (서버 재시작 시 삭제)

## 📝 사용 방법

### ChatGPT에서 사용

1. **서버 배포** (예: Railway):
   ```
   https://web-production-941fc.up.railway.app
   ```

2. **메타데이터 확인**:
   ```bash
   curl https://web-production-941fc.up.railway.app/.well-known/oauth-authorization-server
   ```

3. **ChatGPT 설정**:
   - ChatGPT 설정 → OAuth 커넥터 추가
   - 서버 URL 입력
   - ChatGPT가 자동으로 `/register`를 호출하여 클라이언트 등록

4. **사용자 인증**:
   - 사용자가 연결 시 `/authorize` 페이지로 리다이렉트
   - Username: `admin`, Password: `admin123` (또는 설정된 자격증명)

### 수동 테스트

```bash
# 1. 서버 시작
python main.py

# 2. 메타데이터 확인
curl http://localhost:8000/.well-known/oauth-authorization-server

# 3. 클라이언트 등록
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Test Client",
    "redirect_uris": ["http://localhost:3000/callback"]
  }'

# 4. 테스트 스크립트 실행
python test_dynamic_registration.py
```

## 🔍 검증 방법

### 1. 메타데이터 검증

```bash
curl -H "Accept: application/json" \
  https://your-server.up.railway.app/.well-known/oauth-authorization-server
```

**확인 사항**:
- ✅ `registration_endpoint` 필드가 존재
- ✅ 값이 `https://your-server.up.railway.app/register`

### 2. 등록 엔드포인트 테스트

```bash
curl -X POST https://your-server.up.railway.app/register \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Test",
    "redirect_uris": ["https://example.com/callback"]
  }'
```

**확인 사항**:
- ✅ HTTP 200 응답
- ✅ `client_id`와 `client_secret` 반환
- ✅ RFC 7591 형식 준수

### 3. 전체 플로우 테스트

```bash
python test_dynamic_registration.py
```

**확인 사항**:
- ✅ 메타데이터 조회 성공
- ✅ 클라이언트 등록 성공
- ✅ 등록된 클라이언트로 인증 시작 가능

## 📚 관련 표준

- **RFC 7591**: OAuth 2.0 Dynamic Client Registration Protocol
  - https://tools.ietf.org/html/rfc7591
  
- **RFC 6749**: The OAuth 2.0 Authorization Framework
  - https://tools.ietf.org/html/rfc6749

- **RFC 8414**: OAuth 2.0 Authorization Server Metadata
  - https://tools.ietf.org/html/rfc8414

## 🚀 배포 후 확인사항

### Railway 배포 후

1. **메타데이터 확인**:
   ```bash
   curl https://web-production-941fc.up.railway.app/.well-known/oauth-authorization-server
   ```

2. **등록 엔드포인트 테스트**:
   ```bash
   curl -X POST https://web-production-941fc.up.railway.app/register \
     -H "Content-Type: application/json" \
     -d '{"client_name":"Test","redirect_uris":["https://example.com/callback"]}'
   ```

3. **ChatGPT에서 연결 시도**

### 예상 결과

✅ ChatGPT가 자동으로 클라이언트 등록 완료  
✅ 사용자가 인증 페이지에서 로그인 가능  
✅ 토큰 발급 및 API 호출 성공

## 🔧 트러블슈팅

### "registration_endpoint not found"

**원인**: 메타데이터에 엔드포인트가 없음

**해결**:
```bash
# 메타데이터 확인
curl https://your-server.up.railway.app/.well-known/oauth-authorization-server | jq .registration_endpoint

# 없다면 서버 재배포 필요
git push
```

### "Invalid JSON in request body"

**원인**: Content-Type이 올바르지 않음

**해결**:
```bash
# 반드시 Content-Type: application/json 헤더 포함
curl -X POST .../register \
  -H "Content-Type: application/json" \
  -d '{"client_name":"Test","redirect_uris":["..."]}'
```

### "redirect_uris is required"

**원인**: redirect_uris가 누락되거나 빈 배열

**해결**:
```json
{
  "client_name": "My App",
  "redirect_uris": ["https://example.com/callback"]  // 최소 1개 필요
}
```

## 📊 변경 파일 목록

1. **main.py**
   - 새 엔드포인트 추가: `POST /register` (446-503줄)
   - 메타데이터 업데이트: `registration_endpoint` 추가 (518줄)
   - 홈페이지 HTML 업데이트 (114줄)

2. **test_dynamic_registration.py** (신규)
   - RFC 7591 동적 등록 테스트 스크립트

3. **README.md**
   - Features 섹션 업데이트
   - Management Endpoints 테이블 업데이트
   - ChatGPT Integration 섹션 추가
   - MCP Server Integration 섹션 업데이트

4. **RFC7591_IMPLEMENTATION.md** (신규)
   - 구현 상세 문서

## ✨ 결론

이제 Solar System OAuth Server는 RFC 7591 Dynamic Client Registration을 완전히 지원합니다. 

ChatGPT, MCP 서버, 그리고 다른 OAuth 클라이언트들이 자동으로 등록하고 인증할 수 있습니다.

**다음 단계**:
1. ✅ 코드 변경 완료
2. 🚀 Railway에 배포
3. 🧪 ChatGPT에서 테스트
4. 🎉 사용 시작!

