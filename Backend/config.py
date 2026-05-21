import os

class Config:
    SECRET_KEY = os.urandom(24)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'best_pet_model.pth')
    
    @classmethod
    def init_folders(cls):
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)