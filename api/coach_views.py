import os
import tempfile
import difflib

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def _get_label(score):
    """Return Arabic label based on score."""
    if score >= 90:
        return "ممتاز"
    elif score >= 75:
        return "جيد جداً"
    elif score >= 60:
        return "جيد"
    elif score >= 40:
        return "مقبول"
    else:
        return "يحتاج تحسين"


def _transcribe_audio(audio_path):
    """Transcribe audio file using Google free speech recognition."""
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="en-US")
        return text.lower().strip()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return None


def _convert_to_wav(input_path):
    """Convert audio file to WAV format for speech_recognition compatibility."""
    from pydub import AudioSegment

    wav_path = input_path.replace(os.path.splitext(input_path)[1], ".wav")
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(wav_path, format="wav")
        return wav_path
    except Exception:
        return None


def _get_ipa(word):
    """Get IPA transcription for an English word."""
    try:
        import eng_to_ipa as ipa
        result = ipa.convert(word)
        if result and result != word:
            return result
    except Exception:
        pass
    return word


def _compare_words(target_word, spoken_word):
    """Compare two words and return a similarity score (0-100)."""
    if not spoken_word:
        return 0
    if target_word.lower() == spoken_word.lower():
        return 100

    ratio = difflib.SequenceMatcher(None, target_word.lower(), spoken_word.lower()).ratio()
    return int(ratio * 100)


def _build_phoneme_analysis(target_word, spoken_word):
    """Build phoneme-level analysis comparing target and spoken words."""
    target_ipa = _get_ipa(target_word.lower())
    spoken_ipa = _get_ipa(spoken_word.lower()) if spoken_word else ""

    phonemes = []

    # Use SequenceMatcher to align the IPA characters
    matcher = difflib.SequenceMatcher(None, target_ipa, spoken_ipa)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        target_chunk = target_ipa[i1:i2]

        if tag == "equal":
            # Matched correctly
            for ch in target_chunk:
                if ch in "ˈˌ.":  # skip stress markers
                    continue
                phonemes.append({
                    "phoneme": f"/{ch}/",
                    "score": 100,
                    "label": _get_label(100),
                })
        elif tag == "replace":
            # Substitution – wrong sound
            spoken_chunk = spoken_ipa[j1:j2]
            for idx, ch in enumerate(target_chunk):
                if ch in "ˈˌ.":
                    continue
                wrong = spoken_chunk[idx] if idx < len(spoken_chunk) else "?"
                phonemes.append({
                    "phoneme": f"/{ch}/",
                    "score": 20,
                    "label": _get_label(20),
                    "spoken_as": f"/{wrong}/",
                })
        elif tag == "delete":
            # Missing sound – student skipped it
            for ch in target_chunk:
                if ch in "ˈˌ.":
                    continue
                phonemes.append({
                    "phoneme": f"/{ch}/",
                    "score": 0,
                    "label": "محذوف",
                })
        # "insert" means extra sounds the student added – we note them but
        # they don't map to target phonemes, so we skip for the table.

    # If we got no phonemes (e.g. IPA failed), fall back to letter comparison
    if not phonemes:
        matcher2 = difflib.SequenceMatcher(None, target_word.lower(), (spoken_word or "").lower())
        for tag, i1, i2, j1, j2 in matcher2.get_opcodes():
            chunk = target_word[i1:i2]
            if tag == "equal":
                for ch in chunk:
                    phonemes.append({"phoneme": f"/{ch}/", "score": 100, "label": _get_label(100)})
            elif tag == "replace":
                spoken_chunk = (spoken_word or "")[j1:j2]
                for idx, ch in enumerate(chunk):
                    wrong = spoken_chunk[idx] if idx < len(spoken_chunk) else "?"
                    phonemes.append({"phoneme": f"/{ch}/", "score": 20, "label": _get_label(20), "spoken_as": f"/{wrong}/"})
            elif tag == "delete":
                for ch in chunk:
                    phonemes.append({"phoneme": f"/{ch}/", "score": 0, "label": "محذوف"})

    return phonemes


class PronunciationAssessmentAPIView(APIView):
    """
    Real Pronunciation Assessment API.
    Uses Google free speech recognition to transcribe the student's audio,
    then compares the transcription against the target text phonetically.
    """

    def post(self, request):
        target_text = request.data.get("text", "").strip()
        audio_file = request.FILES.get("audio")

        if not target_text:
            return Response(
                {"success": False, "error": "Target text is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not audio_file:
            return Response(
                {"success": False, "error": "Audio file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── 1. Save uploaded audio to a temp file ──────────────────────
        suffix = os.path.splitext(audio_file.name)[1] or ".m4a"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp.close()

            # ── 2. Convert to WAV ──────────────────────────────────────
            wav_path = _convert_to_wav(tmp.name)
            if not wav_path:
                return Response(
                    {"success": False, "error": "فشل تحويل ملف الصوت. تأكد من تثبيت ffmpeg."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # ── 3. Transcribe ──────────────────────────────────────────
            spoken_text = _transcribe_audio(wav_path)

            # Clean up WAV
            if wav_path != tmp.name and os.path.exists(wav_path):
                os.unlink(wav_path)

            if spoken_text is None:
                return Response(
                    {"success": False, "error": "فشل الاتصال بخدمة التعرف على الصوت."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # ── 4. Compare word-by-word ────────────────────────────────
            target_words = target_text.lower().split()
            spoken_words = spoken_text.split() if spoken_text else []

            # Align spoken words to target words using SequenceMatcher
            word_matcher = difflib.SequenceMatcher(None, target_words, spoken_words)
            aligned_pairs = []

            for tag, i1, i2, j1, j2 in word_matcher.get_opcodes():
                if tag == "equal":
                    for k in range(i2 - i1):
                        aligned_pairs.append((target_words[i1 + k], spoken_words[j1 + k]))
                elif tag == "replace":
                    t_slice = target_words[i1:i2]
                    s_slice = spoken_words[j1:j2]
                    for k in range(max(len(t_slice), len(s_slice))):
                        tw = t_slice[k] if k < len(t_slice) else None
                        sw = s_slice[k] if k < len(s_slice) else None
                        if tw:
                            aligned_pairs.append((tw, sw or ""))
                elif tag == "delete":
                    for k in range(i1, i2):
                        aligned_pairs.append((target_words[k], ""))
                # "insert" = extra words student said, skip

            words_result = []
            total_score = 0

            for target_w, spoken_w in aligned_pairs:
                word_score = _compare_words(target_w, spoken_w)
                total_score += word_score
                phonemes = _build_phoneme_analysis(target_w, spoken_w)
                words_result.append({
                    "word": target_w,
                    "spoken_as": spoken_w if spoken_w != target_w.lower() else None,
                    "accuracy_score": word_score,
                    "phonemes": phonemes,
                })

            overall_score = int(total_score / len(aligned_pairs)) if aligned_pairs else 0

            # Completeness: how many target words were spoken
            matched_count = sum(1 for _, sw in aligned_pairs if sw)
            completeness = int((matched_count / len(target_words)) * 100) if target_words else 0

            result = {
                "success": True,
                "overall_score": overall_score,
                "completeness_score": completeness,
                "pronunciation_score": overall_score,
                "spoken_text": spoken_text or "(لم يتم التعرف على كلام)",
                "words": words_result,
            }

            return Response(result, status=status.HTTP_200_OK)

        finally:
            # Clean up temp file
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
