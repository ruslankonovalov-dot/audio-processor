import os
from auth import get_creds
from ai_logic import process_audio_with_gemini
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ВСТАВЬ СВОИ ID СЮДА
SOURCE_FOLDER_ID = '1dpKG-eaFg2glOovkI4sYgLyPo3mW9Ilg'
SHEET_ID = '16I6nqmaD-AjkKF7sQWWQPRn0xnVdS9HBbwBFTe-_y0U'

def main():
    creds = get_creds()
    drive = build('drive', 'v3', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)

    results = drive.files().list(
        q=f"'{SOURCE_FOLDER_ID}' in parents and mimeType contains 'audio/'",
        fields="files(id, name)"
    ).execute()
    files = results.get('files', [])

    if not files:
        print("Файлы не найдены.")
        return

    for f in files:
        print(f"Обработка: {f['name']}...")
        
        # Скачиваем локально
        request = drive.files().get_media(fileId=f['id'])
        file_path = f['name']
        with open(file_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        # Транскрибация и анализ через Gemini за один запрос
        try:
            result = process_audio_with_gemini(file_path)
            
            # Подготовка строки для таблицы
            # Формат: [Имя файла, Тип, Оценка, Комментарий]
            row = [f['name'], result['type'], result['score'], result['comment']]
            
            sheets.spreadsheets().values().append(
                spreadsheetId=SHEET_ID,
                range="A2",
                valueInputOption="USER_ENTERED",
                body={"values": [row]}
            ).execute()
            
            print(f"Успешно записано: {f['name']}")
        except Exception as e:
            print(f"Ошибка при обработке {f['name']}: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    main()