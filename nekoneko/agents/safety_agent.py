"""
宇宙旅行安全管理エージェント

このエージェントは宇宙旅行の安全管理を担当し、
以下の機能を提供します：

主な機能:
- 健康診断要件の確認
- 安全訓練プログラムの管理
- 緊急時対応プランの策定
- 宇宙天気予報の監視
"""

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from pydantic import BaseModel
from typing import List, Optional

class SafetyCheck(BaseModel):
    passenger_name: str
    health_check_status: bool
    training_completed: bool
    emergency_contact: str
    medical_conditions: Optional[List[str]]
    training_scores: Optional[dict]

class SpaceWeather(BaseModel):
    solar_activity: str
    radiation_level: str
    meteoroid_risk: str
    recommendation: str

# 安全管理エージェントの設定
safety_agent = Agent(
    name="Space Travel Safety Agent",
    role="Safety Specialist",
    model=OpenAIChat(id="gpt-4"),
    tools=[DuckDuckGo()],
    instructions=[
        "宇宙旅行の安全管理専門家として対応します",
        "必要な健康診断と訓練の要件を説明します",
        "安全上のリスクと対策を詳しく解説します",
        "緊急時の対応手順を明確に伝えます",
        "宇宙空間での注意事項を説明します",
        "お客様の健康状態に応じた個別アドバイスを提供します"
    ],
    markdown=True
)

def check_health_requirements(medical_history: dict) -> bool:
    """
    健康診断要件を確認します
    
    Parameters:
        medical_history (dict): 健康診断データ
        
    Returns:
        bool: 健康診断基準を満たしているかどうか
    """
    required_checks = [
        "blood_pressure",
        "heart_condition",
        "bone_density",
        "inner_ear",
        "vision"
    ]
    
    # 必要な健康診断項目の確認
    for check in required_checks:
        if check not in medical_history:
            return False
    
    # 基準値の確認
    if medical_history["blood_pressure"]["systolic"] > 140:
        return False
    if medical_history["blood_pressure"]["diastolic"] > 90:
        return False
    
    return True

def monitor_space_weather() -> SpaceWeather:
    """
    宇宙天気情報を取得・分析します
    
    Returns:
        SpaceWeather: 宇宙天気情報と推奨事項
    """
    # 実際のAPIからデータを取得する想定
    return SpaceWeather(
        solar_activity="moderate",
        radiation_level="normal",
        meteoroid_risk="low",
        recommendation="現在の宇宙天気は安定しており、宇宙旅行に適しています。"
    )

if __name__ == "__main__":
    # エージェントのテスト実行
    safety_agent.print_response(
        """
        宇宙旅行の安全対策について教えてください。
        特に、以下の点について詳しく知りたいです：
        1. 必要な健康診断
        2. 事前トレーニング
        3. 緊急時の対応
        """,
        stream=True
    )
