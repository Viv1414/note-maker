import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { getSharedSheet } from "./api/client";
import { UploadForm } from "./components/UploadForm";
import { SheetViewer } from "./components/SheetViewer";
import type { SheetDetail } from "./api/types";

export default function App() {
  const [sheet, setSheet] = useState<SheetDetail | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const sharedToken = useMemo(() => readSharedToken(), []);

  useEffect(() => {
    if (!sharedToken) {
      return;
    }
    getSharedSheet(sharedToken)
      .then(setSheet)
      .catch((err) => setStatus(err instanceof Error ? err.message : "Could not load shared sheet."));
  }, [sharedToken]);

  if (sharedToken) {
    return (
      <div className="app">
        <header>
          <h1>Shared sheet</h1>
          <p>Read-only view of a shared music sheet.</p>
        </header>
        {status && !sheet ? <p className="error">{status}</p> : null}
        {sheet ? (
          <section className="panel">
            <SheetViewer sheet={sheet} onSheetUpdated={setSheet} readOnly />
          </section>
        ) : null}
      </div>
    );
  }

  return (
    <div className="app">
      <header>
        <h1>Note Maker</h1>
        <p>Upload a song and generate printable sheet music or guitar tabs.</p>
      </header>
      <section className="panel">
        <UploadForm onSheetReady={setSheet} onStatus={setStatus} />
        {status ? <p className="sheet-meta">{status}</p> : null}
      </section>
      {sheet ? (
        <section className="panel">
          <SheetViewer sheet={sheet} onSheetUpdated={setSheet} />
        </section>
      ) : null}
    </div>
  );
}

function readSharedToken(): string | null {
  const match = window.location.pathname.match(/^\/shared\/([^/]+)/);
  return match?.[1] ?? null;
}
