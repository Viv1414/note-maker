import { FormEvent, useState } from "react";
import { createSong, getSheet, transcribeSong, waitForJob } from "../api/client";
import type { SheetDetail, TranscriptionTarget } from "../api/types";

interface Props {
  onSheetReady: (sheet: SheetDetail) => void;
  onStatus?: (message: string | null) => void;
}

export function UploadForm({ onSheetReady, onStatus }: Props) {
  const [title, setTitle] = useState("");
  const [artist, setArtist] = useState("");
  const [target, setTarget] = useState<TranscriptionTarget>("both");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!file || !title.trim()) {
      setError("Title and audio file are required.");
      return;
    }

    setLoading(true);
    setError(null);
    onStatus?.("Uploading audio...");
    try {
      const song = await createSong({
        title: title.trim(),
        artist: artist.trim() || undefined,
        audioFile: file,
      });
      onStatus?.("Transcribing audio...");
      const job = await transcribeSong(song.id, target);
      const finished = await waitForJob(job.id);
      if (finished.status === "failed") {
        throw new Error(finished.result_message || "Transcription failed.");
      }
      if (!finished.sheet_id) {
        throw new Error("Transcription did not return a sheet.");
      }
      const sheet = await getSheet(finished.sheet_id);
      onSheetReady(sheet);
      onStatus?.(finished.result_message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      onStatus?.(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <label>
        Song title
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="e.g. Happy Birthday"
          required
        />
      </label>
      <label>
        Artist (optional)
        <input
          value={artist}
          onChange={(event) => setArtist(event.target.value)}
          placeholder="Artist name"
        />
      </label>
      <label>
        Output type
        <select
          value={target}
          onChange={(event) => setTarget(event.target.value as TranscriptionTarget)}
        >
          <option value="both">Standard notation + tab</option>
          <option value="standard">Standard notation</option>
          <option value="tab">Guitar tab</option>
        </select>
      </label>
      <label>
        Audio file
        <input
          type="file"
          accept="audio/*"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          required
        />
      </label>
      <button type="submit" disabled={loading}>
        {loading ? "Generating..." : "Generate sheet"}
      </button>
      {error ? <p className="error">{error}</p> : null}
    </form>
  );
}
