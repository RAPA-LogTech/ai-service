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
| GET | `/` | HTML UI 제공 | 없음 | HTML |
| GET | `/conversations` | 대화 목록 조회 | 없음 | 대화 목록 배열 |
| POST | `/conversations` | 새 대화 생성 | `{ "message": "..." }` | 생성된 대화 정보 |
| GET | `/conversations/{cid}` | 특정 대화와 메시지 조회 | 없음 | 대화 정보와 메시지 배열 |
| DELETE | `/conversations/{cid}` | 대화 및 메시지 삭제 | 없음 | `{ "ok": true }` |
| POST | `/conversations/{cid}/chat` | 메시지 전송 및 AI 응답 생성 | `{ "message": "..." }` | 생성된 assistant 메시지 |

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

실행 시 주로 필요한 환경 변수는 다음과 같습니다.

| 변수 | 설명 |
| --- | --- |
| `AWS_REGION_NAME` | AWS 리전 |
| `BEDROCK_MODEL_ID` | Bedrock 모델 ID |
| `AGENTCORE_MEMORY_ID` | AgentCore Memory ID, 비어 있으면 미사용 |
| `CHATBOT_CONVERSATIONS_TABLE` | 대화 저장용 DynamoDB 테이블명 |
| `CHATBOT_MESSAGES_TABLE` | 메시지 저장용 DynamoDB 테이블명 |
| `AMP_ENDPOINT` | AMP 조회용 엔드포인트 |
| `OPENSEARCH_ENDPOINT` | OpenSearch 엔드포인트 |
| `OPENSEARCH_USER` | OpenSearch 사용자명 |
| `OPENSEARCH_PASSWORD` | OpenSearch 비밀번호 |

## 로컬 실행 예시

```bash
uvicorn app:app --host 0.0.0.0 --port 8083
```

## 비고

- 이 레포는 Bedrock 기반 AI 기능을 제공하는 백엔드로 사용합니다.
- API 계약은 유지한 채로 프론트엔드와는 BFF를 통해 연결하는 구성이 가장 단순합니다.
- FastAPI 자체에 분석 로직을 다 넣기보다, Bedrock Agent와 tool 계층을 유지하는 편이 확장에 유리합니다.