import { useEffect, useRef, useState } from "react";
import { createShareLink, saveSheetVersion } from "../api/client";
import type { EditorJson, SheetDetail } from "../api/types";

interface Props {
  sheet: SheetDetail;
  onSheetUpdated: (sheet: SheetDetail) => void;
  readOnly?: boolean;
}

export function SheetViewer({ sheet, onSheetUpdated, readOnly = false }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorData: EditorJson | null = sheet.editor_json
    ? JSON.parse(sheet.editor_json)
    : null;
  const [tabText, setTabText] = useState(editorData?.tab?.lines?.join("\n") ?? "");
  const [saving, setSaving] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    setTabText(editorData?.tab?.lines?.join("\n") ?? "");
  }, [sheet.id, sheet.version_number]);

  useEffect(() => {
    let cancelled = false;

    async function render() {
      if (!containerRef.current || !sheet.musicxml) {
        return;
      }
      containerRef.current.innerHTML = "";
      try {
        const { OpenSheetMusicDisplay } = await import("opensheetmusicdisplay");
        if (cancelled || !containerRef.current) {
          return;
        }
        const osmd = new OpenSheetMusicDisplay(containerRef.current, {
          autoResize: true,
        });
        await osmd.load(sheet.musicxml);
        osmd.render();
      } catch {
        if (containerRef.current) {
          containerRef.current.innerHTML =
            "<p>Could not render notation. Run npm install in the frontend folder.</p>";
        }
      }
    }

    void render();
    return () => {
      cancelled = true;
    };
  }, [sheet.musicxml]);

  async function handleSaveTab() {
    if (!sheet.editor_json) {
      return;
    }
    setSaving(true);
    setMessage(null);
    try {
      const parsed: EditorJson = JSON.parse(sheet.editor_json);
      const updated: EditorJson = {
        ...parsed,
        tab: { lines: tabText.split("\n") },
      };
      const next = await saveSheetVersion(sheet.id, {
        editor_json: JSON.stringify(updated),
      });
      onSheetUpdated(next);
      setMessage("Saved new version.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Save failed.");
    } finally {
      setSaving(false);
    }
  }

  async function handleShare() {
    setMessage(null);
    try {
      const link = await createShareLink(sheet.id);
      const url = `${window.location.origin}/shared/${link.share_token}`;
      setShareUrl(url);
      await navigator.clipboard.writeText(url);
      setMessage("Share link copied to clipboard.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Could not create share link.");
    }
  }

  function handlePrint() {
    window.print();
  }

  function handleDownloadXml() {
    const blob = new Blob([sheet.musicxml], { type: "application/xml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `sheet-${sheet.id}.musicxml`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="sheet-viewer">
      <h2>Generated sheet</h2>
      <p className="sheet-meta">
        Sheet #{sheet.id} · version {sheet.version_number} · target: {sheet.target}
        {editorData?.source ? ` · source: ${editorData.source}` : ""}
      </p>
      <div className="osmd-container" ref={containerRef} />
      {(targetIncludesTab(sheet.target) || tabText) && (
        <div className="tab-block panel" style={{ marginTop: "1rem" }}>
          <h3>Guitar tab</h3>
          {readOnly ? (
            <pre>{tabText}</pre>
          ) : (
            <>
              <textarea
                className="tab-editor"
                value={tabText}
                onChange={(event) => setTabText(event.target.value)}
                rows={8}
              />
              <button type="button" onClick={handleSaveTab} disabled={saving}>
                {saving ? "Saving..." : "Save tab edits"}
              </button>
            </>
          )}
        </div>
      )}
      <div className="actions">
        <button type="button" onClick={handlePrint}>
          Print
        </button>
        <button type="button" onClick={handleDownloadXml}>
          Download MusicXML
        </button>
        {!readOnly ? (
          <button type="button" onClick={handleShare}>
            Share
          </button>
        ) : null}
      </div>
      {shareUrl ? <p className="sheet-meta">Share URL: {shareUrl}</p> : null}
      {message ? <p className="sheet-meta">{message}</p> : null}
    </section>
  );
}

function targetIncludesTab(target: string) {
  return target === "tab" || target === "both";
}
