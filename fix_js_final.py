import os
import subprocess

js_content = """(function() {
    function toggleFieldsForSelect(selectEl) {
        var container = selectEl.closest('.inline-related');
        if (!container) {
            container = document;
        }

        var valQ = selectEl.value;
        
        var youtubeField = container.querySelector('.field-youtube_url');
        var videoField = container.querySelector('.field-video_file');
        var audioField = container.querySelector('.field-audio_file');
        var imageField = container.querySelector('.field-image');
        
        if (youtubeField) youtubeField.style.display = 'none';
        if (videoField) videoField.style.display = 'none';
        if (audioField) audioField.style.display = 'none';
        if (imageField) imageField.style.display = 'none';
        
        if (valQ === 'image') {
            if (imageField) imageField.style.display = '';
        } else if (valQ === 'video') {
            if (youtubeField) youtubeField.style.display = '';
            if (videoField) videoField.style.display = '';
        } else if (valQ === 'audio') {
            if (audioField) audioField.style.display = '';
        }
    }

    function initAll() {
        var qSelects = document.querySelectorAll('select[name$="question_type"]');
        qSelects.forEach(function(sel) {
            toggleFieldsForSelect(sel);
            // remove and re-add to avoid duplicates if initAll is called multiple times
            sel.removeEventListener('change', handleChange);
            sel.addEventListener('change', handleChange);
        });
    }

    function handleChange(e) {
        toggleFieldsForSelect(e.target);
    }

    function onReady() {
        initAll();
        if (typeof django !== 'undefined' && django.jQuery) {
            django.jQuery(document).on('formset:added', function(event, row, formsetName) {
                initAll();
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', onReady);
    } else {
        onReady();
    }
})();
"""

base_dir = os.path.dirname(os.path.abspath(__file__))

# Write to source static
source_path = os.path.join(base_dir, 'courses', 'static', 'courses', 'admin', 'question_admin_v3.js')
os.makedirs(os.path.dirname(source_path), exist_ok=True)
with open(source_path, 'w', encoding='utf-8') as f:
    f.write(js_content)
print(f"Written to: {source_path}")

# Write to staticfiles (collected static)
static_path = os.path.join(base_dir, 'staticfiles', 'courses', 'admin', 'question_admin_v3.js')
os.makedirs(os.path.dirname(static_path), exist_ok=True)
with open(static_path, 'w', encoding='utf-8') as f:
    f.write(js_content)
print(f"Written to: {static_path}")

# Fix admin.py to use v3
admin_py_path = os.path.join(base_dir, 'courses', 'admin.py')
with open(admin_py_path, 'r', encoding='utf-8') as f:
    admin_content = f.read()

# Replace any previous version with v3
admin_content = admin_content.replace('courses/admin/question_admin.js', 'courses/admin/question_admin_v3.js')
admin_content = admin_content.replace('courses/admin/question_admin_v2.js', 'courses/admin/question_admin_v3.js')

with open(admin_py_path, 'w', encoding='utf-8') as f:
    f.write(admin_content)
print("Updated admin.py to use question_admin_v3.js")

# Try to run collectstatic
try:
    print("Running collectstatic...")
    subprocess.run(["python", "manage.py", "collectstatic", "--noinput"], cwd=base_dir)
except Exception as e:
    print(f"collectstatic failed, but files are already overwritten. Error: {e}")

print("\nDONE! Please go to the Web tab in PythonAnywhere and click the 'Reload' button.")
