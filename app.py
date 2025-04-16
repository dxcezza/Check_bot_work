from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import uuid
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

# Конфигурация API
tr_url = "https://spotify-downloader9.p.rapidapi.com/downloadSong"
headers = {
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    "x-rapidapi-host": os.getenv("RAPIDAPI_HOST")
}

# Инициализация Spotify клиента
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

print(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))
print(headers)
      
def download_track(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            return False
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False
        
@app.route("/")
def index():
    return send_from_directory(app.static_folder, 'index.html')
    
@app.route('/search', methods=['GET'])
def search_tracks():
    try:
        query = request.args.get('q')
        print(f"Получен запрос поиска с параметром q: {query}")
        
        if not query:
            return jsonify({"error": "Необходимо указать параметр q для поиска"}), 400

        results = sp.search(q=query, type='track', limit=10)
        print(f"Получены результаты от Spotify API: {len(results['tracks']['items'])} треков")
        
        tracks = []
        for track in results['tracks']['items']:
            track_info = {
                "id": track['id'],
                "title": track['name'],
                "artist": track['artists'][0]['name'],
                "album": track['album']['name'],
                "cover_url": track['album']['images'][0]['url'] if track['album']['images'] else None,
                "duration_ms": track['duration_ms'],
                "spotify_url": track['external_urls']['spotify'],
                "preview_url": track['preview_url'],
                "track_url": f"https://open.spotify.com/track/{track['id']}"
            }
            tracks.append(track_info)
        
        response_data = {
            "total_results": len(tracks),
            "tracks": tracks
        }
        print(f"Отправляем ответ: {response_data}")
        return jsonify(response_data)
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download_spotify_track():
    try:
        data = request.json
        if not data or 'track_url' not in data:
            return jsonify({"error": "Необходимо указать track_url"}), 400

        track_url = data['track_url']
        querystring = {"songId": track_url.split('/')[-1]}  # Извлекаем ID трека из URL
        
        response = requests.get(tr_url, headers=headers, params=querystring)
        if response.status_code != 200:
            return jsonify({"error": "Ошибка при получении ссылки на скачивание"}), 500

        data = response.json()
        download_url = data['data']['downloadLink']
        
        filename = f"{uuid.uuid4()}.mp3"
        save_path = os.path.join("downloads", filename)
        
        os.makedirs("downloads", exist_ok=True)
        
        if download_track(download_url, save_path):
            return send_file(save_path, as_attachment=True)
        else:
            return jsonify({"error": "Ошибка при скачивании трека"}), 500
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
