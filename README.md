**Media Processing Service**

Сервіс для автоматичної генерації відео на основі комбінацій відео-, аудіо- та текстових блоків.
Проєкт призначений для обробки мультимедійного контенту, озвучування текстів, комбінування відео та збереження готових результатів у хмарне сховище **Google Cloud Storage (GCS)**.


---

## Запуск проєкту



```bash
docker compose up --build
```

Після запуску API буде доступне за адресою:
[http://localhost:5066/docs](http://localhost:5066/docs)
---

## Опис функціональності

Сервіс приймає **JSON** із блоками:

* **video_blocks** — відеофайли, з яких створюються комбінації
* **audio_blocks** — аудіофайли або музика для накладання
* **voice_blocks** — тексти для озвучування різними голосами

На основі цих блоків сервіс:

1. Генерує всі можливі комбінації відео.
2. Випадково накладає аудіо/озвучку.
3. Зберігає готові результати в хмару (GCS).

---

Якість згенерованого відео можна змінювати в сервісі 
**app/services/video_combiner.py**


## Ендпоінти

### `/process_media`

Використовується для запуску обробки мультимедійних блоків.
**Метод:** `POST`
**Адреса:** [http://localhost:5066/process_media](http://localhost:5066/process_media)

#### 🔹 Приклад JSON-запиту:

```json
{
  "task_name": "test_task_3blocks_with_audio",
  "video_blocks": {
    "block1": [
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/8081_O_GL_v1%20(1).mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/43r43.mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/2025-09-14%2016.02.30.mp4"
    ],
    "block2": [
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/8849_1.mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/IMG_5170.MP4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/Untitled%20design%20(5).mp4"
    ],
    "block3": [
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/Untitled%20design%20(8).mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/img_Asset_8320b1e5-fa98-4df0-876a-8b109b7b0969_dace9d4f-ab36-4c10-bd5d-b74fa58cbca3.mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/img_test3242task_7c062ef2-e570-43c6-9f0e-d92399e08282.mp4"
    ]
  },
  "audio_blocks": {
    "audio1": [
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/audiobible1.mp3",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/audiobible2.mp3",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/audiobible3.mp3"
    ]
  },
  "voice_blocks": {
    "voice1": [
      {
        "text": "Welcome to Plink — the ultimate platform for gamers who want to find perfect teammates...",
        "voice": "Sarah"
      },
      {
        "text": "Plink makes finding the right teammates effortless...",
        "voice": "George"
      },
      {
        "text": "Join millions of gamers who already use Plink...",
        "voice": "Will"
      }
    ]
  }
}
```

У відповідь API поверне **`task_id`**, який можна використовувати для перевірки статусу.

---

### `/task_status/{task_id}`

Перевірка статусу виконання задачі.
**Метод:** `GET`
**Адреса:**

```
http://localhost:5066/task_status/{task_id}
```

#### 🔹 Приклад:

```
http://localhost:5066/task_status/5678ca42-e94f-453a-b37b-fd0c4c719adf
```

---

## Збереження результатів

Після успішної генерації всі створені відео автоматично зберігаються у **Google Cloud Storage (GCS)**.
Посилання на готові файли повертаються у відповіді API або доступні через внутрішню систему керування завданнями.
