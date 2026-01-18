# AWS Lambda Deployment

## Architektura

- **Lambda Function**: `construction-manager`
- **Container Registry**: ECR `334228654022.dkr.ecr.eu-north-1.amazonaws.com/construction-manager`
- **Database**: RDS PostgreSQL `postgres.cdoie4ussx4x.eu-north-1.rds.amazonaws.com`
- **Region**: `eu-north-1`

## Endpoint

```
https://lkdh2cyypntjdtsl3jptx5ylve0xuuzg.lambda-url.eu-north-1.on.aws
```

### API Routes

- `GET /health` - Health check
- `GET /api/v1/constructions/` - Lista konstrukcji
- `GET /api/v1/materials/` - Lista materiałów
- `GET /api/v1/storage-items/` - Lista elementów magazynowych
- `GET /api/v1/categories/` - Lista kategorii

## Aktualizacja kodu

Po zmianach w kodzie wykonaj:

```bash
# 1. Zaloguj się do ECR
aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 334228654022.dkr.ecr.eu-north-1.amazonaws.com

# 2. Zbuduj nowy obraz (zmień vX na kolejną wersję)
docker buildx build --platform linux/amd64 --provenance=false --sbom=false -t construction-manager:vX --load .

# 3. Otaguj i wypchnij do ECR
docker tag construction-manager:vX 334228654022.dkr.ecr.eu-north-1.amazonaws.com/construction-manager:vX
docker push 334228654022.dkr.ecr.eu-north-1.amazonaws.com/construction-manager:vX

# 4. Zaktualizuj Lambda
aws lambda update-function-code \
  --function-name construction-manager \
  --image-uri 334228654022.dkr.ecr.eu-north-1.amazonaws.com/construction-manager:vX \
  --region eu-north-1
```

## Konfiguracja

### Zmienne środowiskowe Lambda

- `DATABASE_URL` - Connection string do RDS PostgreSQL

### VPC

- **VPC**: `vpc-09e0ee227ded4ff4f`
- **Subnets**: `subnet-088e2358d58f75610`, `subnet-023c5f85776610a82`, `subnet-0ba3a83fc78b64932`
- **Security Group**: `sg-0229d00f0f2d43830`

### IAM Role

- `arn:aws:iam::334228654022:role/construction-lambda-role`

## Logi

```bash
# Ostatnie logi
aws logs tail /aws/lambda/construction-manager --region eu-north-1 --since 5m

# Logi na żywo
aws logs tail /aws/lambda/construction-manager --region eu-north-1 --follow
```

## Koszty

- **Lambda**: Darmowy tier 1M requestów/miesiąc, potem ~$0.20 za 1M requestów
- **ECR**: ~$0.10/GB/miesiąc
- **RDS**: Zależne od instancji (db.t3.micro ma darmowy tier)

## Rozwiązywanie problemów

### Cold start jest wolny
Lambda w VPC ma dłuższy cold start (~2-3s). Dla krytycznych aplikacji rozważ Provisioned Concurrency.

### Timeout przy połączeniu z bazą
Sprawdź czy Security Group RDS (`sg-0229d00f0f2d43830`) ma regułę zezwalającą na ruch z samej siebie na porcie 5432.

### 307 Redirect
FastAPI przekierowuje ścieżki bez trailing slash. Używaj `/api/v1/constructions/` zamiast `/api/v1/constructions`.
