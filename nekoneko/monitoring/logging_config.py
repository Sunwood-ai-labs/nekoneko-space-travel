"""
アプリケーションロギング設定モジュール

このモジュールは、アプリケーションの各種ログを
設定・管理するための機能を提供します。

主な機能:
- ログレベルの設定
- ログ出力先の設定
- ログフォーマットの設定
- ログローテーションの設定
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from datetime import datetime
from pathlib import Path

class CustomJSONFormatter(logging.Formatter):
    """カスタムJSONフォーマッタ"""
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
            
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra_data"):
            log_obj["extra"] = record.extra_data
            
        return json.dumps(log_obj)

def setup_logging(
    app_name: str = "nekoneko",
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    アプリケーションのロギング設定をセットアップ
    
    Args:
        app_name (str): アプリケーション名
        log_level (str): ログレベル
        log_dir (str): ログファイル保存ディレクトリ
        max_bytes (int): ログファイルの最大サイズ
        backup_count (int): 保持する過去ログファイル数
        
    Returns:
        logging.Logger: 設定済みのロガーインスタンス
    """
    # ログディレクトリの作成
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # ロガーの作成
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # JSONフォーマッタの作成
    json_formatter = CustomJSONFormatter()

    # ファイルハンドラの設定（サイズベースのローテーション）
    file_handler = RotatingFileHandler(
        filename=log_path / f"{app_name}.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    # エラーログ用のファイルハンドラ（日付ベースのローテーション）
    error_handler = TimedRotatingFileHandler(
        filename=log_path / f"{app_name}_error.log",
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    logger.addHandler(error_handler)

    # コンソール出力用のハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler)

    return logger

# ログコンテキストマネージャー
class LogContext:
    """ログにコンテキスト情報を追加するためのコンテキストマネージャー"""
    def __init__(self, logger: logging.Logger, **kwargs):
        self.logger = logger
        self.extra = kwargs
        self._old_extra = {}

    def __enter__(self):
        # 現在の extra 属性を保存
        if hasattr(self.logger, 'extra_data'):
            self._old_extra = self.logger.extra_data.copy()
        
        # 新しい extra 属性を設定
        if not hasattr(self.logger, 'extra_data'):
            self.logger.extra_data = {}
        self.logger.extra_data.update(self.extra)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 元の extra 属性を復元
        if self._old_extra:
            self.logger.extra_data = self._old_extra
        else:
            delattr(self.logger, 'extra_data')

# 使用例
if __name__ == "__main__":
    logger = setup_logging()

    # 基本的なログ出力
    logger.info("アプリケーションを起動しました")
    logger.warning("警告メッセージ")
    logger.error("エラーが発生しました", exc_info=True)

    # コンテキスト付きのログ出力
    with LogContext(logger, request_id="12345", user="test_user"):
        logger.info("ユーザーがログインしました")
        try:
            raise ValueError("テストエラー")
        except Exception as e:
            logger.error("エラーが発生しました", exc_info=True)
