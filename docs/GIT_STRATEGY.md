# Git 브랜치 전략 (Git Branching Strategy)

## 개요

MedTranslate 프로젝트는 **Git Flow** 기반의 브랜치 전략을 사용합니다.

## 브랜치 구조

```
main (프로덕션)
  │
  ├── develop (개발)
  │     │
  │     ├── feature/번역-엔진-개선 (기능 개발)
  │     ├── feature/상담사-대시보드 (기능 개발)
  │     └── feature/채팅-UI-개선 (기능 개발)
  │
  ├── release/v1.0.0 (릴리스 준비)
  │
  └── hotfix/긴급-버그-수정 (긴급 수정)
```

## 브랜치 유형

### 1. `main` 브랜치
- **목적**: 프로덕션 배포용
- **규칙**:
  - 항상 배포 가능한 안정적인 상태 유지
  - 직접 푸시 금지 (Pull Request를 통해서만 병합)
  - 모든 커밋은 태그로 버전 관리 (v1.0.0, v1.1.0 등)
- **병합 소스**: `release/*` 또는 `hotfix/*` 브랜치만 병합 가능

### 2. `develop` 브랜치
- **목적**: 개발 통합 브랜치
- **규칙**:
  - 다음 릴리스를 위한 개발 작업 통합
  - 기능 개발이 완료되면 이 브랜치로 병합
  - CI/CD로 자동 테스트 실행
- **병합 소스**: `feature/*` 브랜치 병합

### 3. `feature/*` 브랜치
- **목적**: 새로운 기능 개발
- **네이밍 규칙**:
  - `feature/기능명` (예: `feature/translation-engine`)
  - `feature/이슈번호-기능명` (예: `feature/42-chat-ui`)
- **생성 위치**: `develop` 브랜치에서 분기
- **병합 대상**: `develop` 브랜치로 병합
- **삭제**: 병합 후 삭제

**예시:**
```bash
# feature 브랜치 생성
git checkout develop
git checkout -b feature/translation-engine

# 작업 후 커밋
git add .
git commit -m "feat: Claude API 번역 엔진 구현"

# develop으로 병합 (Pull Request 사용 권장)
git checkout develop
git merge feature/translation-engine
git branch -d feature/translation-engine
```

### 4. `release/*` 브랜치
- **목적**: 릴리스 준비 및 QA
- **네이밍 규칙**: `release/v버전` (예: `release/v1.0.0`)
- **생성 위치**: `develop` 브랜치에서 분기
- **병합 대상**: `main`과 `develop` 모두 병합
- **작업 내용**: 버전 번호 수정, 문서 업데이트, 버그 수정만
- **삭제**: 병합 후 삭제

**예시:**
```bash
# release 브랜치 생성
git checkout develop
git checkout -b release/v1.0.0

# 버전 업데이트 및 테스트 후
git checkout main
git merge release/v1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"

git checkout develop
git merge release/v1.0.0
git branch -d release/v1.0.0
```

### 5. `hotfix/*` 브랜치
- **목적**: 프로덕션 긴급 버그 수정
- **네이밍 규칙**: `hotfix/버그명` (예: `hotfix/translation-error`)
- **생성 위치**: `main` 브랜치에서 분기
- **병합 대상**: `main`과 `develop` 모두 병합
- **삭제**: 병합 후 삭제

**예시:**
```bash
# hotfix 브랜치 생성
git checkout main
git checkout -b hotfix/translation-error

# 긴급 수정 후
git checkout main
git merge hotfix/translation-error
git tag -a v1.0.1 -m "Hotfix: 번역 오류 수정"

git checkout develop
git merge hotfix/translation-error
git branch -d hotfix/translation-error
```

## 커밋 메시지 규칙

### Conventional Commits 형식 사용

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 종류
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 코드 리팩토링
- `test`: 테스트 코드 추가/수정
- `chore`: 빌드, 설정 파일 수정

### 예시
```bash
feat(translation): Claude API 번역 엔진 통합

- Anthropic Claude API 클라이언트 초기화
- 6개 언어 번역 함수 구현
- 의료 용어집 매칭 로직 추가

Closes #42
```

## Pull Request 규칙

### PR 생성 시 체크리스트
- [ ] 기능 테스트 완료
- [ ] 코드 리뷰 요청
- [ ] 충돌 해결 완료
- [ ] CI/CD 파이프라인 통과
- [ ] 문서 업데이트 (필요 시)

### PR 제목 형식
```
[Type] 간단한 설명

예시:
[Feature] 의료 번역 엔진 구현
[Fix] 채팅방 연결 오류 수정
[Docs] API 문서 업데이트
```

### PR 본문 템플릿
```markdown
## 변경 사항
- 구현한 기능 또는 수정 내용

## 테스트
- 테스트 방법 및 결과

## 스크린샷 (UI 변경 시)
- Before/After 이미지

## 관련 이슈
- Closes #이슈번호
```

## 버전 관리 (Semantic Versioning)

```
v<Major>.<Minor>.<Patch>

예: v1.2.3
```

- **Major**: 하위 호환되지 않는 API 변경
- **Minor**: 하위 호환되는 기능 추가
- **Patch**: 하위 호환되는 버그 수정

## 워크플로우 예시

### 일반적인 기능 개발 플로우
```bash
# 1. develop에서 최신 코드 가져오기
git checkout develop
git pull origin develop

# 2. feature 브랜치 생성
git checkout -b feature/new-feature

# 3. 개발 및 커밋
git add .
git commit -m "feat: 새 기능 구현"

# 4. 원격 저장소에 푸시
git push origin feature/new-feature

# 5. GitHub에서 Pull Request 생성 (develop <- feature/new-feature)

# 6. 코드 리뷰 및 승인 후 병합

# 7. 로컬 브랜치 정리
git checkout develop
git pull origin develop
git branch -d feature/new-feature
```

## Git Hook 설정 (선택사항)

### Pre-commit Hook
```bash
#!/bin/sh
# .git/hooks/pre-commit

# Backend: 코드 포맷팅 및 린트 검사
cd backend
source venv/bin/activate
black app/
flake8 app/

# Frontend: 코드 포맷팅 및 린트 검사
cd ../frontend
npm run lint
```

## 참고 자료
- [Git Flow 모델](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
