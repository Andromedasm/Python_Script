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
            self.check_and_upload(file_path)

    def check_and_upload(self, file_path):
        last_size = -1
        current_size = os.path.getsize(file_path)
        while current_size != last_size:
            time.sleep(5)  # 等待5秒再次检查文件大小
            last_size = current_size
            current_size = os.path.getsize(file_path)

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
