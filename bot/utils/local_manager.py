import os
import shutil

class LocalManager:
    def __init__(self, folder_path: str = "bot/temp"):
        self.folder_path = folder_path
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            
    def save_photo(self, photo_bytes: bytes, filename: str) -> str:
        file_path = os.path.join(self.folder_path, filename)
        with open(file_path, 'wb') as file:
            file.write(photo_bytes)
        return file_path
    
    def delete_photo(self, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False