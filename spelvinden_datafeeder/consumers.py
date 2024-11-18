import time
from channels.generic.websocket import WebsocketConsumer
import json


class ProgressBarConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        # Simulate a long-running task
        for progress in range(101):
            time.sleep(0.1)  # Simulate task time
            self.send(json.dumps({'progress': progress}))
