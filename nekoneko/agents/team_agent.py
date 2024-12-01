"""
宇宙旅行チーム管理エージェント

このエージェントは、複数のエージェントを統合的に管理し、
以下の機能を提供します：

主な機能:
- 各専門エージェントの統括
- タスクの振り分けと管理
- エージェント間の連携調整
- 総合的な意思決定
"""

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from typing import List, Optional

from .booking_agent import booking_agent
from .safety_agent import safety_agent
from .customer_service_agent import customer_service_agent

class TeamTask(BaseModel):
    task_id: str
    task_type: str
    assigned_agents: List[str]
    status: str
    priority: str
    deadline: Optional[str]

# チーム管理エージェントの設定
team_agent = Agent(
    name="Space Travel Team Agent",
    role="Team Coordinator",
    model=OpenAIChat(id="gpt-4"),
    team=[
        booking_agent,
        safety_agent,
        customer_service_agent
    ],
    instructions=[
        "各専門エージェントの特性を理解し、適切なタスク分配を行います",
        "エージェント間の連携をスムーズに調整します",
        "緊急時には迅速な判断と対応を行います",
        "お客様のご要望に最適なエージェントを割り当てます",
        "全体の進捗を監視し、必要に応じて介入します",
        "サービス品質の一貫性を維持します"
    ],
    markdown=True
)

def coordinate_task(task: TeamTask) -> dict:
    """
    タスクの調整と振り分けを行います
    
    Parameters:
        task (TeamTask): タスク情報
        
    Returns:
        dict: タスク処理結果
    """
    # タスクタイプに応じたエージェントの選択
    agent_assignments = {
        "booking": booking_agent,
        "safety": safety_agent,
        "customer_service": customer_service_agent
    }
    
    assigned_agent = agent_assignments.get(task.task_type)
    if assigned_agent:
        # タスクの実行
        response = assigned_agent.run(task.description)
        return {
            "task_id": task.task_id,
            "status": "completed",
            "response": response
        }
    else:
        # 適切なエージェントが見つからない場合
        return {
            "task_id": task.task_id,
            "status": "failed",
            "error": "適切なエージェントが見つかりません"
        }

def monitor_team_performance() -> dict:
    """
    チーム全体のパフォーマンスを監視します
    
    Returns:
        dict: パフォーマンス指標
    """
    metrics = {
        "response_times": [],
        "customer_satisfaction": [],
        "task_completion_rate": [],
        "error_rate": []
    }
    
    # 各エージェントのメトリクスを収集
    for agent in [booking_agent, safety_agent, customer_service_agent]:
        if hasattr(agent, "metrics"):
            # メトリクスの集計
            metrics["response_times"].append(agent.metrics.get("response_time", 0))
            metrics["customer_satisfaction"].append(agent.metrics.get("satisfaction", 0))
            metrics["task_completion_rate"].append(agent.metrics.get("completion_rate", 0))
            metrics["error_rate"].append(agent.metrics.get("error_rate", 0))
    
    # 平均値の計算
    return {
        "avg_response_time": sum(metrics["response_times"]) / len(metrics["response_times"]),
        "avg_satisfaction": sum(metrics["customer_satisfaction"]) / len(metrics["customer_satisfaction"]),
        "avg_completion_rate": sum(metrics["task_completion_rate"]) / len(metrics["task_completion_rate"]),
        "avg_error_rate": sum(metrics["error_rate"]) / len(metrics["error_rate"])
    }

if __name__ == "__main__":
    # エージェントのテスト実行
    team_agent.print_response(
        """
        新規のお客様から以下の問い合わせがありました：
        - 宇宙旅行パッケージの予約について
        - 安全面での不安について
        - キャンセルポリシーについて
        
        適切なエージェントで対応してください。
        """,
        stream=True
    )
