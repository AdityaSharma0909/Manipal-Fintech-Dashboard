import threading
from abc import ABC, abstractmethod

class BackgroundTask(ABC, threading.Thread):


    @abstractmethod
    def process(self, **kwargs):
        pass
    #threading method
    def run(self, *args, **kwargs):
       self.process()
