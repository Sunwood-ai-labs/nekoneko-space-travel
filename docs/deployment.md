# 🚀 ねこねこスペーストラベル デプロイメントガイド

## 📋 前提条件

- Python 3.8+
- PostgreSQL 13+
- Docker
- AWS/GCPアカウント

## 🌐 インフラストラクチャのセットアップ

### データベースの準備

1. PostgreSQLのセットアップ:
```sql
CREATE DATABASE space_travel;
CREATE USER nekoneko WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE space_travel TO nekoneko;
```

2. 初期マイグレーションの実行:
```bash
python -m alembic upgrade head
```

### 環境変数の設定

1. 本番環境用の`.env`ファイルを作成:
```env
# Database
POSTGRES_USER=nekoneko
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=space_travel
POSTGRES_HOST=your_db_host

# API Keys
OPENAI_API_KEY=your_openai_key
STRIPE_API_KEY=your_stripe_key

# Security
JWT_SECRET_KEY=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Email
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password
```

### Dockerコンテナのビルドとデプロイ

1. Dockerイメージのビルド:
```bash
docker build -t nekoneko-space-travel .
```

2. コンテナの実行:
```bash
docker-compose up -d
```

## 🔒 セキュリティ設定

### SSL/TLS証明書の設定

1. Let's Encryptで証明書を取得:
```bash
certbot certonly --webroot -w /var/www/html -d your-domain.com
```

2. Nginxの設定:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
```

### ファイアウォールの設定

1. 必要なポートのみを開放:
```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5432/tcp  # PostgreSQL（内部ネットワークのみ）
```

## 📊 モニタリングの設定

### Prometheusのセットアップ

1. `prometheus.yml`の設定:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'nekoneko-space'
    static_configs:
      - targets: ['localhost:8501']
```

### Grafanaダッシュボードの設定

1. メトリクスの設定:
   - サーバーリソース使用率
   - アプリケーションパフォーマンス
   - ユーザーアクティビティ
   - 予約状況

## 🔄 CI/CDパイプライン

### GitHub Actionsの設定

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Run tests
        run: pytest
        
      - name: Build and push Docker image
        run: |
          docker build -t nekoneko-space-travel .
          docker push your-registry/nekoneko-space-travel
          
      - name: Deploy to production
        run: |
          ssh ${{ secrets.PROD_SERVER }} "cd /app && docker-compose pull && docker-compose up -d"
```

## 📝 バックアップ設定

### データベースバックアップ

1. 自動バックアップスクリプトの設定:
```bash
#!/bin/bash
BACKUP_DIR="/backup/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U nekoneko space_travel > $BACKUP_DIR/space_travel_$TIMESTAMP.sql
```

2. cronジョブの設定:
```cron
0 2 * * * /scripts/backup_database.sh  # 毎日午前2時にバックアップを実行
```

## 🚨 障害復旧手順

1. データベースの復元:
```bash
psql -U nekoneko space_travel < backup_file.sql
```

2. アプリケーションの再起動:
```bash
docker-compose restart
```

3. ログの確認:
```bash
docker-compose logs -f
```

## 📈 スケーリング戦略

### 水平スケーリング

1. Kubernetesマニフェストの設定:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nekoneko-space-travel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nekoneko-space-travel
  template:
    metadata:
      labels:
        app: nekoneko-space-travel
    spec:
      containers:
      - name: nekoneko-space-travel
        image: your-registry/nekoneko-space-travel
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
```

## 🔍 トラブルシューティング

### よくある問題と解決方法

1. データベース接続エラー:
   - 接続文字列の確認
   - ファイアウォールルールの確認
   - PostgreSQLログの確認

2. メモリ使用量の増加:
   - アプリケーションログの確認
   - メモリリークの調査
   - キャッシュの設定見直し

3. API応答の遅延:
   - ネットワーク設定の確認
   - データベースインデックスの最適化
   - キャッシュの有効化

## 📞 サポート連絡先

- 技術サポート: tech@nekoneko-space.travel
- 緊急連絡先: emergency@nekoneko-space.travel
- オンコール担当: oncall@nekoneko-space.travel
