from pathlib import Path
from typing import List
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleDriveService:
    def __init__(
        self,
        folder_name: str = "video_generator",
        credentials_file: str = "core/mycredentials.json",
        client_secrets_file: str = "core/client_secret_814344390131-ghjj334aoend3r7udesfsjkq9779vqkf.apps.googleusercontent.com.json"
    ):
        """
        :param folder_name: Имя папки на Google Drive
        :param credentials_file: Файл с токеном OAuth2 (сохраняется после первого запуска)
        :param client_secrets_file: Файл client_secrets.json от Google
        """
        self.folder_name = folder_name
        self.credentials_file = credentials_file
        self.client_secrets_file = client_secrets_file

        # Авторизация
        self.gauth = GoogleAuth()
        self.gauth.DEFAULT_SETTINGS['client_config_file'] = self.client_secrets_file
        self.gauth.LoadCredentialsFile(self.credentials_file)

        if self.gauth.credentials is None:
            # Первый запуск - откроется браузер для авторизации
            self.gauth.LocalWebserverAuth()
            self.gauth.SaveCredentialsFile(self.credentials_file)
        elif self.gauth.access_token_expired:
            self.gauth.Refresh()
            self.gauth.SaveCredentialsFile(self.credentials_file)
        else:
            self.gauth.Authorize()

        self.drive = GoogleDrive(self.gauth)
        self.folder_id = self._get_or_create_folder(self.folder_name)

    def _get_or_create_folder(self, folder_name: str) -> str:
        """Ищет или создаёт папку на Google Drive"""
        file_list = self.drive.ListFile({
            'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        }).GetList()

        if file_list:
            print(f"📁 Папка найдена: {folder_name}")
            return file_list[0]['id']

        folder = self.drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        })
        folder.Upload()
        print(f"📁 Папка создана: {folder_name}")
        return folder['id']

    def upload_files(self, local_folder: str) -> List[str]:
        """Загружает все файлы из локальной папки"""
        local_folder_path = Path(local_folder)
        if not local_folder_path.exists() or not local_folder_path.is_dir():
            raise FileNotFoundError(f"Папка не найдена: {local_folder}")

        uploaded_files = []
        for file_path in local_folder_path.glob("*"):
            if file_path.is_file():
                gfile = self.drive.CreateFile({
                    'title': file_path.name,
                    'parents': [{'id': self.folder_id}]
                })
                gfile.SetContentFile(str(file_path))
                gfile.Upload()
                uploaded_files.append(file_path.name)
                print(f"📤 Загружен: {file_path.name}")

        return uploaded_files


if __name__ == "__main__":
    LOCAL_FOLDER = Path("app/temp_files/test_task_3blocks_with_audio/done")
    DRIVE_FOLDER = "video_generator"
    CREDENTIALS_FILE = "core/mycredentials.json"  # токен OAuth2
    # Инициализация сервиса
    drive_service = GoogleDriveService(
        folder_name=DRIVE_FOLDER,
        credentials_file=CREDENTIALS_FILE,
        client_secrets_file="client_secret_814344390131-ghjj334aoend3r7udesfsjkq9779vqkf.apps.googleusercontent.com.json"
    )
    # Загружаем файлы
    uploaded_files = drive_service.upload_files(str(LOCAL_FOLDER))

    print(f"\n✅ Всего файлов загружено: {len(uploaded_files)}")
    for f in uploaded_files:
        print(f" - {f}")
