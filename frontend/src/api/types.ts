export type TranscriptionTarget = "standard" | "tab" | "both";

export interface Song {
  id: number;
  title: string;
  artist: string | null;
  audio_file_path: string | null;
  created_at: string;
}

export interface Job {
  id: number;
  song_id: number;
  sheet_id: number | null;
  target: string;
  status: string;
  result_message: string;
  created_at: string;
}

export interface SheetDetail {
  id: number;
  song_id: number;
  target: string;
  share_token: string | null;
  created_at: string;
  musicxml: string;
  editor_json: string | null;
  version_number: number;
}

export interface ShareLink {
  share_token: string;
  share_path: string;
}

export interface EditorJson {
  title: string;
  target: string;
  source?: string;
  tab?: {
    lines: string[];
  };
}
