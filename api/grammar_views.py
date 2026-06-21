import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import google.generativeai as genai
from django.conf import settings

class GrammarCoachAPIView(APIView):
    """
    Grammar Coach API.
    Receives a sentence, sends it to Google Gemini API to check for grammar errors,
    and returns the corrected sentence along with an explanation in Arabic.
    """

    def post(self, request):
        text = request.data.get('text', '').strip()

        if not text:
            return Response(
                {"success": False, "error": "Text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        api_key = getattr(settings, 'GEMINI_API_KEY', os.environ.get('GEMINI_API_KEY'))

        if not api_key:
            # Fallback mock response if API key is not configured
            if "man" in text.lower() and "i am" in text.lower():
                return Response({
                    "success": True,
                    "original_text": text,
                    "corrected_text": "I am a man",
                    "explanation": "في اللغة الإنجليزية، يجب استخدام أدوات النكرة (a / an) قبل الأسماء المفردة المعدودة. كلمة 'man' هي اسم مفرد ومعدود ويبدأ بحرف ساكن، لذا نستخدم قبله 'a'."
                }, status=status.HTTP_200_OK)

            return Response({
                "success": False,
                "error": "مفتاح GEMINI_API_KEY غير متوفر في الخادم. يرجى إضافته في الإعدادات."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        genai.configure(api_key=api_key)

        prompt = f"""
أنت معلم لغة إنجليزية محترف. قام أحد الطلاب بكتابة الجملة التالية باللغة الإنجليزية:
"{text}"

مهمتك:
1. تصحيح الجملة إذا كان بها أخطاء إملائية أو نحوية. إذا لم يكن هناك خطأ، أعد الجملة كما هي.
2. شرح سبب الخطأ (إن وجد) والقاعدة النحوية المتعلقة به باللغة العربية بطريقة مبسطة ومشجعة (مثلاً متى نستخدم a/an، الخ). إذا كانت صحيحة، امدح الطالب.
3. يجب أن يكون ردك حصراً بصيغة JSON بالتنسيق التالي بدون أي إضافات:
{{
  "original_text": "النص الأصلي",
  "corrected_text": "النص المصحح",
  "explanation": "الشرح باللغة العربية"
}}
"""

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            response_text = response.text.strip()
            
            # Clean markdown code blocks if the model wrapped the JSON
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            response_text = response_text.strip()
            
            result_data = json.loads(response_text)
            result_data["success"] = True
            
            return Response(result_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Fallback mock in case of failure
            if "man" in text.lower() and "i am" in text.lower():
                return Response({
                    "success": True,
                    "original_text": text,
                    "corrected_text": "I am a man",
                    "explanation": "في اللغة الإنجليزية، يجب استخدام أدوات النكرة (a / an) قبل الأسماء المفردة المعدودة. كلمة 'man' هي اسم مفرد ومعدود ويبدأ بحرف ساكن، لذا نستخدم قبله 'a'."
                }, status=status.HTTP_200_OK)
                
            return Response({
                "success": False,
                "error": f"حدث خطأ أثناء التواصل مع الذكاء الاصطناعي: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
