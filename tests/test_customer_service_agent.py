"""
カスタマーサービスエージェントのテストモジュール

このモジュールは、カスタマーサービスエージェントの
機能をテストするためのテストケースを提供します。

テスト対象:
- 問い合わせ対応
- クレーム処理
- フィードバック分析
- 顧客満足度評価
"""

import unittest
from unittest.mock import Mock, patch
from nekoneko.agents.customer_service_agent import (
    customer_service_agent,
    handle_inquiry,
    process_feedback
)
from datetime import datetime

class TestCustomerServiceAgent(unittest.TestCase):
    def setUp(self):
        """テストの前準備"""
        self.test_inquiry = {
            "inquiry_id": "INQ123",
            "customer_name": "宇宙猫太郎",
            "inquiry_type": "general",
            "content": "月旅行パッケージについて詳しく知りたいです",
            "timestamp": datetime.now(),
            "priority": "medium",
            "status": "new"
        }
        
        self.test_feedback = {
            "feedback_id": "FB123",
            "booking_id": "BK789",
            "rating": 4,
            "comments": "とても楽しい宇宙旅行でした！スタッフの対応も親切でした。",
            "timestamp": datetime.now(),
            "response_required": False
        }

    def test_handle_inquiry(self):
        """問い合わせ対応のテスト"""
        # 一般的な問い合わせ
        response = handle_inquiry(self.test_inquiry)
        self.assertIsNotNone(response)
        self.assertIn("にゃー", response)  # 猫らしい応答の確認
        
        # 緊急の問い合わせ
        urgent_inquiry = self.test_inquiry.copy()
        urgent_inquiry["priority"] = "high"
        urgent_inquiry["inquiry_type"] = "emergency"
        response = handle_inquiry(urgent_inquiry)
        self.assertIn("直ちに", response)  # 緊急性の反映を確認
        
        # 予約関連の問い合わせ
        booking_inquiry = self.test_inquiry.copy()
        booking_inquiry["inquiry_type"] = "booking"
        response = handle_inquiry(booking_inquiry)
        self.assertIn("ご予約", response)

    @patch('nekoneko.agents.customer_service_agent.customer_service_agent.run')
    def test_handle_complaint(self, mock_run):
        """クレーム処理のテスト"""
        # モックの設定
        mock_run.return_value = {
            "success": True,
            "complaint_id": "COMP123",
            "resolution": "お詫びと代替サービスの提供",
            "compensation": {
                "type": "discount",
                "amount": 50000
            }
        }
        
        # クレームの処理
        response = customer_service_agent.run(
            """
            以下のクレームについて対応をお願いします：
            - 内容: 宇宙船内の無重力体験施設が利用できなかった
            - 予約番号: BK789
            - 深刻度: 中
            """
        )
        
        # 応答の検証
        self.assertTrue(response.get("success"))
        self.assertIsNotNone(response.get("complaint_id"))
        self.assertIsNotNone(response.get("resolution"))
        self.assertIsInstance(response.get("compensation"), dict)

    def test_process_feedback(self):
        """フィードバック処理のテスト"""
        # 通常のフィードバック
        result = process_feedback(self.test_feedback)
        self.assertTrue(result["processed"])
        self.assertFalse(result["follow_up_required"])
        
        # 低評価のフィードバック
        negative_feedback = self.test_feedback.copy()
        negative_feedback["rating"] = 2
        negative_feedback["comments"] = "サービスに不満があります"
        result = process_feedback(negative_feedback)
        self.assertTrue(result["processed"])
        self.assertTrue(result["follow_up_required"])
        
        # フォローアップ要求のあるフィードバック
        followup_feedback = self.test_feedback.copy()
        followup_feedback["response_required"] = True
        result = process_feedback(followup_feedback)
        self.assertTrue(result["follow_up_required"])

    def test_sentiment_analysis(self):
        """感情分析のテスト"""
        # ポジティブなコメント
        positive_sentiment = customer_service_agent.analyze_sentiment(
            "スタッフの対応が素晴らしく、思い出に残る宇宙旅行になりました！"
        )
        self.assertGreater(positive_sentiment["score"], 0.5)
        
        # ネガティブなコメント
        negative_sentiment = customer_service_agent.analyze_sentiment(
            "予約変更の対応が遅く、とても不満です。"
        )
        self.assertLess(negative_sentiment["score"], 0.5)
        
        # 中立的なコメント
        neutral_sentiment = customer_service_agent.analyze_sentiment(
            "普通の宇宙旅行でした。"
        )
        self.assertAlmostEqual(neutral_sentiment["score"], 0.5, delta=0.2)

    def test_response_generation(self):
        """応答生成のテスト"""
        # 基本的な応答
        response = customer_service_agent.generate_response(
            "月旅行の予約方法を教えてください"
        )
        self.assertIsInstance(response, str)
        self.assertIn("にゃー", response)  # 猫らしさの確認
        
        # 詳細な情報を含む応答
        detailed_response = customer_service_agent.generate_response(
            "宇宙船内での生活について詳しく知りたいです"
        )
        self.assertGreater(len(detailed_response), 100)  # 十分な情報量の確認
        
        # 緊急時の応答
        emergency_response = customer_service_agent.generate_response(
            "酸素供給に問題が発生しています",
            priority="high"
        )
        self.assertIn("緊急", emergency_response)
        self.assertIn("直ちに", emergency_response)

    def test_satisfaction_survey(self):
        """満足度調査のテスト"""
        # 調査データの作成
        survey_data = {
            "booking_id": "BK789",
            "questions": [
                {"id": 1, "score": 5, "comment": "とても良かった"},
                {"id": 2, "score": 4, "comment": "概ね満足"},
                {"id": 3, "score": 3, "comment": "普通"}
            ],
            "timestamp": datetime.now()
        }
        
        # 満足度の分析
        analysis = customer_service_agent.analyze_satisfaction(survey_data)
        
        # 結果の検証
        self.assertIsInstance(analysis["average_score"], float)
        self.assertIsInstance(analysis["recommendations"], list)
        self.assertGreaterEqual(len(analysis["recommendations"]), 1)

if __name__ == '__main__':
    unittest.main()
