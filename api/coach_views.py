from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class PronunciationAssessmentAPIView(APIView):
    """
    Mock API for Pronunciation Assessment.
    In a real-world scenario, this would send the audio and text to Microsoft Azure Speech Services
    and parse the JSON response for phoneme-level accuracy scores.
    """

    def post(self, request):
        target_text = request.data.get('text', '')
        audio_file = request.FILES.get('audio')

        if not target_text:
            return Response({"success": False, "error": "Target text is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Basic validation
        if not audio_file:
            return Response({"success": False, "error": "Audio file is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Simulate a 1-second delay for API processing
        import time
        time.sleep(1)

        # Mock Data based on the provided screenshot "Academy" example
        # The word is broken down into its IPA phonemes: /ə/, /k/, /æ/, /d/, /ə/, /m/, /i/
        # All scored as "ممتاز" (Excellent)

        mock_data = {
            "success": True,
            "overall_score": 96,
            "fluency_score": 98,
            "completeness_score": 100,
            "pronunciation_score": 96,
            "words": [
                {
                    "word": target_text,
                    "accuracy_score": 96,
                    "phonemes": [
                        {"phoneme": "/ə/", "score": 95, "label": "ممتاز"},
                        {"phoneme": "/k/", "score": 98, "label": "ممتاز"},
                        {"phoneme": "/æ/", "score": 92, "label": "ممتاز"},
                        {"phoneme": "/d/", "score": 96, "label": "ممتاز"},
                        {"phoneme": "/ə/", "score": 97, "label": "ممتاز"},
                        {"phoneme": "/m/", "score": 99, "label": "ممتاز"},
                        {"phoneme": "/i/", "score": 94, "label": "ممتاز"},
                    ]
                }
            ]
        }

        # If they sent a different word, generate a generic mock response
        if target_text.lower() != "academy":
            mock_data["words"] = []
            for word in target_text.split():
                # Just mock some dummy phonemes for any other word
                word_phonemes = []
                for char in word:
                    word_phonemes.append({"phoneme": f"/{char.lower()}/", "score": 90, "label": "جيد جداً"})
                
                mock_data["words"].append({
                    "word": word,
                    "accuracy_score": 90,
                    "phonemes": word_phonemes
                })
            mock_data["overall_score"] = 90

        return Response(mock_data, status=status.HTTP_200_OK)
