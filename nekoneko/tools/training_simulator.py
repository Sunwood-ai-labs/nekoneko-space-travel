"""
宇宙飛行訓練シミュレータツール

このモジュールは宇宙飛行に必要な
訓練プログラムのシミュレーションを提供します。

主な機能:
- 無重力環境訓練
- 緊急時対応訓練
- 宇宙船操縦訓練
- 健康管理訓練
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import random

class TrainingType(Enum):
    ZERO_GRAVITY = "zero_gravity"
    EMERGENCY = "emergency"
    SPACECRAFT = "spacecraft"
    HEALTH = "health"
    COMMUNICATION = "communication"

class TrainingLevel(Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class TrainingSimulator:
    def __init__(self):
        self.training_programs = {
            TrainingType.ZERO_GRAVITY: {
                "duration_days": 5,
                "requirements": ["基本的な体力", "めまい耐性"],
                "equipment": ["無重力シミュレータ", "特殊スーツ"],
                "description": "無重力環境での生活と活動に慣れるための訓練プログラムです。"
            },
            TrainingType.EMERGENCY: {
                "duration_days": 3,
                "requirements": ["基本訓練修了"],
                "equipment": ["救命装置", "消火装置"],
                "description": "宇宙船内外での緊急事態に対応するための訓練プログラムです。"
            },
            TrainingType.SPACECRAFT: {
                "duration_days": 7,
                "requirements": ["基本訓練修了", "シミュレータ経験"],
                "equipment": ["操縦シミュレータ", "通信機器"],
                "description": "宇宙船の基本操作と運航手順を学ぶ訓練プログラムです。"
            },
            TrainingType.HEALTH: {
                "duration_days": 2,
                "requirements": ["基本的な体力"],
                "equipment": ["医療機器", "運動設備"],
                "description": "宇宙での健康管理と応急処置を学ぶ訓練プログラムです。"
            },
            TrainingType.COMMUNICATION: {
                "duration_days": 1,
                "requirements": ["基本訓練修了"],
                "equipment": ["通信機器", "緊急通信装置"],
                "description": "地上管制との通信手順と緊急通信を学ぶ訓練プログラムです。"
            }
        }

        self.passing_score = 80  # 合格基準点

    def create_training_schedule(self, 
                               trainee_name: str,
                               departure_date: datetime,
                               training_types: List[TrainingType]) -> Dict[str, any]:
        """
        訓練スケジュールを作成します
        
        Parameters:
            trainee_name (str): 訓練生の名前
            departure_date (datetime): 出発予定日
            training_types (List[TrainingType]): 必要な訓練タイプのリスト
            
        Returns:
            Dict: 訓練スケジュール
        """
        total_days = sum(self.training_programs[t]["duration_days"] for t in training_types)
        start_date = departure_date - timedelta(days=total_days + 14)  # 2週間の余裕を持たせる
        
        schedule = {
            "trainee_name": trainee_name,
            "start_date": start_date,
            "end_date": departure_date - timedelta(days=7),
            "departure_date": departure_date,
            "training_modules": []
        }
        
        current_date = start_date
        for training_type in training_types:
            program = self.training_programs[training_type]
            schedule["training_modules"].append({
                "type": training_type.value,
                "start_date": current_date,
                "end_date": current_date + timedelta(days=program["duration_days"]),
                "duration_days": program["duration_days"],
                "requirements": program["requirements"],
                "equipment": program["equipment"],
                "description": program["description"]
            })
            current_date += timedelta(days=program["duration_days"] + 1)
        
        return schedule

    def run_training_session(self, 
                           training_type: TrainingType,
                           trainee_name: str,
                           level: TrainingLevel = TrainingLevel.BASIC) -> Dict[str, any]:
        """
        訓練セッションを実行します
        
        Parameters:
            training_type (TrainingType): 訓練タイプ
            trainee_name (str): 訓練生の名前
            level (TrainingLevel): 訓練レベル
            
        Returns:
            Dict: 訓練結果
        """
        # 訓練結果のシミュレーション
        base_score = random.randint(60, 100)
        
        # レベルによる難易度調整
        difficulty_multiplier = {
            TrainingLevel.BASIC: 1.0,
            TrainingLevel.INTERMEDIATE: 0.9,
            TrainingLevel.ADVANCED: 0.8
        }[level]
        
        final_score = base_score * difficulty_multiplier
        
        return {
            "trainee_name": trainee_name,
            "training_type": training_type.value,
            "level": level.value,
            "date": datetime.now(),
            "score": final_score,
            "passed": final_score >= self.passing_score,
            "feedback": self._generate_feedback(training_type, final_score),
            "next_steps": self._recommend_next_steps(training_type, final_score)
        }

    def _generate_feedback(self, training_type: TrainingType, score: float) -> str:
        """
        訓練結果に基づいてフィードバックを生成します
        """
        if score >= 90:
            return "にゃー！素晴らしい成績です。実践的な技能が十分に身についています。"
        elif score >= 80:
            return "にゃ。合格基準を満たしています。さらなる練習で完璧を目指しましょう。"
        else:
            return "にゃん...もう少し練習が必要です。基本に立ち返って復習しましょう。"

    def _recommend_next_steps(self, training_type: TrainingType, score: float) -> List[str]:
        """
        訓練結果に基づいて次のステップを推奨します
        """
        if score >= 90:
            return ["上級訓練プログラムへの参加", "他の訓練生のメンター担当"]
        elif score >= 80:
            return ["追加の実践訓練", "弱点分野の強化"]
        else:
            return ["基本訓練の復習", "個別指導の予約", "補足訓練の実施"]

if __name__ == "__main__":
    # 使用例
    simulator = TrainingSimulator()
    
    # 訓練スケジュールの作成
    schedule = simulator.create_training_schedule(
        "宇宙猫太郎",
        datetime.now() + timedelta(days=60),
        [TrainingType.ZERO_GRAVITY, TrainingType.EMERGENCY, TrainingType.SPACECRAFT]
    )
    print("訓練スケジュール:", schedule)
    
    # 訓練セッションの実行
    result = simulator.run_training_session(
        TrainingType.ZERO_GRAVITY,
        "宇宙猫太郎",
        TrainingLevel.BASIC
    )
    print("訓練結果:", result)
