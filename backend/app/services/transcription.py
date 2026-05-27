"""Audio transcription: optional basic-pitch, music21 MIDI conversion, stub fallback."""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Standard guitar tuning: string label -> open-string MIDI note number
GUITAR_STRINGS: list[tuple[str, int]] = [
    ("e", 64),
    ("B", 59),
    ("G", 55),
    ("D", 50),
    ("A", 45),
    ("E", 40),
]


@dataclass
class TranscriptionResult:
    musicxml: str
    editor_json: str
    source: str
    message: str


def transcribe_audio(
    audio_path: str | None,
    title: str,
    artist: str | None,
    target: str,
) -> TranscriptionResult:
    if not audio_path or not Path(audio_path).exists():
        return _stub_result(title, artist, target, "No audio file found; using placeholder sheet.")

    midi_path = _audio_to_midi(audio_path)
    if midi_path is None:
        return _stub_result(
            title,
            artist,
            target,
            "Install optional ML deps (see requirements-ml.txt) for real transcription; using placeholder.",
        )

    try:
        musicxml = _midi_to_musicxml(midi_path, title, artist)
        editor_json = _build_editor_json_from_musicxml(musicxml, title, target, source="basic-pitch")
        return TranscriptionResult(
            musicxml=musicxml,
            editor_json=editor_json,
            source="basic-pitch",
            message="Transcribed audio with basic-pitch and converted to MusicXML.",
        )
    except Exception as exc:
        return _stub_result(title, artist, target, f"Transcription failed ({exc}); using placeholder.")


def _stub_result(title: str, artist: str | None, target: str, message: str) -> TranscriptionResult:
    return TranscriptionResult(
        musicxml=build_stub_musicxml(title, artist),
        editor_json=build_stub_editor_json(title, target, source="stub"),
        source="stub",
        message=message,
    )


def _audio_to_midi(audio_path: str) -> str | None:
    try:
        from basic_pitch.inference import predict
        from basic_pitch import ICASSP_2022_MODEL_PATH
    except ImportError:
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        _, midi_data, _ = predict(audio_path, ICASSP_2022_MODEL_PATH)
        if not midi_data:
            return None
        output = Path(tmpdir) / "transcription.mid"
        midi_data.write(str(output))
        # Copy to a persistent temp file because tmpdir is deleted on exit
        persistent = Path(tempfile.gettempdir()) / f"note-maker-{Path(audio_path).stem}.mid"
        persistent.write_bytes(output.read_bytes())
        return str(persistent)


def _midi_to_musicxml(midi_path: str, title: str, artist: str | None) -> str:
    from music21 import converter, metadata

    score = converter.parse(midi_path)
    score.metadata = metadata.Metadata()
    score.metadata.title = title
    if artist:
        score.metadata.composer = artist

    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as tmp:
        output_path = tmp.name

    score.write("musicxml", fp=output_path)
    return Path(output_path).read_text(encoding="utf-8")


def _build_editor_json_from_musicxml(
    musicxml: str,
    title: str,
    target: str,
    source: str,
) -> str:
    from music21 import converter

    score = converter.parse(musicxml)
    notes: list[dict[str, str]] = []
    for element in score.flat.notes:
        if hasattr(element, "pitch") and element.pitch is not None:
            notes.append(
                {
                    "pitch": element.pitch.nameWithOctave,
                    "duration": element.duration.type if element.duration else "quarter",
                }
            )
        elif element.isChord:
            for pitch in element.pitches:
                notes.append({"pitch": pitch.nameWithOctave, "duration": "quarter"})

    if not notes:
        return build_stub_editor_json(title, target, source=source)

    tab_lines = _notes_to_tab_lines(notes[:32])
    payload: dict[str, Any] = {
        "title": title,
        "target": target,
        "source": source,
        "measures": [{"number": 1, "notes": notes[:32]}],
        "tab": {"strings": [label for label, _ in GUITAR_STRINGS], "lines": tab_lines},
    }
    return json.dumps(payload, ensure_ascii=False)


def _notes_to_tab_lines(notes: list[dict[str, str]]) -> list[str]:
    from music21 import pitch as m21_pitch

    lines = {label: ["-"] * (len(notes) * 3 + 2) for label, _ in GUITAR_STRINGS}

    for index, note in enumerate(notes):
        column = index * 3 + 1
        try:
            midi = int(m21_pitch.Pitch(note["pitch"]).midi)
        except Exception:
            continue
        string_label, fret = _midi_to_guitar_position(midi)
        fret_text = str(fret) if fret >= 0 else "x"
        lines[string_label][column : column + len(fret_text)] = list(fret_text)

    rendered: list[str] = []
    for label, _ in GUITAR_STRINGS:
        rendered.append(f"{label}|{''.join(lines[label])}|")
    return rendered


def _midi_to_guitar_position(midi: int) -> tuple[str, int]:
    best: tuple[str, int] | None = None
    for label, open_midi in GUITAR_STRINGS:
        fret = midi - open_midi
        if 0 <= fret <= 15:
            if best is None or fret < best[1]:
                best = (label, fret)
    return best if best else ("e", 0)


def build_stub_musicxml(title: str, artist: str | None) -> str:
    subtitle = f" — {artist}" if artist else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<score-partwise version="3.1">\n'
        "  <work>\n"
        f"    <work-title>{_xml_escape(title)}{_xml_escape(subtitle)}</work-title>\n"
        "  </work>\n"
        "  <part-list>\n"
        '    <score-part id="P1"><part-name>Generated</part-name></score-part>\n'
        "  </part-list>\n"
        '  <part id="P1">\n'
        '    <measure number="1">\n'
        "      <attributes>\n"
        "        <divisions>1</divisions>\n"
        "        <time><beats>4</beats><beat-type>4</beat-type></time>\n"
        "        <clef><sign>G</sign><line>2</line></clef>\n"
        "      </attributes>\n"
        "      <note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>\n"
        "      <note><pitch><step>D</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>\n"
        "      <note><pitch><step>E</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>\n"
        "      <note><pitch><step>F</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>\n"
        "    </measure>\n"
        "  </part>\n"
        "</score-partwise>\n"
    )


def build_stub_editor_json(title: str, target: str, source: str = "stub") -> str:
    payload: dict[str, Any] = {
        "title": title,
        "target": target,
        "source": source,
        "measures": [
            {
                "number": 1,
                "notes": [
                    {"pitch": "C4", "duration": "quarter"},
                    {"pitch": "D4", "duration": "quarter"},
                    {"pitch": "E4", "duration": "quarter"},
                    {"pitch": "F4", "duration": "quarter"},
                ],
            }
        ],
        "tab": {
            "strings": ["e", "B", "G", "D", "A", "E"],
            "lines": [
                "e|--0--2--0-----|",
                "B|--------------|",
                "G|--------------|",
                "D|--------------|",
                "A|--------------|",
                "E|--------------|",
            ],
        },
    }
    return json.dumps(payload, ensure_ascii=False)


def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
