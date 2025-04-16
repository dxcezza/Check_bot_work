import React from 'react';
import { Play, Clock, Download } from 'lucide-react';
import axios from 'axios';
import type { Track } from '../types';

interface TrackListProps {
  tracks: Track[];
  onTrackSelect: (track: Track) => void;
}

export function TrackList({ tracks, onTrackSelect }: TrackListProps) {
  const formatDuration = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(0);
    return `${minutes}:${Number(seconds) < 10 ? '0' : ''}${seconds}`;
  };

  const handleDownload = async (track: Track) => {
    try {
      const response = await axios.post('/api/download', {
        track_url: track.track_url
      }, {
        responseType: 'blob'
      });

      // Создаем ссылку для скачивания
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${track.title} - ${track.artist}.mp3`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Ошибка при скачивании:', error);
      alert('Произошла ошибка при скачивании трека');
    }
  };

  return (
    <div className="space-y-3">
      {tracks.map((track) => (
        <div
          key={track.id}
          className="group relative flex items-center gap-6 p-4 hover:bg-gray-800/50 rounded-2xl cursor-pointer transition-all duration-300 hover:scale-[1.02]"
          onClick={() => onTrackSelect(track)}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-violet-500/0 via-fuchsia-500/0 to-pink-500/0 rounded-2xl transition-all duration-300 opacity-0 group-hover:opacity-10" />
          
          <div className="relative">
            <img
              src={track.cover_url || 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&h=300&fit=crop'}
              alt={track.title}
              className="w-20 h-20 rounded-xl shadow-lg object-cover transition-transform duration-300 group-hover:shadow-2xl group-hover:shadow-violet-500/20"
            />
            <button className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-all duration-300 rounded-xl backdrop-blur-sm">
              <Play className="w-10 h-10 text-white transform translate-x-0.5" fill="white" />
            </button>
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-100 text-lg truncate group-hover:text-violet-300 transition-colors duration-300">
              {track.title}
            </h3>
            <p className="text-gray-300 truncate mt-1 group-hover:text-gray-200 transition-colors duration-300">
              {track.artist}
            </p>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3 text-sm text-gray-300 group-hover:text-gray-200 transition-colors duration-300">
              <Clock className="w-4 h-4" />
              <span>{formatDuration(track.duration_ms)}</span>
            </div>

            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDownload(track);
              }}
              className="p-2 hover:bg-white/10 rounded-full transition-colors duration-300"
              title="Скачать трек"
            >
              <Download className="w-5 h-5 text-gray-300" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
} 