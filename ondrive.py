import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from onedrivesdk import OneDriveClient, FileSystemTokenBackedModelAdapter

# 初始化OneDrive客户端
client_id = 'your_client_id'
client_secret = 'your_client_secret'
redirect_uri = 'http://localhost'
client = OneDriveClient(
    'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    client_id,
    client_secret,
    redirect_uri,
    FileSystemTokenBackedModelAdapter('token.json')
)

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            self.upload_and_delete(file_path)

    def upload_and_delete(self, file_path):
        # 上传文件到OneDrive
        remote_path = '/path/on/onedrive/' + os.path.basename(file_path)
        client.item(drive='me', id='root').children[os.path.basename(file_path)].upload(file_path)

        # 确认上传成功后删除本地文件
        if client.item(drive='me', id='root').children[os.path.basename(file_path)].get():
            os.remove(file_path)

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='/path/to/watch', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
