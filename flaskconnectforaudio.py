from flask import Flask, request, jsonify
from flask_cors import CORS
from io import BytesIO
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from bs4 import BeautifulSoup # Text Cleaning
import re, string # Regular Expressions, String
from nltk.corpus import stopwords # stopwords
from nltk.stem.porter import PorterStemmer # for word stemming
from nltk.stem import WordNetLemmatizer # for word lemmatization
import unicodedata
import html
import nltk
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import json
import speech_recognition as sr
app = Flask(__name__)
CORS(app)
nltk.download('stopwords')
modelfordvdetectionforweb = tf.keras.models.load_model("D:\TextProj\dvdtect_model.h5")
stop = set(stopwords.words('english'))

# update stopwords to have punctuation too
stop.update(list(string.punctuation))
def clean_text(text):

    # Remove unwanted html characters
    re1 = re.compile(r'  +')
    x1 = text.lower().replace('#39;', "'").replace('amp;', '&').replace('#146;', "'").replace(
    'nbsp;', ' ').replace('#36;', '$').replace('\\n', "\n").replace('quot;', "'").replace(
    '<br />', "\n").replace('\\"', '"').replace('<unk>', 'u_n').replace(' @.@ ', '.').replace(
    ' @-@ ', '-').replace('\\', ' \\ ')
    text = re1.sub(' ', html.unescape(x1))

    # remove non-ascii characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')

#     # strip html
#     soup = BeautifulSoup(text, 'html.parser')
#     text = soup.get_text()

    # remove between square brackets
    text = re.sub('\[[^]]*\]', '', text)

    # remove URLs
    text = re.sub(r'http\S+', '', text)

    # remove twitter tags
    text = text.replace("@", "")

    # remove hashtags
    text = text.replace("#", "")

    # remove all non-alphabetic characters
    text = re.sub(r'[^a-zA-Z ]', '', text)

    # remove stopwords from text
    final_text = []
    for word in text.split():
        if word.strip().lower() not in stop:
            final_text.append(word.strip().lower())

    text = " ".join(final_text)

    # lemmatize words
    lemmatizer = WordNetLemmatizer()
    text = " ".join([lemmatizer.lemmatize(word) for word in text.split()])
    text = " ".join([lemmatizer.lemmatize(word, pos = 'v') for word in text.split()])

    # replace all numbers with "num"
    text = re.sub("\d", "num", text)

    return text.lower()
@app.route('/audiointerpage', methods=['POST'])
def predict():
    input_audio = request.files['audio'] 
    recog = sr.Recognizer()
    with sr.AudioFile(input_audio) as source:
       interhld = recog.record(source)
    transcribed_text = recog.recognize_google(interhld)
    print("Transcribed Text:")
    print(transcribed_text)
    vocab_size = 10000
    test_median_data = int(18.0)
    cleaned_sentence = clean_text(transcribed_text)
    tokenizer = Tokenizer(num_words = vocab_size, oov_token = 'UNK')
    tokenizer.fit_on_texts(cleaned_sentence)
    X_input = tokenizer.texts_to_sequences([cleaned_sentence])
    X_input = pad_sequences(X_input, maxlen=test_median_data, truncating='post', padding='post')
    # Make the prediction
    prediction = modelfordvdetectionforweb.predict(X_input)
    # Display the prediction for each label
    summationofvalus = prediction[0][0]+prediction[0][1]+prediction[0][2]+prediction[0][2]+prediction[0][3]+prediction[0][4]
    if summationofvalus <1.0:
        answer = "No Domestic Violence detected"
        pred = {"predicted":answer}
        return jsonify(pred)
    else:
        prediction_float = prediction[0].tolist()
        predicnjn = {
        'severe_toxicity': prediction_float[0],
        'obscene': prediction_float[1],
        'threat': prediction_float[2],
        'insult': prediction_float[3],
        'identity_attack': prediction_float[4]
        }
        ans = {"predicted":predicnjn,"transcribed":transcribed_text}
        response_json = json.dumps(ans)
        return response_json 

if __name__ == '__main__':
    app.run(debug=True)