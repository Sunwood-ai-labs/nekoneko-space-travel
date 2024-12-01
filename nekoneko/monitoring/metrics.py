"""
アプリケーションメトリクス収集モジュール

このモジュールは、アプリケーションの各種メトリクスを
収集・管理するための機能を提供します。

主な機能:
- 予約数の追跡
- エラー率の監視
- システムリソースの監視
- ユーザーアクティビティの追跡
"""

from prometheus_client import Counter, Gauge, Histogram, REGISTRY, start_http_server
import time
from typing import Dict, Optional
from functools import wraps

# メトリクスの定義
BOOKINGS_TOTAL = Counter(
    'nekoneko_bookings_total',
    '合計予約数',
    ['package_type']
)

ACTIVE_USERS = Gauge(
    'nekoneko_active_users',
    'アクティブユーザー数'
)

ERRORS_TOTAL = Counter(
    'nekoneko_errors_total',
    'エラー発生数',
    ['error_type']
)

REQUEST_LATENCY = Histogram(
    'nekoneko_request_latency_seconds',
    'リクエスト処理時間',
    ['endpoint']
)

# メトリクス管理クラス
class MetricsManager:
    def __init__(self):
        self._active_sessions: Dict[str, float] = {}

    def record_booking(self, package_type: str):
        """予約を記録"""
        BOOKINGS_TOTAL.labels(package_type=package_type).inc()

    def start_user_session(self, user_id: str):
        """ユーザーセッションの開始を記録"""
        self._active_sessions[user_id] = time.time()
        ACTIVE_USERS.inc()

    def end_user_session(self, user_id: str):
        """ユーザーセッションの終了を記録"""
        if user_id in self._active_sessions:
            del self._active_sessions[user_id]
            ACTIVE_USERS.dec()

    def record_error(self, error_type: str):
        """エラーを記録"""
        ERRORS_TOTAL.labels(error_type=error_type).inc()

    @staticmethod
    def measure_latency(endpoint: str):
        """エンドポイントのレイテンシーを測定するデコレータ"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    return func(*args, **kwargs)
                finally:
                    REQUEST_LATENCY.labels(endpoint=endpoint).observe(
                        time.time() - start_time
                    )
            return wrapper
        return decorator

# グローバルなメトリクスマネージャーのインスタンス
metrics_manager = MetricsManager()

# メトリクスエンドポイントの起動
def start_metrics_server(port: int = 8000):
    """
    Prometheusメトリクスサーバーを起動
    
    Args:
        port (int): メトリクスサーバーのポート番号
    """
    start_http_server(port)

# 使用例
if __name__ == "__main__":
    # メトリクスサーバーの起動
    start_metrics_server()
    
    # テスト用のメトリクス生成
    metrics_manager.record_booking("moon_tour")
    metrics_manager.start_user_session("user123")
    time.sleep(1)
    metrics_manager.end_user_session("user123")
    metrics_manager.record_error("database_connection")
    
    @metrics_manager.measure_latency("test_endpoint")
    def test_function():
        time.sleep(0.1)
        return "test"
    
    test_function()
