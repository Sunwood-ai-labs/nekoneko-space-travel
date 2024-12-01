"""
宇宙旅行予約管理エージェント

このエージェントは宇宙旅行の予約管理を担当し、
以下の機能を提供します：

主な機能:
- 宇宙旅行パッケージの検索と提案
- 予約の受付と管理
- 料金の計算と決済処理
- 旅程の最適化
"""

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from pydantic import BaseModel
from typing import List, Optional

# 予約情報のデータモデル
class SpaceBooking(BaseModel):
    destination: str
    departure_date: str
    return_date: str
    passengers: int
    package_type: str
    special_requests: Optional[List[str]]
    total_price: float

# 予約管理エージェントの設定
booking_agent = Agent(
    name="Space Travel Booking Agent",
    role="Booking Specialist",
    model=OpenAIChat(id="gpt-4"),
    tools=[DuckDuckGo()],
    instructions=[
        "宇宙旅行の予約専門エージェントとして応対します",
        "お客様のご要望を丁寧にヒアリングします",
        "最適な宇宙旅行パッケージを提案します",
        "安全面の説明を必ず含めます",
        "予算に応じた選択肢を提供します",
        "特別な要望にも柔軟に対応します"
    ],
    markdown=True
)

# 料金計算機能
def calculate_price(destination: str, days: int, package_type: str, passengers: int) -> float:
    """
    宇宙旅行の料金を計算します
    
    Parameters:
        destination (str): 目的地（月、火星、宇宙ステーションなど）
        days (int): 旅行日数
        package_type (str): パッケージタイプ（エコノミー、ビジネス、ファーストクラス）
        passengers (int): 乗客数
        
    Returns:
        float: 合計金額
    """
    # 基本料金テーブル
    base_prices = {
        "moon": 1000000,  # 月旅行の基本料金
        "mars": 5000000,  # 火星旅行の基本料金
        "space_station": 800000  # 宇宙ステーション旅行の基本料金
    }
    
    # パッケージタイプによる係数
    package_multipliers = {
        "economy": 1.0,
        "business": 1.5,
        "first": 2.0
    }
    
    # 基本料金の計算
    base_price = base_prices.get(destination.lower(), 1000000)
    package_multiplier = package_multipliers.get(package_type.lower(), 1.0)
    
    # 最終料金の計算（日数と乗客数を考慮）
    total = base_price * package_multiplier * days * passengers
    
    return total

if __name__ == "__main__":
    # エージェントのテスト実行
    booking_agent.print_response(
        """
        月への3日間の旅行を検討しています。
        大人2名で、エコノミーパッケージを希望します。
        費用と旅程を教えてください。
        """,
        stream=True
    )
