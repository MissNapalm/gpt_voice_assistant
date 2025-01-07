import sys
import threading
import queue
import speech_recognition as sr
import subprocess
from openai import OpenAI
import os
from dotenv import load_dotenv
import time
from elevenlabs.client import ElevenLabs
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, 
                           QTextEdit, QPushButton, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCursor, QMouseEvent
from easter_eggs import get_easter_egg_response

class SignalEmitter(QObject):
    update_text_signal = pyqtSignal(str, bool)
    listening_signal = pyqtSignal(bool)
    thinking_signal = pyqtSignal(bool)
    transcribe_signal = pyqtSignal(str)
    response_ready_signal = pyqtSignal(str)

class AriaAssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.update_text_signal.connect(self.update_chat)
        self.signal_emitter.transcribe_signal.connect(self.update_transcription)
        self.signal_emitter.thinking_signal.connect(self.update_thinking_indicator)
        self.signal_emitter.response_ready_signal.connect(self.display_response)
        
        # Dragging variables
        self._dragging = False
        self._drag_start_position = QPoint()
        
        self.initUI()
        self.assistant = SimpleVoiceAssistant(self.signal_emitter)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton and self._dragging:
            self.move(event.globalPos() - self._drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()

    def initUI(self):
        self.setWindowTitle('Aria AI Assistant')
        self.setGeometry(100, 100, 800, 600)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Thinking Label
        self.thinking_label = QLabel()
        self.thinking_label.setStyleSheet("""
            color: #00FFFF;
            font-size: 18px;
            font-weight: bold;
            background-color: rgba(0, 30, 60, 0.8);
            border: 2px solid #00FFFF;
            border-radius: 10px;
            padding: 15px;
            margin: 0 50px;
            text-align: center;
        """)
        self.thinking_label.setAlignment(Qt.AlignCenter)
        self.thinking_label.hide()
        main_layout.addWidget(self.thinking_label)
        
        # Transcription Label
        self.transcription_label = QLabel("Transcription: ")
        self.transcription_label.setStyleSheet("""
            color: #00BFFF;
            font-size: 14px;
            padding: 10px;
            font-weight: bold;
            background-color: rgba(0, 20, 40, 0.5);
            border-radius: 5px;
        """)
        main_layout.addWidget(self.transcription_label)
        
        # Chat Area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #001020;
                color: #00FFFF;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                border: 2px solid #00BFFF;
                border-radius: 10px;
                padding: 15px;
            }
            QScrollBar:vertical {
                background-color: rgba(0, 30, 60, 0.5);
                width: 15px;
                margin: 15px 0 15px 0;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background-color: #00BFFF;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        main_layout.addWidget(self.chat_area)
        
        # Start Listening Button
        self.listen_btn = QPushButton('Start Listening')
        self.listen_btn.setStyleSheet("""
        QPushButton {
            background-color: rgba(0, 30, 60, 0.8);
            color: #00FFFF;
            border: 2px solid #00BFFF;
            border-radius: 10px;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        QPushButton:hover {
            background-color: rgba(0, 50, 100, 0.9);
            border-color: white;
        }
        QPushButton:pressed {
            background-color: rgba(0, 20, 40, 0.9);
        }
        """)
        self.listen_btn.clicked.connect(self.start_listening)
        main_layout.addWidget(self.listen_btn)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.setStyleSheet("""
        QMainWindow {
            background-color: #000C1F;
            color: #00FFFF;
        }
        """)
        
        # Add a subtle drop shadow and make window draggable
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setContentsMargins(10, 10, 10, 10)

    def update_thinking_indicator(self, is_thinking):
        if is_thinking:
            self.thinking_label.setText("Thinking...")
            self.thinking_label.show()
        else:
            self.thinking_label.hide()

    def display_response(self, text):
        self.update_chat(text, False)

    def update_transcription(self, text):
        self.transcription_label.setText(f"Transcription: {text}")

    def update_listening_indicator(self, is_listening):
        # Removed as requested
        pass

    def start_listening(self):
        self.listen_btn.setEnabled(False)
        threading.Thread(target=self.assistant.run, daemon=True).start()
        QTimer.singleShot(5000, lambda: self.listen_btn.setEnabled(True))

    def update_chat(self, text, is_user=True):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_area.setTextCursor(cursor)
        
        prefix = "USER >>> " if is_user else "ARIA >>> "
        color = "#00BFFF" if is_user else "#00FFFF"
        
        self.chat_area.setTextColor(QColor(color))
        self.chat_area.insertPlainText(f"{prefix}{text}\n")
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )

class SimpleVoiceAssistant:
    def __init__(self, signal_emitter):
        self.signal_emitter = signal_emitter
        load_dotenv()
        
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.eleven = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
        self.response_cache = {}
        self.is_speaking = False
        self.is_listening = False
        self.stop_listening = threading.Event()
        
        # Voice settings
        self.voice_settings = {
            "voice": "Glinda",
            "model": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.95,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            }
        }

    def get_gpt_response(self, text):
        self.signal_emitter.thinking_signal.emit(True)
        
        if text in self.response_cache:
            return self.response_cache[text]

        try:
            full_response = ""
            for chunk in self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Aria, a concise AI assistant. Always respond in 1-2 sentences maximum, even for complex questions. Never use lists or bullet points."},
                    {"role": "user", "content": text}
                ],
                stream=True,
                max_tokens=100  # Limit response length
            ):
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            self.response_cache[text] = full_response
            return full_response
        
        except Exception as e:
            print(f"Error: {e}")
            return "System error. Unable to process request."

    def speak(self, text):
        if self.is_speaking:
            return
        
        try:
            self.is_speaking = True
            self.is_listening = False
            
            self.signal_emitter.thinking_signal.emit(True)
            self.signal_emitter.listening_signal.emit(False)
            
            def generate_and_play():
                try:
                    audio = self.eleven.generate(text=text, **self.voice_settings)
                    
                    with open("temp_audio.mp3", "wb") as f:
                        for chunk in audio:
                            f.write(chunk)
                    
                    self.signal_emitter.thinking_signal.emit(False)
                    self.signal_emitter.response_ready_signal.emit(text)
                    subprocess.run(['afplay', 'temp_audio.mp3'], check=True)
                    
                except Exception as e:
                    print(f"ElevenLabs audio generation/playback error: {e}")
                    # Emit the text response even if audio fails
                    self.signal_emitter.response_ready_signal.emit(text)
                
                finally:
                    # Clean up the temporary audio file
                    try:
                        if os.path.exists("temp_audio.mp3"):
                            os.remove("temp_audio.mp3")
                    except Exception as e:
                        print(f"Error removing temporary audio file: {e}")
                    
                    self.signal_emitter.thinking_signal.emit(False)
                    self.is_speaking = False
                    self.is_listening = False
                    self.signal_emitter.listening_signal.emit(True)
            
            threading.Thread(target=generate_and_play, daemon=True).start()
        
        except Exception as e:
            print(f"Speaking error: {e}")
            self.signal_emitter.thinking_signal.emit(False)
            self.is_speaking = False
            self.is_listening = False
            self.signal_emitter.listening_signal.emit(True)
            
            threading.Thread(target=generate_and_play, daemon=True).start()
        
        except Exception as e:
            print(f"Speaking error: {e}")
            self.signal_emitter.thinking_signal.emit(False)
            self.is_speaking = False
            self.is_listening = False
            self.signal_emitter.listening_signal.emit(True)

    def run(self):
        self.signal_emitter.listening_signal.emit(True)
        self.speak("Initializing Aria system. Ready for input.")
        self.stop_listening.clear()
        
        while not self.stop_listening.is_set():
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                    
                    while self.is_speaking:
                        time.sleep(0.1)
                    
                    self.is_listening = True
                    self.signal_emitter.listening_signal.emit(True)
                    
                    try:
                        audio = self.recognizer.listen(
                            source,
                            timeout=10,
                            phrase_time_limit=10
                        )
                        
                        def process_audio():
                            try:
                                if self.is_speaking:
                                    return
                                
                                text = None
                                for _ in range(3):
                                    try:
                                        text = self.recognizer.recognize_google(audio).lower()
                                        self.signal_emitter.transcribe_signal.emit(text)
                                        break
                                    except sr.UnknownValueError:
                                        time.sleep(0.1)
                                
                                if not text:
                                    print("Could not understand audio after multiple attempts")
                                    return
                                
                                self.signal_emitter.update_text_signal.emit(text, True)
                                
                                if text == "exit":
                                    self.speak("Shutting down. Goodbye.")
                                    self.stop_listening.set()
                                    return
                                
                                # Check for easter egg responses first
                                easter_egg = get_easter_egg_response(text)
                                if easter_egg:
                                    self.speak(easter_egg)
                                    return
                                    
                                # If no easter egg found, get GPT response
                                response = self.get_gpt_response(text)
                                self.speak(response)
                            
                            except Exception as e:
                                print(f"Processing error: {e}")
                            finally:
                                self.is_listening = False
                        
                        threading.Thread(target=process_audio, daemon=True).start()
                    
                    except sr.WaitTimeoutError:
                        self.is_listening = False
            
            except Exception as e:
                print(f"Listening error: {e}")
                self.is_listening = False
                time.sleep(0.1)

def main():
    app = QApplication(sys.argv)
    aria = AriaAssistantUI()
    aria.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
