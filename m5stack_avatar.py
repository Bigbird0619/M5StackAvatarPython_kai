"""
M5Stack Avatar - PySide6版
顔のアニメーション（まばたき、口の動き）とテキスト表示機能を提供
"""
import random
import queue
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont


class M5StackAvatar(QWidget):
    """M5Stack風アバターウィジェット"""
    
    def __init__(self):
        """アバターウィジェットの初期化"""
        super().__init__()
        self.setWindowTitle('M5Stack Avatar')
        self.setFixedSize(320, 240)
        
        # ウィンドウサイズとフォント設定
        self.ww = 320  # ウィンドウ幅
        self.wh = 240  # ウィンドウ高さ
        self.fw = 12   # フォント幅
        self.fh = 24   # フォント高さ
        
        # 目の設定
        self.eye_x = 90
        self.eye_y = 80
        self.eye_r = 10
        self.eye_close_x = 70
        self.eye_close_width = 40
        self.eye_close_height = 5
        self.blink_term_ms = 500
        
        # 口の設定
        self.mouth_x = 135
        self.mouth_y = 150
        self.mouth_width = 50
        self.mouth_height = 5
        self.mouth_close = True
        self.mouth_close_height = 20
        
        # エクスクラメーションマークの設定
        self.exclamation_x = 280
        self.exclamation_y = 20
        self.exclamation_width = 10
        self.exclamation_height = 30
        self.exclamation_space = 8
        
        # 状態変数
        self.eyes_closed = False
        self.exclamation_visible = False
        self.pale_visible = False
        self.current_text = ''
        self.text_visible = False
        self.speaking = False
        
        # メッセージキュー
        self.message_queue = queue.Queue()
        
        # タイマー設定
        self._setup_timers()
        
        self.app = None
    
    def _setup_timers(self):
        """各種タイマーの設定"""
        # まばたきタイマー
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)
        
        self.blink_close_timer = QTimer()
        self.blink_close_timer.timeout.connect(self.open_eyes)
        self.blink_close_timer.setSingleShot(True)
        
        # 口の動きタイマー
        self.mouth_timer = QTimer()
        self.mouth_timer.timeout.connect(self.toggle_mouth)
        
        # テキストスクロールタイマー
        self.text_timer = QTimer()
        self.text_timer.timeout.connect(self.update_text)
        
        # メッセージチェックタイマー
        self.message_check_timer = QTimer()
        self.message_check_timer.timeout.connect(self.check_messages)
        self.message_check_timer.start(100)

    def paintEvent(self, event):
        """描画イベント処理"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景を黒で塗りつぶし
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # 各パーツを描画
        self.draw_eyes(painter)
        self.draw_mouth(painter)
        
        if self.exclamation_visible:
            self.draw_exclamation(painter)
            
        if self.pale_visible:
            self.draw_pale(painter)
            
        if self.text_visible and self.current_text:
            self.draw_text(painter)
    
    def draw_eyes(self, painter):
        """目を描画"""
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        
        if self.eyes_closed:
            painter.fillRect(self.eye_close_x, self.eye_y, 
                           self.eye_close_width, self.eye_close_height, 
                           QColor(255, 255, 255))
            painter.fillRect(self.ww - self.eye_close_x - self.eye_close_width, 
                           self.eye_y, self.eye_close_width, self.eye_close_height, 
                           QColor(255, 255, 255))
        else:
            painter.drawEllipse(self.eye_x - self.eye_r, self.eye_y - self.eye_r, 
                              self.eye_r * 2, self.eye_r * 2)
            painter.drawEllipse(self.ww - self.eye_x - self.eye_r, self.eye_y - self.eye_r, 
                              self.eye_r * 2, self.eye_r * 2)
    
    def draw_mouth(self, painter):
        """口を描画"""
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        
        if self.mouth_close:
            # 閉じた口
            painter.fillRect(self.mouth_x, self.mouth_y, 
                           self.mouth_width, self.mouth_height, 
                           QColor(255, 255, 255))
        else:
            # 開いた口
            painter.fillRect(self.mouth_x, self.mouth_y - self.mouth_close_height // 2,
                           self.mouth_width, self.mouth_height + self.mouth_close_height, 
                           QColor(255, 255, 255))
    
    def draw_exclamation(self, painter):
        """エクスクラメーションマーク（！）を描画"""
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        
        # ビックリマークの棒部分
        painter.fillRect(self.exclamation_x, self.exclamation_y, 
                        self.exclamation_width, self.exclamation_height, 
                        QColor(255, 0, 0))
        # ビックリマークの点部分
        painter.fillRect(self.exclamation_x, 
                        self.exclamation_y + self.exclamation_height + self.exclamation_space,
                        self.exclamation_width, self.exclamation_width, 
                        QColor(255, 0, 0))
    
    def draw_pale(self, painter):
        """青ざめエフェクト（縦線）を描画"""
        painter.setPen(QPen(QColor(0, 0, 255), 2))
        painter.setBrush(QBrush(QColor(0, 0, 255)))
        
        # 右側の縦線群
        painter.fillRect(200, 0, 5, 40, QColor(0, 0, 255))
        painter.fillRect(220, 0, 5, 45, QColor(0, 0, 255))
        painter.fillRect(240, 0, 5, 50, QColor(0, 0, 255))
        painter.fillRect(260, 0, 5, 55, QColor(0, 0, 255))
        # 左側の縦線群
        painter.fillRect(40, 100, 5, 40, QColor(0, 0, 255))
        painter.fillRect(60, 103, 5, 35, QColor(0, 0, 255))
        painter.fillRect(80, 106, 5, 30, QColor(0, 0, 255))
        painter.fillRect(100, 109, 5, 25, QColor(0, 0, 255))
    
    def draw_text(self, painter):
        """テキストを画面下部に描画"""
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        font = QFont("Arial", 12)
        painter.setFont(font)
        
        # テキスト背景（白）
        painter.fillRect(0, self.wh - self.fh - 5, self.ww, self.fh + 5, 
                        QColor(255, 255, 255))
        
        # テキスト本体（黒）
        painter.drawText(5, self.wh - 8, self.current_text)
    
    def toggle_blink(self):
        """まばたきアニメーションを実行"""
        if not self.eyes_closed:
            self.eyes_closed = True
            self.update()
            self.blink_close_timer.start(self.blink_term_ms)
        
        # 次のまばたきをランダムな間隔でスケジュール
        next_blink = random.randint(2000, 6000)
        self.blink_timer.start(next_blink)
    
    def open_eyes(self):
        """目を開ける"""
        self.eyes_closed = False
        self.update()
    
    def toggle_mouth(self):
        """口の開閉を切り替え（リップシンク用）"""
        self.mouth_close = not self.mouth_close
        self.update()
    
    def update_text(self):
        """テキストをスクロールさせる"""
        if len(self.current_text) > 0:
            self.current_text = self.current_text[1:]
            self.update()
        else:
            # テキストが終了したらタイマーを停止
            self.text_timer.stop()
            self.text_visible = False
            self.mouth_timer.stop()
            self.mouth_close = True
            self.speaking = False
            self.update()
    
    def check_messages(self):
        """メッセージキューをチェックして読み上げを開始"""
        if not self.speaking and not self.message_queue.empty():
            text = self.message_queue.get()
            self._speak(text)
    
    def _speak(self, text):
        """
        テキストを読み上げる（内部処理）
        
        Args:
            text: 読み上げるテキスト
        """
        self.speaking = True
        self.current_text = text
        self.text_visible = True
        self.update()
        
        # 口のアニメーション開始
        self.mouth_timer.start(200)
        
        # テキストスクロール開始
        self.text_timer.start(200)

    def start(self):
        """アバターを起動"""
        self.show()
        # まばたきアニメーション開始
        self.blink_timer.start(random.randint(2000, 6000))

    def speak(self, text):
        """
        テキストを読み上げる（公開API）
        
        Args:
            text: 読み上げるテキスト
        """
        self.message_queue.put(text)

    def exclamation_on(self):
        """エクスクラメーションマークを表示"""
        self.exclamation_visible = True
        self.update()

    def exclamation_off(self):
        """エクスクラメーションマークを非表示"""
        self.exclamation_visible = False
        self.update()

    def pale_on(self):
        """青ざめエフェクトを表示"""
        self.pale_visible = True
        self.update()

    def pale_off(self):
        """青ざめエフェクトを非表示"""
        self.pale_visible = False
        self.update()
