"""
Created on Fri Jan 17 21:37:27 2025

@author: marce
"""
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.process import process_file
import time
from app.logger import logger

# Detectar arquivos xlsx e csv
class NewFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith((".xls", ".xlsx", ".csv")):
            print(f"Detectado xlsx novo/modificado: {event.src_path}")
            process_file(event.src_path) #self.

# Configuração do monitoramento
def start_monitoring(folder_to_watch):
    print(f"Monitorando a pasta: {folder_to_watch}")
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()
    
    try:
        logger.info(f"Iniciando monitoramento da pasta: {folder_to_watch}")
        while True:
            time.sleep(1) # Mantém o monitoramento ativo
    except KeyboardInterrupt:
        observer.stop()
    observer.join()