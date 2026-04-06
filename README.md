# ai-service

FastAPI 기반의 Bedrock 연동 AI API로, 요청 이력은 DynamoDB에 저장하고 응답 생성과 관측성 데이터 조회는 Bedrock Agent가 담당합니다.

## 개요

이 서비스는 Bedrock에 연결된 AI API입니다. 사용자의 요청을 받고 세션 상태를 관리한 뒤, Bedrock Agent를 통해 로그, 메트릭, 트레이스, 인프라 상태, 장기 이력 등을 조회해 응답을 생성합니다.

핵심 원칙은 다음과 같습니다.

- FastAPI는 요청 처리, 대화 저장, API 라우팅을 담당합니다.
- 실제 분석과 외부 데이터 조회는 Bedrock Agent와 tools가 담당합니다.
- 대화 상태는 DynamoDB에 저장합니다.
- 서비스 간 연결은 대시보드 BFF 또는 다른 클라이언트가 호출하는 형태를 전제로 합니다.

## 처리 흐름

1. 사용자가 `/conversations/{cid}/chat`로 메시지를 보냅니다.
2. FastAPI가 세션 또는 대화 존재 여부를 확인합니다.
3. FastAPI가 DynamoDB에서 최신 요약과 최근 메시지 컨텍스트를 불러옵니다.
4. 사용자 메시지 또는 요청을 DynamoDB에 저장합니다.
5. FastAPI가 Bedrock Agent를 호출합니다.
6. Agent는 필요한 tool을 사용해 AMP, OpenSearch, CloudWatch, S3/Athena, EC2/RDS, ELB/ASG, CloudTrail 등을 조회합니다.
7. 생성된 응답을 FastAPI가 다시 DynamoDB에 저장합니다.
8. 최종 응답이 클라이언트로 반환됩니다.

요약하면, FastAPI 자체가 AMP나 OpenSearch에 직접 붙는 구조가 아니라, Bedrock Agent가 tool을 통해 외부 AWS 자원에 접근하는 구조입니다.

## 엔드포인트

서비스 기본 포트는 `8083`입니다.

| 메서드 | 경로 | 설명 | 요청 바디 | 응답 |
| --- | --- | --- | --- | --- |
| GET | `/` | 데모 실행 상태 확인 | 없음 | 상태 JSON |
| GET | `/health` | 헬스 체크 | 없음 | `{ "status": "ok" }` |
| GET | `/debug/env` | 주요 환경변수 확인 | 없음 | 환경변수 JSON |

현재 레포의 기본 데모는 환경변수 수신 여부를 확인하는 최소 FastAPI 앱입니다. 실제 챗봇 엔드포인트는 이후 Bedrock 연동 구현과 함께 확장하면 됩니다.

### AI 요청/응답 예시

요청:

```json
{
  "message": "최근 1시간 동안 에러율이 왜 올랐는지 알려줘"
}
```

응답:

```json
{
  "message": {
    "id": "message-id",
    "conversation_id": "conversation-id",
    "role": "assistant",
    "content": "...",
    "created_at": "2026-04-06T10:30:00Z"
  }
}
```

## 외부 의존성

### FastAPI가 직접 사용하는 자원

- DynamoDB
  - `chatbot-conversations`: 세션 또는 대화 메타데이터
  - `chatbot-messages`: 메시지와 요약 저장

### Bedrock Agent가 tool을 통해 접근하는 자원

- Amazon Managed Prometheus(AMP)
- OpenSearch
- CloudWatch
- S3
- Athena
- EC2
- RDS
- ELB
- Auto Scaling
- CloudTrail

### 선택적 장기 메모리

- AgentCore Memory
  - 대화 간 반복 정보나 중요한 문맥을 저장할 때 사용합니다.

## 환경 변수

현재 데모가 실제로 읽는 환경 변수는 `chatbot` 폴더에서 쓰던 값만 남겨서 다음 다섯 개입니다.

| 변수 | 설명 |
| --- | --- |
| `AWS_REGION_NAME` | AWS 리전 |
| `BEDROCK_MODEL_ID` | Bedrock 모델 ID |
| `AGENTCORE_MEMORY_ID` | AgentCore Memory ID, 비어 있으면 미사용 |
| `CHATBOT_CONVERSATIONS_TABLE` | 대화 저장용 DynamoDB 테이블명 |
| `CHATBOT_MESSAGES_TABLE` | 메시지 저장용 DynamoDB 테이블명 |

Bedrock 연동 버전으로 확장할 때는 이 값을 기반으로 Agent와 DynamoDB 연동을 이어붙이면 됩니다.

## 로컬 실행 예시

```bash
uvicorn app:app --host 0.0.0.0 --port 8083
```

Docker로 실행하려면 다음과 같이 빌드합니다.

```bash
docker build -t ai-service .
docker run --rm -p 8083:8083 \
  -e AWS_REGION_NAME=ap-northeast-2 \
  -e BEDROCK_MODEL_ID=us.anthropic.claude-3-5-haiku-20241022-v1:0 \
  -e AGENTCORE_MEMORY_ID= \
  -e CHATBOT_CONVERSATIONS_TABLE=chatbot-conversations \
  -e CHATBOT_MESSAGES_TABLE=chatbot-messages \
  ai-service
```

실행 후 `GET /debug/env`를 호출하면 전달된 환경변수를 확인할 수 있습니다.

## 비고

- 이 레포는 Bedrock 기반 AI 기능을 제공하는 백엔드로 사용합니다.
- API 계약은 유지한 채로 프론트엔드와는 BFF를 통해 연결하는 구성이 가장 단순합니다.
- FastAPI 자체에 분석 로직을 다 넣기보다, Bedrock Agent와 tool 계층을 유지하는 편이 확장에 유리합니다.
