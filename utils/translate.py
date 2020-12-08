from google_trans_new import google_translator

translator = google_translator()
translate_text = translator.translate('視訊小姐', lang_tgt='zh-cn')
print(translate_text)
