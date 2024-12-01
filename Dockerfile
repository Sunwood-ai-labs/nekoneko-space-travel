# ベースイメージとしてPython 3.10を使用
FROM python:3.10-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存パッケージをコピーしてインストール
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 環境変数の設定
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# ヘルスチェック用のエンドポイントを設定
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# アプリケーションの起動
CMD ["streamlit", "run", "app.py"]
