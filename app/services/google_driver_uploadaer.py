from pathlib import Path
from typing import List
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleDriveService:
    def __init__(self, project_name: str):
        self.project_name = project_name

        # Корень проекта
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.BASE_TEMP_DIR = self.BASE_DIR / "app" / "temp_files"

        # Файлы для авторизации Google
        self.credentials_file = self.BASE_DIR / "core" / "mycredentials.json"
        self.client_secrets_file = self.BASE_DIR / "core" / "client_secret_814344390131-ghjj334aoend3r7udesfsjkq9779vqkf.apps.googleusercontent.com.json"

        # Создаём директорию для токена, если её нет
        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)

        # Авторизация
        self.gauth = GoogleAuth()
        self.gauth.DEFAULT_SETTINGS['client_config_file'] = str(self.client_secrets_file)
        self.gauth.LoadCredentialsFile(str(self.credentials_file))

        if self.gauth.credentials is None:
            self.gauth.LocalWebserverAuth()
            self.gauth.SaveCredentialsFile(str(self.credentials_file))
        elif self.gauth.access_token_expired:
            self.gauth.Refresh()
            self.gauth.SaveCredentialsFile(str(self.credentials_file))
        else:
            self.gauth.Authorize()

        self.drive = GoogleDrive(self.gauth)

        # 1️⃣ Папка "video_generator" на Google Drive
        self.main_folder_id = self._get_or_create_folder("video_generator")
        # 2️⃣ Папка с названием проекта внутри "video_generator"
        self.project_folder_id = self._get_or_create_folder(self.project_name, parent_id=self.main_folder_id)

    def _get_or_create_folder(self, folder_name: str, parent_id: str = None) -> str:
        """Ищет или создаёт папку на Google Drive. Если указан parent_id, создаётся внутри родителя"""
        query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        file_list = self.drive.ListFile({'q': query}).GetList()

        if file_list:
            print(f"📁 Папка найдена на Drive: {folder_name}")
            return file_list[0]['id']

        folder_metadata = {'title': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        if parent_id:
            folder_metadata['parents'] = [{'id': parent_id}]

        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()
        print(f"📁 Папка создана на Drive: {folder_name}")
        return folder['id']

    def upload_files(self) -> List[str]:
        """Ищет папку done для текущего проекта и загружает все файлы"""
        local_folder_path = self.BASE_TEMP_DIR / self.project_name / "done"
        if not local_folder_path.exists() or not local_folder_path.is_dir():
            raise FileNotFoundError(f"Папка не найдена: {local_folder_path}")

        uploaded_files = []
        for file_path in local_folder_path.glob("*"):
            if file_path.is_file():
                gfile = self.drive.CreateFile({
                    'title': file_path.name,
                    'parents': [{'id': self.project_folder_id}]
                })
                gfile.SetContentFile(str(file_path))
                gfile.Upload()
                uploaded_files.append(file_path.name)
                print(f"📤 Загружен: {file_path.name}")

        return uploaded_files


if __name__ == "__main__":
    # Передаём только имя проекта
    drive_service = GoogleDriveService(project_name="test_task_3blocks_with_audio")
    uploaded_files = drive_service.upload_files()

    print(f"\n✅ Всего файлов загружено: {len(uploaded_files)}")
    for f in uploaded_files:
        print(f" - {f}")
