# updated code of py
import json
import os
import time
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from .models import URL

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from weasyprint import HTML

# Global flag
is_file_ready = False
latest_pdf_name = None

# Configure headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def home(request):
    return HttpResponse("Welcome to the PDF Generator API!")

@csrf_exempt
def generate_pdf(request):
    global is_file_ready, latest_pdf_name

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            if not url:
                return JsonResponse({"error": "URL is required."}, status=400)

            new_url = URL(url=url)
            new_url.save()

            is_file_ready = False
            latest_pdf_name = f"{new_url.id}.pdf"

            # Set up Selenium
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url)
            time.sleep(5)  # Wait for dynamic content

            # Extract elements
            questions_elements = driver.find_elements(By.CSS_SELECTOR, ".markdown.prose.w-full.break-words")
            answers_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="markdown"][class*="prose"][class*="break-words"]')

            questions = [el.text.strip() for el in questions_elements]
            answers = [el.get_attribute('innerHTML') for el in answers_elements]

            driver.quit()

            # Format as HTML
            html_content = f"""
            <html>
            <head>
                <title>Scraped Data</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 30px; line-height: 1.6; }}
                    h2 {{ color: #343a40; margin-top: 20px; }}
                    p {{ background: #fff; padding: 10px; border-radius: 5px; }}
                    div {{ margin-bottom: 20px; }}
                    pre, code {{ background: #f1f1f1; padding: 5px; border-radius: 3px; }}
                    button {{ display: none; }}
                </style>
            </head>
            <body>
                {''.join(f"""
                    <h2>Question {i+1}:</h2>
                    <p>{escape(q)}</p>
                    <h2>Answer {i+1}:</h2>
                    <div>{answers[i] if i < len(answers) else 'No answer found'}</div>
                """ for i, q in enumerate(questions))}
                <hr><h6>Source URL: {escape(url)}</h6>
            </body>
            </html>
            """

            # Convert to PDF
            HTML(string=html_content).write_pdf(target=latest_pdf_name)
            is_file_ready = True

            return JsonResponse({"message": "PDF generated", "pdf_id": new_url.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)

def check_status(request):
    return JsonResponse({"isFileReady": is_file_ready})

def download_pdf(request):
    global latest_pdf_name

    if not latest_pdf_name:
        return JsonResponse({"message": "No PDF request found"}, status=404)

    if os.path.exists(latest_pdf_name):
        try:
            # Read the file content into memory
            with open(latest_pdf_name, 'rb') as f:
                file_data = f.read()

            # Create response before deleting the file
            response = HttpResponse(file_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(latest_pdf_name)}"'

            # Now delete the file safely
            os.remove(latest_pdf_name)
            print(f"[INFO] Deleted file: {latest_pdf_name}")

            return response
        except Exception as e:
            print(f"[ERROR] Could not delete file: {e}")
            return JsonResponse({"message": "Failed to serve PDF"}, status=500)

    return JsonResponse({"message": "PDF not ready yet"}, status=404)