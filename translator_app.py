import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import tempfile
import base64

# Set page configuration
st.set_page_config(
    page_title="Multilingual Translator",
    page_icon="🌐",
    layout="wide"
)

# Set default API key
DEFAULT_API_KEY = "AIzaSyDf1x1_XibDDV-qvRq_1fTe5Ft_qm5UdVs"
os.environ['GEMINI_API_KEY'] = DEFAULT_API_KEY

# Function to get audio playback HTML
def get_audio_player(audio_bytes):
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    audio_html = f'''
        <audio controls autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    '''
    return audio_html

# Function to translate text using Gemini API
def translate_text(text, target_languages):
    try:
        # Configure the Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Create a model instance
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare the prompt for translation
        prompt = f"""
        Translate the following English text into these languages: {', '.join(target_languages)}
        
        Text: {text}
        
        Format the response as:
        Language: Translation
        """
        
        # Generate the translation
        response = model.generate_content(prompt)
        
        # Parse the response
        translations = {}
        current_language = None
        
        for line in response.text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    current_language = parts[0].strip()
                    translation = parts[1].strip()
                    translations[current_language] = translation
        
        return translations
    
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return {}

# Available languages
LANGUAGES = [
    "Spanish", "French", "German", "Italian", "Portuguese", 
    "Russian", "Japanese", "Chinese", "Korean", "Arabic",
    "Hindi", "Dutch", "Swedish", "Greek", "Turkish",
    "Urdu", "Bengali", "Thai", "Vietnamese", "Polish",
    "Ukrainian", "Farsi", "Hebrew", "Malay", "Indonesian",
    "Gemini"
]

# Main app
def main():
    st.title("🌐 Multilingual Translator with Voice")
    st.write("Translate English text to multiple languages with voice output")
    
    # Remove the API key input section completely
    
    # Text input
    input_text = st.text_area("Enter English text to translate", height=150)
    
    # Language selection
    st.subheader("Select target languages")
    selected_languages = []
    
    # Create columns for language selection
    cols = st.columns(5)
    for i, lang in enumerate(LANGUAGES):
        col_idx = i % 5
        with cols[col_idx]:
            if st.checkbox(lang, value=True if i < 5 else False):
                selected_languages.append(lang)
    
    # Translate button
    if st.button("Translate", type="primary") and input_text and selected_languages:
        with st.spinner("Translating..."):
            translations = translate_text(input_text, selected_languages)
            
            if translations:
                st.success("Translation completed!")
                
                # Display translations with audio
                for lang, translated_text in translations.items():
                    with st.expander(f"{lang}", expanded=True):
                        st.write(translated_text)
                        
                        # Generate speech
                        with st.spinner(f"Generating {lang} audio..."):
                            try:
                                # Map language names to language codes for gTTS
                                lang_code_map = {
                                    "Spanish": "es", "French": "fr", "German": "de", 
                                    "Italian": "it", "Portuguese": "pt", "Russian": "ru",
                                    "Japanese": "ja", "Chinese": "zh-CN", "Korean": "ko",
                                    "Arabic": "ar", "Hindi": "hi", "Dutch": "nl",
                                    "Swedish": "sv", "Greek": "el", "Turkish": "tr",
                                    "Urdu": "ur", "Bengali": "bn", "Thai": "th", 
                                    "Vietnamese": "vi", "Polish": "pl", "Ukrainian": "uk",
                                    "Farsi": "fa", "Hebrew": "he", "Malay": "ms",
                                    "Indonesian": "id", "Gemini": "en"  # Using English TTS for Gemini
                                }
                                
                                lang_code = lang_code_map.get(lang)
                                if lang_code:
                                    tts = gTTS(text=translated_text, lang=lang_code, slow=False)
                                    
                                    # Save to a temporary file
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                                        tts.save(fp.name)
                                        with open(fp.name, 'rb') as audio_file:
                                            audio_bytes = audio_file.read()
                                        os.unlink(fp.name)
                                    
                                    # Display audio player
                                    st.markdown(get_audio_player(audio_bytes), unsafe_allow_html=True)
                                else:
                                    st.warning(f"Text-to-speech not available for {lang}")
                            except Exception as e:
                                st.error(f"Error generating audio: {str(e)}")

if __name__ == "__main__":
    main()