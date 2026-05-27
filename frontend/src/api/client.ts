import type { Job, ShareLink, SheetDetail, Song, TranscriptionTarget } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function createSong(params: {
  title: string;
  artist?: string;
  audioFile: File;
}): Promise<Song> {
  const form = new FormData();
  form.append("title", params.title);
  if (params.artist) {
    form.append("artist", params.artist);
  }
  form.append("audio_file", params.audioFile);
  return request<Song>("/songs", { method: "POST", body: form });
}

export async function transcribeSong(
  songId: number,
  target: TranscriptionTarget,
): Promise<Job> {
  return request<Job>(`/songs/${songId}/transcribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target }),
  });
}

export async function getJob(jobId: number): Promise<Job> {
  return request<Job>(`/jobs/${jobId}`);
}

export async function waitForJob(jobId: number, timeoutMs = 120000): Promise<Job> {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const job = await getJob(jobId);
    if (job.status === "completed" || job.status === "failed") {
      return job;
    }
    await sleep(1000);
  }
  throw new Error("Transcription timed out.");
}

export async function getSheet(sheetId: number): Promise<SheetDetail> {
  return request<SheetDetail>(`/sheets/${sheetId}`);
}

export async function getSharedSheet(token: string): Promise<SheetDetail> {
  return request<SheetDetail>(`/shared/${token}`);
}

export async function saveSheetVersion(
  sheetId: number,
  payload: { editor_json?: string; musicxml?: string },
): Promise<SheetDetail> {
  return request<SheetDetail>(`/sheets/${sheetId}/versions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function createShareLink(sheetId: number): Promise<ShareLink> {
  return request<ShareLink>(`/sheets/${sheetId}/share`, { method: "POST" });
}
