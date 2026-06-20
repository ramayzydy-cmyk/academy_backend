(function() {
    function toggleFieldsForQuestion(container) {
        var qTypeSelect = container.querySelector('select[name$="question_type"]');
        var aTypeSelect = container.querySelector('select[name$="answer_type"]');

        if (!qTypeSelect || !aTypeSelect) return;

        var valQ = qTypeSelect.value;
        var valA = aTypeSelect.value;
        
        // Media fields
        var youtubeField = container.querySelector('.field-youtube_url');
        var videoField = container.querySelector('.field-video_file');
        var audioField = container.querySelector('.field-audio_file');
        var imageField = container.querySelector('.field-image');
        
        // Answer fields
        var correctTextField = container.querySelector('.field-correct_text_answer');
        
        // Inline choices groups (only present on Question/LevelTestQuestion standalone admin pages)
        var choicesGroup = document.getElementById('choices-group') || document.getElementById('leveltestchoice_set-group') || document.getElementById('choice_set-group');

        // Hide all media first
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

        // Toggle answer fields
        if (valA === 'text') {
            if (correctTextField) correctTextField.style.display = '';
            if (choicesGroup) choicesGroup.style.display = 'none';
        } else {
            // choices or multi_choices
            if (correctTextField) correctTextField.style.display = 'none';
            if (choicesGroup) choicesGroup.style.display = '';
        }
    }

    function initAll() {
        // Handle inlines
        var inlineContainers = document.querySelectorAll('.inline-related');
        inlineContainers.forEach(function(container) {
            toggleFieldsForQuestion(container);
            
            var qTypeSelect = container.querySelector('select[name$="question_type"]');
            var aTypeSelect = container.querySelector('select[name$="answer_type"]');
            
            if (qTypeSelect) {
                qTypeSelect.removeEventListener('change', handleChange);
                qTypeSelect.addEventListener('change', handleChange);
            }
            if (aTypeSelect) {
                aTypeSelect.removeEventListener('change', handleChange);
                aTypeSelect.addEventListener('change', handleChange);
            }
        });

        // Handle standalone
        var mainQType = document.querySelector('#id_question_type');
        var mainAType = document.querySelector('#id_answer_type');
        if (mainQType && mainAType) {
            toggleFieldsForQuestion(document);
            mainQType.removeEventListener('change', handleMainChange);
            mainQType.addEventListener('change', handleMainChange);
            mainAType.removeEventListener('change', handleMainChange);
            mainAType.addEventListener('change', handleMainChange);
        }
    }

    function handleChange(e) {
        var container = e.target.closest('.inline-related');
        if (container) {
            toggleFieldsForQuestion(container);
        }
    }

    function handleMainChange(e) {
        toggleFieldsForQuestion(document);
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