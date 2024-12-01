"""
予約エージェントのテストモジュール

このモジュールは、予約エージェントの機能を
テストするためのテストケースを提供します。

テスト対象:
- 予約プロセス
- 料金計算
- 予約の変更とキャンセル
"""

import unittest
from unittest.mock import Mock, patch
from nekoneko.agents.booking_agent import booking_agent, calculate_price
from datetime import datetime, timedelta

class TestBookingAgent(unittest.TestCase):
    def setUp(self):
        """テストの前準備"""
        self.test_user = {
            "name": "宇宙猫太郎",
            "email": "test@nekoneko-space.travel",
            "age": 30
        }
        
        self.test_booking = {
            "destination": "moon",
            "package_type": "economy",
            "departure_date": datetime.now() + timedelta(days=30),
            "return_date": datetime.now() + timedelta(days=33),
            "passengers": 2
        }

    def test_calculate_price(self):
        """料金計算のテスト"""
        # 月旅行の料金計算
        moon_price = calculate_price(
            destination="moon",
            days=3,
            package_type="economy",
            passengers=2
        )
        self.assertIsInstance(moon_price, float)
        self.assertTrue(moon_price > 0)
        
        # 火星旅行の料金計算
        mars_price = calculate_price(
            destination="mars",
            days=30,
            package_type="business",
            passengers=1
        )
        self.assertIsInstance(mars_price, float)
        self.assertTrue(mars_price > moon_price)  # 火星は月より高い
        
        # エラーケース：不正な目的地
        with self.assertRaises(ValueError):
            calculate_price(
                destination="invalid",
                days=1,
                package_type="economy",
                passengers=1
            )

    @patch('nekoneko.agents.booking_agent.booking_agent.run')
    def test_create_booking(self, mock_run):
        """予約作成のテスト"""
        # モックの設定
        mock_run.return_value = {
            "success": True,
            "booking_id": "TEST123",
            "total_price": 1000000
        }
        
        # 予約の作成
        response = booking_agent.run(
            f"""
            以下の予約を作成してください：
            - 目的地: {self.test_booking['destination']}
            - パッケージ: {self.test_booking['package_type']}
            - 出発日: {self.test_booking['departure_date']}
            - 帰還日: {self.test_booking['return_date']}
            - 乗客数: {self.test_booking['passengers']}
            """
        )
        
        # レスポンスの検証
        self.assertTrue(response.get("success"))
        self.assertIsNotNone(response.get("booking_id"))
        self.assertIsInstance(response.get("total_price"), (int, float))

    @patch('nekoneko.agents.booking_agent.booking_agent.run')
    def test_modify_booking(self, mock_run):
        """予約変更のテスト"""
        # モックの設定
        mock_run.return_value = {
            "success": True,
            "booking_id": "TEST123",
            "modified": True,
            "price_difference": 50000
        }
        
        # 予約の変更
        response = booking_agent.run(
            """
            予約番号TEST123の以下の変更をお願いします：
            - パッケージをビジネスクラスに変更
            - 乗客を1名追加
            """
        )
        
        # レスポンスの検証
        self.assertTrue(response.get("success"))
        self.assertTrue(response.get("modified"))
        self.assertIsInstance(response.get("price_difference"), (int, float))

    @patch('nekoneko.agents.booking_agent.booking_agent.run')
    def test_cancel_booking(self, mock_run):
        """予約キャンセルのテスト"""
        # モックの設定
        mock_run.return_value = {
            "success": True,
            "booking_id": "TEST123",
            "cancelled": True,
            "refund_amount": 800000
        }
        
        # 予約のキャンセル
        response = booking_agent.run(
            """
            予約番号TEST123のキャンセルをお願いします。
            キャンセル理由：都合により参加できなくなりました。
            """
        )
        
        # レスポンスの検証
        self.assertTrue(response.get("success"))
        self.assertTrue(response.get("cancelled"))
        self.assertIsInstance(response.get("refund_amount"), (int, float))

    def test_validate_booking_dates(self):
        """予約日程の検証テスト"""
        # 正常ケース：30日後の予約
        future_date = datetime.now() + timedelta(days=30)
        self.assertTrue(booking_agent.validate_dates(future_date))
        
        # エラーケース：過去の日付
        past_date = datetime.now() - timedelta(days=1)
        with self.assertRaises(ValueError):
            booking_agent.validate_dates(past_date)
        
        # エラーケース：近すぎる日付
        near_date = datetime.now() + timedelta(days=7)
        with self.assertRaises(ValueError):
            booking_agent.validate_dates(near_date)

    def test_validate_passengers(self):
        """乗客情報の検証テスト"""
        # 正常ケース：標準的な乗客情報
        valid_passengers = [
            {"name": "宇宙猫太郎", "age": 30},
            {"name": "宇宙猫花子", "age": 28}
        ]
        self.assertTrue(booking_agent.validate_passengers(valid_passengers))
        
        # エラーケース：乗客数超過
        invalid_passengers = [{"name": f"乗客{i}", "age": 30} for i in range(5)]
        with self.assertRaises(ValueError):
            booking_agent.validate_passengers(invalid_passengers)
        
        # エラーケース：未成年の乗客
        minor_passengers = [
            {"name": "宇宙猫太郎", "age": 30},
            {"name": "宇宙猫次郎", "age": 15}
        ]
        with self.assertRaises(ValueError):
            booking_agent.validate_passengers(minor_passengers)

if __name__ == '__main__':
    unittest.main()
