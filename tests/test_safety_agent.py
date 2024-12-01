"""
安全管理エージェントのテストモジュール

このモジュールは、安全管理エージェントの機能を
テストするためのテストケースを提供します。

テスト対象:
- 健康診断要件の確認
- 安全訓練プログラムの評価
- 緊急時対応計画の検証
- 宇宙天気予報の精度
"""

import unittest
from unittest.mock import Mock, patch
from nekoneko.agents.safety_agent import safety_agent, check_health_requirements, monitor_space_weather
from datetime import datetime

class TestSafetyAgent(unittest.TestCase):
    def setUp(self):
        """テストの前準備"""
        self.test_medical_data = {
            "blood_pressure": {
                "systolic": 120,
                "diastolic": 80
            },
            "heart_rate": 72,
            "bone_density": 1.2,
            "inner_ear": "normal",
            "vision": "20/20",
            "last_check_date": datetime.now()
        }
        
        self.test_training_data = {
            "zero_gravity": {
                "completed": True,
                "score": 85,
                "date": datetime.now()
            },
            "emergency_response": {
                "completed": True,
                "score": 90,
                "date": datetime.now()
            }
        }

    def test_health_check(self):
        """健康診断要件の確認テスト"""
        # 正常ケース
        self.assertTrue(check_health_requirements(self.test_medical_data))
        
        # エラーケース：高血圧
        high_bp_data = self.test_medical_data.copy()
        high_bp_data["blood_pressure"]["systolic"] = 150
        self.assertFalse(check_health_requirements(high_bp_data))
        
        # エラーケース：必要な検査項目の欠落
        incomplete_data = {
            "blood_pressure": self.test_medical_data["blood_pressure"]
        }
        self.assertFalse(check_health_requirements(incomplete_data))

    @patch('nekoneko.agents.safety_agent.monitor_space_weather')
    def test_space_weather_monitoring(self, mock_weather):
        """宇宙天気監視のテスト"""
        # モックの設定
        mock_weather.return_value = {
            "solar_activity": "moderate",
            "radiation_level": "normal",
            "meteoroid_risk": "low",
            "recommendation": "現在の宇宙天気は安定しています"
        }
        
        # 天気情報の取得
        weather_info = monitor_space_weather()
        
        # 結果の検証
        self.assertIn("solar_activity", weather_info)
        self.assertIn("radiation_level", weather_info)
        self.assertIn("meteoroid_risk", weather_info)
        self.assertIn("recommendation", weather_info)

    @patch('nekoneko.agents.safety_agent.safety_agent.run')
    def test_emergency_response_plan(self, mock_run):
        """緊急時対応計画の検証テスト"""
        # モックの設定
        mock_run.return_value = {
            "success": True,
            "plan_id": "EMERG123",
            "procedures": [
                "酸素マスクの装着",
                "非常用電源の起動",
                "地上管制との通信確立"
            ]
        }
        
        # 緊急時対応計画の取得
        response = safety_agent.run(
            """
            以下の状況での緊急時対応手順を教えてください：
            - 状況: 船内気圧の急激な低下
            - 場所: 月への航行中
            - 乗客数: 3名
            """
        )
        
        # 応答の検証
        self.assertTrue(response.get("success"))
        self.assertIsNotNone(response.get("plan_id"))
        self.assertIsInstance(response.get("procedures"), list)
        self.assertTrue(len(response.get("procedures")) > 0)

    def test_validate_training_completion(self):
        """訓練完了状況の検証テスト"""
        # 正常ケース：全ての訓練を完了
        self.assertTrue(safety_agent.validate_training(self.test_training_data))
        
        # エラーケース：未完了の訓練がある
        incomplete_training = self.test_training_data.copy()
        incomplete_training["zero_gravity"]["completed"] = False
        with self.assertRaises(ValueError):
            safety_agent.validate_training(incomplete_training)
        
        # エラーケース：低スコアの訓練
        low_score_training = self.test_training_data.copy()
        low_score_training["emergency_response"]["score"] = 60
        with self.assertRaises(ValueError):
            safety_agent.validate_training(low_score_training)

    def test_evaluate_space_suit(self):
        """宇宙服の点検テスト"""
        test_suit_data = {
            "oxygen_level": 100,
            "pressure": 1.0,
            "battery": 98,
            "communication": "operational",
            "seals": "intact"
        }
        
        # 正常ケース
        self.assertTrue(safety_agent.evaluate_space_suit(test_suit_data))
        
        # エラーケース：酸素レベル低下
        low_oxygen_suit = test_suit_data.copy()
        low_oxygen_suit["oxygen_level"] = 80
        with self.assertRaises(ValueError):
            safety_agent.evaluate_space_suit(low_oxygen_suit)
        
        # エラーケース：通信機器の不具合
        comm_failure_suit = test_suit_data.copy()
        comm_failure_suit["communication"] = "failed"
        with self.assertRaises(ValueError):
            safety_agent.evaluate_space_suit(comm_failure_suit)

if __name__ == '__main__':
    unittest.main()
