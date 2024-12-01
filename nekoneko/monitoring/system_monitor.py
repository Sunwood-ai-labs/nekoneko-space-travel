"""
システム状態監視モジュール

このモジュールは、システムの状態を監視し、
異常を検知するための機能を提供します。

主な機能:
- システムリソースの監視
- 死活監視
- パフォーマンス監視
- アラート通知
"""

import psutil
import time
import threading
from typing import Dict, List, Callable, Optional
from datetime import datetime
import logging
from .logging_config import setup_logging
from .metrics import metrics_manager

class SystemMonitor:
    def __init__(self, 
                 check_interval: int = 60,
                 alert_threshold: Dict[str, float] = None):
        """
        システムモニターの初期化
        
        Args:
            check_interval (int): チェック間隔（秒）
            alert_threshold (Dict[str, float]): アラートしきい値設定
        """
        self.logger = setup_logging(app_name="system_monitor")
        self.check_interval = check_interval
        self.alert_threshold = alert_threshold or {
            "cpu_percent": 80.0,        # CPU使用率のしきい値
            "memory_percent": 85.0,     # メモリ使用率のしきい値
            "disk_percent": 90.0,       # ディスク使用率のしきい値
            "network_error_rate": 0.01  # ネットワークエラー率のしきい値
        }
        
        self.alert_callbacks: List[Callable] = []
        self._stop_monitoring = threading.Event()

    def add_alert_callback(self, callback: Callable[[str, Dict], None]):
        """
        アラート通知用のコールバックを追加
        
        Args:
            callback (Callable): アラート時に呼び出す関数
        """
        self.alert_callbacks.append(callback)

    def check_system_resources(self) -> Dict[str, float]:
        """
        システムリソースの使用状況をチェック
        
        Returns:
            Dict[str, float]: リソース使用状況
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "timestamp": datetime.now().isoformat()
            }
            
            # メトリクスの記録
            for key, value in metrics.items():
                if key != "timestamp":
                    metrics_manager.record_metric(f"system_{key}", value)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"システムリソースのチェックに失敗: {str(e)}", exc_info=True)
            metrics_manager.record_error("system_check_failed")
            return {}

    def check_network_health(self) -> Dict[str, float]:
        """
        ネットワークの状態をチェック
        
        Returns:
            Dict[str, float]: ネットワーク状態
        """
        try:
            net_io = psutil.net_io_counters()
            metrics = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "error_rate": (net_io.errin + net_io.errout) / 
                             (net_io.packets_sent + net_io.packets_recv + 1)
            }
            
            # メトリクスの記録
            for key, value in metrics.items():
                metrics_manager.record_metric(f"network_{key}", value)
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"ネットワーク状態のチェックに失敗: {str(e)}", exc_info=True)
            metrics_manager.record_error("network_check_failed")
            return {}

    def check_application_health(self) -> Dict[str, bool]:
        """
        アプリケーションの状態をチェック
        
        Returns:
            Dict[str, bool]: アプリケーション状態
        """
        health_status = {
            "web_server": self._check_web_server(),
            "database": self._check_database(),
            "redis": self._check_redis(),
            "message_queue": self._check_message_queue()
        }
        
        # メトリクスの記録
        for service, status in health_status.items():
            metrics_manager.record_metric(f"service_{service}_health", 1 if status else 0)
            
        return health_status

    def _check_web_server(self) -> bool:
        """Webサーバーの状態確認"""
        # 実装例: HTTPリクエストでヘルスチェック
        return True

    def _check_database(self) -> bool:
        """データベースの状態確認"""
        # 実装例: DB接続テスト
        return True

    def _check_redis(self) -> bool:
        """Redisの状態確認"""
        # 実装例: Redis接続テスト
        return True

    def _check_message_queue(self) -> bool:
        """メッセージキューの状態確認"""
        # 実装例: キュー接続テスト
        return True

    def alert(self, alert_type: str, details: Dict):
        """
        アラートを発報
        
        Args:
            alert_type (str): アラートの種類
            details (Dict): アラートの詳細情報
        """
        self.logger.warning(f"アラート発生: {alert_type}", extra={"alert_details": details})
        
        # 登録済みのコールバックを実行
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, details)
            except Exception as e:
                self.logger.error(f"アラートコールバックの実行に失敗: {str(e)}", exc_info=True)

    def start_monitoring(self):
        """監視を開始"""
        self.logger.info("システム監視を開始します")
        self._stop_monitoring.clear()
        
        monitoring_thread = threading.Thread(target=self._monitoring_loop)
        monitoring_thread.start()

    def stop_monitoring(self):
        """監視を停止"""
        self.logger.info("システム監視を停止します")
        self._stop_monitoring.set()

    def _monitoring_loop(self):
        """メインの監視ループ"""
        while not self._stop_monitoring.is_set():
            try:
                # システムリソースのチェック
                resources = self.check_system_resources()
                for key, value in resources.items():
                    if key in self.alert_threshold and value > self.alert_threshold[key]:
                        self.alert("resource_threshold_exceeded", {
                            "metric": key,
                            "value": value,
                            "threshold": self.alert_threshold[key]
                        })

                # ネットワーク状態のチェック
                network = self.check_network_health()
                if network.get("error_rate", 0) > self.alert_threshold["network_error_rate"]:
                    self.alert("network_errors", network)

                # アプリケーション状態のチェック
                health = self.check_application_health()
                for service, status in health.items():
                    if not status:
                        self.alert("service_unhealthy", {
                            "service": service,
                            "status": status
                        })

            except Exception as e:
                self.logger.error(f"監視ループでエラーが発生: {str(e)}", exc_info=True)
                metrics_manager.record_error("monitoring_loop_error")

            time.sleep(self.check_interval)

# 使用例
if __name__ == "__main__":
    def alert_handler(alert_type: str, details: Dict):
        print(f"アラート受信: {alert_type}")
        print(f"詳細: {json.dumps(details, indent=2, ensure_ascii=False)}")

    monitor = SystemMonitor(check_interval=30)
    monitor.add_alert_callback(alert_handler)
    
    try:
        monitor.start_monitoring()
        # テスト用に1時間実行
        time.sleep(3600)
    finally:
        monitor.stop_monitoring()
