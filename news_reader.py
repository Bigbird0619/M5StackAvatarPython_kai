"""
Googleニュースを取得して読み上げる機能を提供するモジュール
"""
import feedparser
from PySide6.QtCore import QTimer


class NewsReader:
    """Googleニュースを取得・管理するクラス"""
    
    def __init__(self, avatar):
        """
        Args:
            avatar: M5StackAvatarインスタンス
        """
        self.avatar = avatar
        self.news_index = 0
        self.news_items = []
        
    def fetch_google_news(self, topic='japan', lang='ja', max_items=10):
        """
        GoogleニュースのRSSフィードを取得
        
        Args:
            topic: ニュースのトピック（'japan'または検索キーワード）
            lang: 言語コード（デフォルト: 'ja'）
            max_items: 取得する最大ニュース数（デフォルト: 10）
            
        Returns:
            bool: 取得成功時True、失敗時False
        """
        try:
            # GoogleニュースのRSS URL
            if topic == 'japan':
                url = f'https://news.google.com/rss?hl={lang}&gl=JP&ceid=JP:{lang}'
            else:
                url = f'https://news.google.com/rss/search?q={topic}&hl={lang}&gl=JP&ceid=JP:{lang}'
            
            feed = feedparser.parse(url)
            self.news_items = []
            
            # ニュース項目を解析
            for entry in feed.entries[:max_items]:
                title = entry.title
                # 提供元を除去（' - 'で区切られている場合）
                if ' - ' in title:
                    title = title.split(' - ')[0]
                
                self.news_items.append({
                    'title': title,
                    'link': entry.link,
                    'published': entry.get('published', '')
                })
            
            return len(self.news_items) > 0
            
        except Exception as e:
            print(f"ニュース取得エラー: {e}")
            return False
    
    def read_next_news(self):
        """
        次のニュースを読み上げる
        
        Returns:
            bool: 読み上げ成功時True、全て読み終えた場合False
        """
        if self.news_index < len(self.news_items):
            news = self.news_items[self.news_index]
            self.avatar.speak(f"ニュース{self.news_index + 1}: {news['title']}")
            self.news_index += 1
            return True
        else:
            self.avatar.speak("以上でニュースは終わりです")
            self.news_index = 0
            return False
    
    def read_all_news(self, interval=8000):
        """
        全てのニュースを順番に読み上げる
        
        Args:
            interval: 各ニュースの読み上げ間隔（ミリ秒）
        """
        if self.news_index < len(self.news_items):
            self.read_next_news()
            QTimer.singleShot(interval, lambda: self.read_all_news(interval))
        else:
            self.news_index = 0
    
    def reset(self):
        """ニュースインデックスをリセット"""
        self.news_index = 0
    
    def get_news_count(self):
        """
        取得したニュース数を返す
        
        Returns:
            int: ニュース数
        """
        return len(self.news_items)
