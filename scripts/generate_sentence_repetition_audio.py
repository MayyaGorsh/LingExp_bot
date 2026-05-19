"""генерация wav-стимулов для шаблона sentence repetition.

три условия предъявления прайма + два филлера, все на английском,
один голос:
  type1  - прайм отдельным предложением перед таргетом.
  type2  - прайм во второй клаузе того же предложения, что и таргет.
  type3a - прайм первой клаузой, таргет второй.
  type3b - таргет первой клаузой, прайм второй.

запуск: python -m scripts.generate_sentence_repetition_audio
"""

import asyncio
import io
import shutil
import sys
import tempfile
from pathlib import Path

import edge_tts
from pydub import AudioSegment

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


VOICE = "en-US-AriaNeural"
RATE = "-5%"
PAUSE_MS = 700  # пауза между двумя отдельными предложениями в type1

OUT_DIR = Path(__file__).resolve().parent.parent / "templates" / "examples" / "media"

# и прайм, и таргет используют PP-dative конструкцию ("V NP to NP") -
# именно её прайм должен закрепить.
PRIME = "The teacher handed a book to the student."
TARGET = "The waiter brought a menu to the guest."

TRIALS: list[tuple[str, list[str]]] = [
    # type1: два отдельных предложения, прайм первым.
    ("type1_separate_01.wav", [PRIME, TARGET]),

    # type2: одно предложение, таргет первой клаузой, прайм второй.
    (
        "type2_prime_second_clause_02.wav",
        [f"{TARGET[:-1]}, and {PRIME[0].lower()}{PRIME[1:]}"],
    ),

    # type3a: одно предложение, прайм первой клаузой, таргет второй.
    (
        "type3a_prime_first_03.wav",
        [f"{PRIME[:-1]}, and {TARGET[0].lower()}{TARGET[1:]}"],
    ),

    # type3b: одно предложение, таргет первой клаузой, прайм второй.
    # внешне совпадает с type2, разница только в экспериментальной роли:
    # type3 варьирует порядок как переменную, type2 фиксирует
    # «прайм после таргета».
    (
        "type3b_target_first_04.wav",
        [f"{TARGET[:-1]}, and {PRIME[0].lower()}{PRIME[1:]}"],
    ),

    ("filler_01.wav", ["The garden is full of beautiful red roses."]),
    ("filler_02.wav", ["A hot cup of tea is sitting on the wooden table."]),
]


async def synth_to_mp3(text: str, mp3_path: Path) -> None:
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(str(mp3_path))


async def build_trial(filename: str, sentences: list[str], tmp_dir: Path) -> Path:
    parts: list[AudioSegment] = []
    silence = AudioSegment.silent(duration=PAUSE_MS)

    for idx, sentence in enumerate(sentences):
        mp3_path = tmp_dir / f"{filename}_{idx}.mp3"
        await synth_to_mp3(sentence, mp3_path)
        seg = AudioSegment.from_file(mp3_path, format="mp3")
        if idx > 0:
            parts.append(silence)
        parts.append(seg)

    combined = sum(parts[1:], parts[0])
    out_path = OUT_DIR / filename
    combined = combined.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    combined.export(out_path, format="wav")
    return out_path


async def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for filename, sentences in TRIALS:
            out_path = await build_trial(filename, sentences, tmp_dir)
            print(f"  [ok] {out_path.relative_to(OUT_DIR.parent.parent)}")


if __name__ == "__main__":
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg не найден в PATH - pydub не сможет конвертировать mp3 в wav")
    asyncio.run(main())
