"""
アラート通知モジュール

このモジュールは、システムアラートを適切な
チャンネルに通知するための機能を提供します。

主な機能:
- メール通知
- Slack通知
- LINE通知
- Discord通知
- Webhook通知
"""

import smtplib
import requests
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from .logging_config import setup_logging

# 環境変数の読み込み
load_dotenv()

class AlertNotifier:
    def __init__(self):
        """アラート通知システムの初期化"""
        self.logger = setup_logging(app_name="alert_notifier")
        
        # メール設定
        self.smtp_settings = {
            "server": os.getenv("SMTP_SERVER"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "from_address": os.getenv("ALERT_FROM_EMAIL")
        }
        
        # Slack設定
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        
        # LINE設定
        self.line_token = os.getenv("LINE_NOTIFY_TOKEN")
        
        # Discord設定
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")

    def send_email_alert(self,
                        subject: str,
                        message: str,
                        recipients: List[str]) -> bool:
        """
        メールでアラートを送信
        
        Args:
            subject (str): メールの件名
            message (str): メールの本文
            recipients (List[str]): 受信者のメールアドレスリスト
            
        Returns:
            bool: 送信成功したかどうか
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_settings["from_address"]
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = f"[ねこねこスペーストラベル アラート] {subject}"
            
            # HTML形式のメール本文
            html_content = f"""
            <html>
                <body>
                    <h2>🚨 アラート通知</h2>
                    <p><strong>時刻:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>種類:</strong> {subject}</p>
                    <hr>
                    <div>{message}</div>
                    <hr>
                    <p>
                        <small>
                            このメールはねこねこスペーストラベルの監視システムから自動送信されています。<br>
                            問題が解決しない場合は技術チームまでご連絡ください。
                        </small>
                    </p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP(self.smtp_settings["server"], self.smtp_settings["port"]) as server:
                server.starttls()
                server.login(self.smtp_settings["username"], self.smtp_settings["password"])
                server.send_message(msg)
                
            self.logger.info(f"アラートメールを送信しました: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"メール送信に失敗: {str(e)}", exc_info=True)
            return False

    def send_slack_alert(self,
                        title: str,
                        message: str,
                        severity: str = "warning") -> bool:
        """
        Slackでアラートを送信
        
        Args:
            title (str): アラートのタイトル
            message (str): アラートの詳細メッセージ
            severity (str): 重要度（info, warning, error）
            
        Returns:
            bool: 送信成功したかどうか
        """
        try:
            # 重要度に応じた絵文字とカラーの設定
            severity_config = {
                "info": ("ℹ️", "#36a64f"),
                "warning": ("⚠️", "#ffd700"),
                "error": ("🚨", "#ff0000")
            }
            
            emoji, color = severity_config.get(severity.lower(), ("🔔", "#808080"))
            
            payload = {
                "attachments": [{
                    "color": color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"{emoji} {title}"
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": message
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"発生時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                }
                            ]
                        }
                    ]
                }]
            }
            
            response = requests.post(
                self.slack_webhook,
                json=payload
            )
            response.raise_for_status()
            
            self.logger.info(f"Slackアラートを送信しました: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Slack通知に失敗: {str(e)}", exc_info=True)
            return False

    def send_line_alert(self,
                       message: str) -> bool:
        """
        LINEでアラートを送信
        
        Args:
            message (str): 送信するメッセージ
            
        Returns:
            bool: 送信成功したかどうか
        """
        try:
            headers = {'Authorization': f'Bearer {self.line_token}'}
            payload = {'message': f"🚨 アラート通知\n\n{message}"}
            
            response = requests.post(
                'https://notify-api.line.me/api/notify',
                headers=headers,
                data=payload
            )
            response.raise_for_status()
            
            self.logger.info("LINEアラートを送信しました")
            return True
            
        except Exception as e:
            self.logger.error(f"LINE通知に失敗: {str(e)}", exc_info=True)
            return False

    def send_discord_alert(self,
                         title: str,
                         message: str,
                         color: int = 0xFF0000) -> bool:
        """
        Discordでアラートを送信
        
        Args:
            title (str): アラートのタイトル
            message (str): アラートの詳細メッセージ
            color (int): 埋め込みメッセージの色（16進数）
            
        Returns:
            bool: 送信成功したかどうか
        """
        try:
            payload = {
                "embeds": [{
                    "title": f"🚨 {title}",
                    "description": message,
                    "color": color,
                    "footer": {
                        "text": f"発生時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                }]
            }
            
            response = requests.post(
                self.discord_webhook,
                json=payload
            )
            response.raise_for_status()
            
            self.logger.info(f"Discordアラートを送信しました: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Discord通知に失敗: {str(e)}", exc_info=True)
            return False

    def broadcast_alert(self,
                       title: str,
                       message: str,
                       severity: str = "warning",
                       email_recipients: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        全チャンネルにアラートを送信
        
        Args:
            title (str): アラートのタイトル
            message (str): アラートの詳細メッセージ
            severity (str): 重要度
            email_recipients (Optional[List[str]]): メール受信者リスト
            
        Returns:
            Dict[str, bool]: 各チャンネルの送信結果
        """
        results = {}
        
        # メール通知
        if email_recipients:
            results["email"] = self.send_email_alert(title, message, email_recipients)
        
        # Slack通知
        if self.slack_webhook:
            results["slack"] = self.send_slack_alert(title, message, severity)
        
        # LINE通知
        if self.line_token:
            results["line"] = self.send_line_alert(f"{title}\n\n{message}")
        
        # Discord通知
        if self.discord_webhook:
            results["discord"] = self.send_discord_alert(title, message)
        
        return results

# 使用例
if __name__ == "__main__":
    notifier = AlertNotifier()
    
    # テスト通知の送信
    results = notifier.broadcast_alert(
        title="システム負荷警告",
        message="CPU使用率が90%を超えています。\n即時の対応が必要です。",
        severity="error",
        email_recipients=["admin@nekoneko-space.travel"]
    )
    
    print("通知結果:", results)
