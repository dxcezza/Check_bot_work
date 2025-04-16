export interface Track {
  id: string;
  title: string;
  artist: string;
  album: string;
  cover_url: string | null;
  duration_ms: number;
  spotify_url: string;
  preview_url: string | null;
  track_url: string;
}

export interface SearchResponse {
  total_results: number;
  tracks: Track[];
} 