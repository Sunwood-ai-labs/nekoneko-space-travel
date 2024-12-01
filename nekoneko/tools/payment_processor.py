"""
宇宙旅行決済処理ツール

このモジュールは宇宙旅行の予約に関する
決済処理を行うツールを提供します。

主な機能:
- 料金計算
- 決済処理
- 領収書発行
- 返金処理
"""

from typing import Dict, Optional
import stripe
from datetime import datetime
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

class PaymentProcessor:
    def __init__(self):
        self.currency = "jpy"
        self.tax_rate = 0.10  # 消費税率10%
        
        # 支払いプラン
        self.payment_plans = {
            "full": {"description": "一括払い", "discount": 0.05},  # 5%割引
            "split": {"description": "分割払い", "discount": 0},
            "deposit": {"description": "頭金プラン", "discount": 0}
        }

    def calculate_total(self, 
                       base_price: float, 
                       passengers: int,
                       payment_plan: str = "full") -> Dict[str, float]:
        """
        最終的な支払い金額を計算します
        
        Parameters:
            base_price (float): 基本料金
            passengers (int): 乗客数
            payment_plan (str): 支払いプラン
            
        Returns:
            Dict[str, float]: 料金の内訳
        """
        # 基本料金の計算
        subtotal = base_price * passengers
        
        # 割引の適用
        discount = subtotal * self.payment_plans[payment_plan]["discount"]
        
        # 税金の計算
        tax = (subtotal - discount) * self.tax_rate
        
        # 合計金額
        total = subtotal - discount + tax
        
        return {
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": total
        }

    def process_payment(self,
                       amount: int,
                       token: str,
                       customer_email: str,
                       booking_ref: str) -> Dict[str, any]:
        """
        決済を処理します
        
        Parameters:
            amount (int): 支払い金額（円）
            token (str): 決済トークン
            customer_email (str): 顧客のメールアドレス
            booking_ref (str): 予約参照番号
            
        Returns:
            Dict: 決済結果
        """
        try:
            # Stripeで決済を実行
            charge = stripe.Charge.create(
                amount=amount,
                currency=self.currency,
                source=token,
                description=f"ねこねこスペーストラベル - 予約番号: {booking_ref}",
                receipt_email=customer_email
            )
            
            return {
                "success": True,
                "transaction_id": charge.id,
                "amount": charge.amount,
                "receipt_url": charge.receipt_url,
                "status": charge.status,
                "created": datetime.fromtimestamp(charge.created)
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code,
                "booking_ref": booking_ref
            }

    def process_refund(self,
                      transaction_id: str,
                      amount: Optional[int] = None) -> Dict[str, any]:
        """
        返金を処理します
        
        Parameters:
            transaction_id (str): 元の取引ID
            amount (Optional[int]): 返金額（指定しない場合は全額返金）
            
        Returns:
            Dict: 返金結果
        """
        try:
            refund = stripe.Refund.create(
                charge=transaction_id,
                amount=amount
            )
            
            return {
                "success": True,
                "refund_id": refund.id,
                "amount": refund.amount,
                "status": refund.status,
                "created": datetime.fromtimestamp(refund.created)
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code,
                "transaction_id": transaction_id
            }

    def generate_receipt(self,
                        transaction_data: Dict[str, any],
                        customer_info: Dict[str, str]) -> str:
        """
        領収書を生成します
        
        Parameters:
            transaction_data (Dict): 取引データ
            customer_info (Dict): 顧客情報
            
        Returns:
            str: 領収書のHTML形式のデータ
        """
        receipt_template = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h1 style="text-align: center;">領収書</h1>
            <div style="text-align: right;">
                <p>発行日: {datetime.now().strftime('%Y年%m月%d日')}</p>
                <p>領収書番号: {transaction_data['transaction_id']}</p>
            </div>
            <div style="margin: 40px 0;">
                <h2>{customer_info['name']} 様</h2>
                <p>下記の金額を領収いたしました。</p>
                <h3 style="text-align: center;">￥{transaction_data['amount']:,}</h3>
                <p>但し、宇宙旅行代金として</p>
            </div>
            <div style="margin: 40px 0;">
                <div style="text-align: center;">
                    <img src="logo.png" alt="ねこねこスペーストラベル" style="max-width: 200px;">
                    <p>ねこねこスペーストラベル株式会社</p>
                    <p>〒123-4567 東京都月面区星空町1-2-3</p>
                    <p>TEL: 03-1234-5678</p>
                </div>
            </div>
        </div>
        """
        
        return receipt_template

if __name__ == "__main__":
    # 処理例
    processor = PaymentProcessor()
    
    # 料金計算
    price_details = processor.calculate_total(1000000, 2, "full")
    print("料金内訳:", price_details)
