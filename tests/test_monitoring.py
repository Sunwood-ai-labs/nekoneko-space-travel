"""
監視システムのテストモジュール

このモジュールは、システム監視機能を
テストするためのテストケースを提供します。

テスト対象:
- メトリクス収集
- アラート通知
- ログ記録
- システム状態監視
"""

import unittest
from unittest.mock import Mock, patch
import json
from datetime import datetime
from nekoneko.monitoring.metrics import MetricsManager
from nekoneko.monitoring.alert_notifier import AlertNotifier
from nekoneko.monitoring.system_monitor import SystemMonitor
from nekoneko.monitoring.logging_config import setup_logging

class TestMonitoringSystem(unittest.TestCase):
    def setUp(self):
        """テストの前準備"""
        self.metrics_manager = MetricsManager()
        self.alert_notifier = AlertNotifier()
        self.system_monitor = SystemMonitor()
        self.logger = setup_logging(app_name="test_monitoring")

    def test_metrics_collection(self):
        """メトリクス収集のテスト"""
        # 予約数の記録
        self.metrics_manager.record_booking("moon_tour")
        moon_bookings = self.metrics_manager.get_metric_value("bookings_total", {"package_type": "moon_tour"})
        self.assertEqual(moon_bookings, 1)
        
        # アクティブユーザーの追跡
        self.metrics_manager.start_user_session("user123")
        active_users = self.metrics_manager.get_metric_value("active_users")
        self.assertEqual(active_users, 1)
        
        self.metrics_manager.end_user_session("user123")
        active_users = self.metrics_manager.get_metric_value("active_users")
        self.assertEqual(active_users, 0)
        
        # エラーの記録
        self.metrics_manager.record_error("database_connection")
        error_count = self.metrics_manager.get_metric_value("errors_total", {"error_type": "database_connection"})
        self.assertEqual(error_count, 1)

    @patch('requests.post')
    def test_alert_notifications(self, mock_post):
        """アラート通知のテスト"""
        # Slack通知のテスト
        mock_post.return_value.status_code = 200
        result = self.alert_notifier.send_slack_alert(
            "システム負荷警告",
            "CPU使用率が90%を超えています",
            "error"
        )
        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # メール通知のテスト
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.return_value.__enter__.return_value.send_message.return_value = {}
            result = self.alert_notifier.send_email_alert(
                "システム警告",
                "メモリ使用率が高くなっています",
                ["admin@nekoneko-space.travel"]
            )
            self.assertTrue(result)
            mock_smtp.assert_called_once()
        
        # 複数チャンネルへの同時通知
        results = self.alert_notifier.broadcast_alert(
            "緊急警告",
            "データベース接続エラーが発生しています",
            severity="error",
            email_recipients=["admin@nekoneko-space.travel"]
        )
        self.assertTrue(all(results.values()))

    def test_system_monitoring(self):
        """システム監視のテスト"""
        # システムリソースのチェック
        resources = self.system_monitor.check_system_resources()
        self.assertIn("cpu_percent", resources)
        self.assertIn("memory_percent", resources)
        self.assertIn("disk_percent", resources)
        
        # ネットワーク状態のチェック
        network = self.system_monitor.check_network_health()
        self.assertIn("bytes_sent", network)
        self.assertIn("bytes_recv", network)
        self.assertIn("error_rate", network)
        
        # アプリケーション状態のチェック
        health = self.system_monitor.check_application_health()
        self.assertIn("web_server", health)
        self.assertIn("database", health)
        self.assertIn("redis", health)

    def test_alert_thresholds(self):
        """アラートしきい値のテスト"""
        # CPU使用率のしきい値テスト
        with patch('psutil.cpu_percent', return_value=95):
            resources = self.system_monitor.check_system_resources()
            self.assertTrue(resources["cpu_percent"] > self.system_monitor.alert_threshold["cpu_percent"])
        
        # メモリ使用率のしきい値テスト
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value.percent = 90
            resources = self.system_monitor.check_system_resources()
            self.assertTrue(resources["memory_percent"] > self.system_monitor.alert_threshold["memory_percent"])

    def test_log_rotation(self):
        """ログローテーションのテスト"""
        # 大量のログメッセージを生成
        for i in range(1000):
            self.logger.info(f"Test log message {i}")
        
        # ログファイルのサイズと数を確認
        import os
        log_files = [f for f in os.listdir("logs") if f.startswith("test_monitoring")]
        self.assertGreaterEqual(len(log_files), 1)
        
        # 最新のログファイルの内容を確認
        with open(f"logs/{log_files[-1]}", "r") as f:
            last_line = f.readlines()[-1]
            self.assertIn("Test log message", last_line)

    def test_metric_persistence(self):
        """メトリクスの永続化テスト"""
        # メトリクスの記録
        test_metrics = {
            "cpu_usage": 45.2,
            "memory_usage": 68.7,
            "active_users": 125
        }
        
        for name, value in test_metrics.items():
            self.metrics_manager.record_metric(name, value)
        
        # 保存されたメトリクスの読み込みと検証
        saved_metrics = self.metrics_manager.load_metrics()
        for name, value in test_metrics.items():
            self.assertAlmostEqual(saved_metrics[name], value, places=1)

if __name__ == '__main__':
    unittest.main()
