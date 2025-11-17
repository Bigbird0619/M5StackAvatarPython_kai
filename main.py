"""
M5Stack Avatar - Googleニュースリーダー
PySide6で動作するアバターアプリケーション
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from m5stack_avatar import M5StackAvatar
from news_reader import NewsReader


def main():
    """メイン処理"""
    # アプリケーション初期化
    app = QApplication(sys.argv)
    
    # アバター作成
    avatar = M5StackAvatar()
    avatar.app = app
    avatar.start()
    
    # ニュースリーダー作成
    news_reader = NewsReader(avatar)
    
    def start_news_reading():
        """ニュース読み上げを開始"""
        avatar.speak('Googleニュースを取得中...')
        
        if news_reader.fetch_google_news():
            count = news_reader.get_news_count()
            avatar.speak(f'{count}件のニュースを取得しました')
            QTimer.singleShot(3000, lambda: news_reader.read_all_news(interval=10000))
        else:
            avatar.speak('ニュースの取得に失敗しました')
            QTimer.singleShot(5000, start_news_reading)
    
    # 起動時にニュース読み上げ開始
    QTimer.singleShot(1000, start_news_reading)
    
    # アプリケーション実行
    sys.exit(app.exec())


if __name__ == '__main__':
    main()