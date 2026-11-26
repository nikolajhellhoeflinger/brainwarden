#!/usr/bin/env python3
"""Voice memos into the inbox, as text — transcribed on this computer.

    python3 .tools/transcribe.py              # every voice memo in 00-inbox/ becomes a capture
    python3 .tools/transcribe.py --check      # which speech engine would be used — nothing else
    python3 .tools/transcribe.py --language de
    python3 .tools/transcribe.py --auto on    # let the weekly runner's 20-minute tick do it

(Windows: `py -3`.) The idea you have while walking is the one that gets
lost: nobody types a note into a phone at a traffic light. Speaking is fast,
but an audio file is a dead end for a brain — no search finds it, no review
files it, no agent can read it. So a memo has to become text before the
brain can use it, and it should not have to leave the computer for that.

How it gets here: anything that puts a file into `00-inbox/` works — the
Obsidian app on the phone with the vault synced (Obsidian Sync, iCloud on
iPhone, Syncthing on Android), "Save to Files" from the phone's recorder, a
shared folder. Audio formats: m4a, mp3, wav, ogg/opus, webm, aac, flac, amr,
caf. What this does with it: transcribes it LOCALLY with the first engine it
finds, writes `00-inbox/YYYY-MM-DD-voice-<first words>.md` (an ordinary
capture — the weekly review files it like any other), and moves the audio
next to the archive (`90-…/voice/`), embedded in the note so it can still be
played. Nothing is uploaded, no account, no model call.

Needs ffmpeg (ffmpeg.org; macOS: `brew install ffmpeg`), which every engine
below uses anyway: each recording is converted to a plain WAV first, with its
format named explicitly, and only that WAV reaches an engine.

Engines, in this order (install one; none comes with the kit):
  1. a command of your own: `.tools/transcribe.json` →
     {"command": ["my-stt", "{audio}"]} — whatever it prints is the text
  2. mlx-whisper (Apple Silicon):   pipx install mlx-whisper
  3. whisper.cpp (`whisper-cli`) with a model file named in
     .tools/transcribe.json {"model": "/path/ggml-base.bin"} or WHISPER_CPP_MODEL
  4. faster-whisper (Python):        pip install faster-whisper
  5. openai-whisper (`whisper`):     pip install openai-whisper
The first run of 2, 4 and 5 downloads a speech model (hundreds of MB to
~1.6 GB) — run it once by hand, so that download does not happen silently
in a background job. Then `--auto on` lets the runner's tick pick memos up
within 20 minutes (needs `autoreview.py install`).

Known limit: speech models invent text on silence (a "thank you for
watching" on an empty recording). The note keeps the audio embedded, so the
review can listen before it trusts a strange sentence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
TOOLS = VAULT / ".tools"
CONFIG = TOOLS / "transcribe.json"
RUNNER_CONFIG = TOOLS / "autoreview.json"
AUDIO = {".m4a", ".mp3", ".wav", ".ogg", ".oga", ".opus", ".webm", ".aac", ".flac", ".amr", ".caf", ".aiff"}
MLX_MODEL = "mlx-community/whisper-large-v3-turbo"
SMALL_MODEL = "small"
TIMEOUT = 3600            # one memo; an hour-long recording on a slow CPU still fits


def utf8_stdout():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def load_config():
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def numbered(prefix):
    """The vault's folder with this number, whatever its name in the vault's
    language (`00-inbox`, `90-archiv`, `90-archivo` …)."""
    try:
        for name in sorted(os.listdir(VAULT)):
            if name.startswith(prefix) and (VAULT / name).is_dir():
                return VAULT / name
    except OSError:
        pass
    return None


# ------------------------------------------------------------------ engines
def engine(cfg):
    """(name, function audio_path, language -> text) or None."""
    custom = os.environ.get("BRAINWARDEN_TRANSCRIBER") or cfg.get("command")
    if custom:
        if isinstance(custom, str) and custom.lstrip().startswith("["):
            custom = json.loads(custom)          # a list survives Windows paths; shlex eats backslashes
        argv = shlex.split(custom) if isinstance(custom, str) else [str(a) for a in custom]
        return "your command", lambda audio, lang: run_text([a.replace("{audio}", str(audio)) for a in argv])
    if platform.system() == "Darwin" and platform.machine() == "arm64" and shutil.which("mlx_whisper"):
        return "mlx-whisper", mlx_whisper
    model = cfg.get("model") or os.environ.get("WHISPER_CPP_MODEL")
    if shutil.which("whisper-cli") and model and os.path.isfile(os.path.expanduser(model)):
        return "whisper.cpp", lambda audio, lang: whisper_cpp(audio, lang, os.path.expanduser(model))
    if python_has("faster_whisper"):
        return "faster-whisper", faster_whisper
    if shutil.which("whisper"):
        return "openai-whisper", openai_whisper
    return None


def python_has(module):
    try:
        import importlib.util
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def run_text(argv):
    """Every engine runs in an empty folder of its own. `python -c` puts the
    current folder first on the import path, and the vault is a folder the
    unattended review writes into: a planted `faster_whisper.py` there would
    run with the next tick's rights."""
    with tempfile.TemporaryDirectory() as neutral:
        # UTF-8 out of every Python engine: on Windows a child prints in the old
        # code page, and "für" arrived as "f\ufffdr" (seen in CI)
        r = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=TIMEOUT, cwd=neutral, stdin=subprocess.DEVNULL,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1"))
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout).strip()[-300:] or f"exit {r.returncode}")
    return r.stdout


def via_txt(argv, out_dir, stem):
    """Engines that write `<stem>.txt` instead of printing."""
    run_text(argv)
    return (Path(out_dir) / f"{stem}.txt").read_text(encoding="utf-8", errors="replace")


def mlx_whisper(audio, lang):
    with tempfile.TemporaryDirectory() as tmp:
        argv = ["mlx_whisper", str(audio), "--model", MLX_MODEL, "-f", "txt", "-o", tmp,
                "--output-name", "memo", "--verbose", "False"]
        return via_txt(argv + (["--language", lang] if lang else []), tmp, "memo")


def whisper_cpp(audio, lang, model):
    with tempfile.TemporaryDirectory() as tmp:
        argv = ["whisper-cli", "-m", model, "-f", str(audio), "-otxt", "-of", str(Path(tmp) / "out"), "-np"]
        return via_txt(argv + (["-l", lang] if lang else []), tmp, "out")


def faster_whisper(audio, lang):
    code = ("import sys\nfrom faster_whisper import WhisperModel\n"
            f"m = WhisperModel({SMALL_MODEL!r}, device='auto', compute_type='int8')\n"
            "segs, _ = m.transcribe(sys.argv[1], language=sys.argv[2] or None, vad_filter=True)\n"
            "print(' '.join(s.text.strip() for s in segs))\n")
    return run_text([sys.executable, "-c", code, str(audio), lang or ""])


def openai_whisper(audio, lang):
    with tempfile.TemporaryDirectory() as tmp:
        argv = ["whisper", str(audio), "--model", SMALL_MODEL, "--output_format", "txt", "--output_dir", tmp]
        return via_txt(argv + (["--language", lang] if lang else []), tmp, audio.stem)


# --------------------------------------------------------------- the memos
def memos():
    inbox = numbered("00-")
    if not inbox:
        return []
    found = []
    for dirpath, dirnames, filenames in os.walk(inbox):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for f in sorted(filenames):
            p = Path(dirpath) / f
            if p.suffix.lower() in AUDIO and not f.startswith(".") and p.is_file() and not p.is_symlink():
                found.append(p)
    return found


UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


def container(path):
    """The recording's container, read from its first bytes — None when it is
    not one. The name proves nothing: a TEXT file called memo.m4a holding a
    playlist (#EXTM3U …) or an ffconcat list makes a decoder that guesses the
    format fetch the URLs or read the files it lists, and anything that can
    write a text file into the inbox could send vault text to a URL that way.
    So the format is decided HERE and handed to ffmpeg explicitly (`-f`):
    ffmpeg never guesses, and a playlist demuxer is never chosen."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(16)
    except OSError:
        return None
    if head[4:8] == b"ftyp":
        return "mov"                                     # m4a, mp4, 3gp (iPhone, Android)
    sig = {b"OggS": "ogg", b"fLaC": "flac", b"caff": "caf", b"\x1aE\xdf\xa3": "matroska"}
    if head[:4] in sig:
        return sig[head[:4]]
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "wav"
    if head[:4] == b"FORM" and head[8:12] in (b"AIFF", b"AIFC"):
        return "aiff"
    if head[:5] == b"#!AMR":
        return "amr"
    if head[:3] == b"ID3":
        return "mp3"
    if len(head) > 1 and head[0] == 0xFF and head[1] & 0xE0 == 0xE0:
        return "aac" if head[1] & 0x06 == 0 else "mp3"   # ADTS has layer 0, MPEG audio does not
    return None


def ffmpeg_cmd():
    """ffmpeg (BRAINWARDEN_FFMPEG only for the kit's self-check)."""
    custom = os.environ.get("BRAINWARDEN_FFMPEG")
    if custom:
        return json.loads(custom)
    found = shutil.which("ffmpeg")
    return [found] if found else None


def to_wav(audio, tmp):
    """Copy, check, convert — in a folder nobody else writes to, so the bytes
    that were checked are the bytes that get decoded. Every engine then reads
    a plain 16 kHz WAV this function wrote, never the inbox file itself."""
    copy = Path(tmp) / ("in" + audio.suffix.lower())
    shutil.copyfile(audio, copy)
    fmt = container(copy)
    if not fmt:
        raise ValueError("not an audio recording by its content")
    ffmpeg = ffmpeg_cmd()
    if not ffmpeg:
        raise RuntimeError("ffmpeg is needed to read recordings safely — install it (ffmpeg.org)")
    wav = Path(tmp) / "memo.wav"
    run_text(ffmpeg + ["-nostdin", "-loglevel", "error", "-protocol_whitelist", "file", "-f", fmt,
                       "-i", str(copy), "-vn", "-ar", "16000", "-ac", "1", "-y", str(wav)])
    if not wav.is_file():
        raise RuntimeError("ffmpeg wrote no audio")
    return wav


def slug(text, words=6):
    # ä → ae as in search.py: "fur" for "für" is a different word to anyone reading the name
    plain = unicodedata.normalize("NFKD", unicodedata.normalize("NFC", text.lower()).translate(UMLAUT))
    plain = "".join(c for c in plain if not unicodedata.combining(c))
    parts = re.findall(r"[a-z0-9]+", plain)[:words]
    return "-".join(parts) or "memo"


def tidy(text):
    """Engines print one line per segment; a note wants paragraphs."""
    lines = [l.strip() for l in text.replace("\r", "").split("\n")]
    text = re.sub(r"[ \t]+", " ", " ".join(l for l in lines if l)).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    paras, cur = [], []
    for s in sentences:
        cur.append(s)
        if len(" ".join(cur)) > 400:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return "\n\n".join(p for p in paras if p)


def headline(text, limit=80):
    first = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0].strip()
    if len(first) <= limit:
        return first
    return first[:limit].rsplit(" ", 1)[0].rstrip(",;:") + " …"


def free(path):
    n, base = 2, path
    while path.exists():
        path = base.with_name(f"{base.stem}-{n}{base.suffix}")
        n += 1
    return path


def transcribe_one(audio, name, fn, lang, archive):
    when = dt.datetime.fromtimestamp(audio.stat().st_mtime)
    with tempfile.TemporaryDirectory() as tmp:
        text = tidy(fn(to_wav(audio, tmp), lang))
    kept = free(archive / audio.name)
    kept.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(audio), str(kept))           # first the audio, so a crash cannot transcribe it twice
    try:
        title = headline(text) if text else "Voice memo (no speech recognised)"
        # into the inbox itself, wherever the sync put the recording: the review reads the inbox
        note = free(numbered("00-") / f"{when:%Y-%m-%d}-voice-{slug(text) if text else 'empty'}.md")
        body = text or "(No speech recognised — listen to the recording before deleting it.)"
        note.write_text(f"# {title}\n\n{body}\n\n![[{kept.name}]]\n\n"
                        f"_Captured: {when:%Y-%m-%d %H:%M} · Context: voice memo `{audio.name}`, "
                        f"transcribed on this computer ({name}) — check names and numbers against the recording_\n",
                        encoding="utf-8")
    except Exception:
        shutil.move(str(kept), str(audio))       # no note, no move: the next run tries again
        raise
    return note


def set_auto(on):
    try:
        cfg = json.loads(RUNNER_CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cfg = {}
    cfg["transcribe"] = bool(on)
    RUNNER_CONFIG.write_text(json.dumps(cfg, indent=1) + "\n", encoding="utf-8")
    print(f"automatic transcription {'on' if on else 'off'} — the runner's 20-minute tick "
          + ("now turns new voice memos into captures (`autoreview.py install` must have run)." if on else
             "leaves voice memos alone."))
    return 0


def main(argv=None):
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="say which engine would run, transcribe nothing")
    ap.add_argument("--language", help="e.g. de, en — default: the engine detects it")
    ap.add_argument("--auto", choices=["on", "off"], help="let the runner's tick transcribe")
    ap.add_argument("--quiet", action="store_true", help="print only when something happened (for the tick)")
    a = ap.parse_args(argv)
    cfg = load_config()
    found = engine(cfg)
    # every engine reads a WAV that ffmpeg wrote (to_wav), so ffmpeg is part of "ready"
    missing = ("no speech engine is installed (see `transcribe.py --help`)" if not found else
               "ffmpeg is not installed (ffmpeg.org — every recording is converted by it first)"
               if not ffmpeg_cmd() else "")
    if a.check:
        print(f"engine: {found[0]}" if found else "engine: none")
        if missing:
            print(f"not ready: {missing}")
        return 1 if missing else 0
    if a.auto:
        if a.auto == "on" and missing:
            # a background tick would fail on every memo, every 20 minutes
            print(f"not switched on: {missing}")
            return 1
        return set_auto(a.auto == "on")
    pending = memos()
    if not pending:
        if not a.quiet:
            print("no voice memos in the inbox")
        return 0
    if missing:
        if not a.quiet:              # the tick would repeat this every 20 minutes
            print(f"{len(pending)} voice memo(s) waiting, but {missing}. They stay where they are.")
        return 0
    name, fn = found
    archive = (numbered("90-") or (numbered("00-") / ".transcribed")) / "voice"
    lang = a.language or cfg.get("language")
    failed = 0
    for audio in pending:
        if not container(audio):
            if not a.quiet:
                print(f"{audio.name}: not an audio recording by its content — left alone, not decoded")
            continue
        try:
            note = transcribe_one(audio, name, fn, lang, archive)
            print(f"{audio.name} → {note.relative_to(VAULT).as_posix()}")
        except Exception as e:      # noqa: BLE001 — one bad file must not stop the rest
            failed += 1
            print(f"{audio.name}: not transcribed ({e.__class__.__name__}: {str(e)[:200]}) — it stays in the inbox")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
