from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import openai
from transformers import pipeline

app = Flask(__name__)
CORS(app)

# OpenAI API key
openai.api_key = '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'

# Initialize conversation with a system message
conversation_history = [
    {"role": "system", "content": "You are an expert in writing thesis, help user with thesis enhancement\
     , correct their grammar, or give them a good paragraph or thesis based on their wish."}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_data', methods=['POST'])
def process_data():
    try:
        data_from_frontend = request.get_json()
        user_type = data_from_frontend.get('type', '')
        user_message = data_from_frontend.get('user_message', '')

        print(f"Received frontend - Type: {user_type}, Message: {user_message}")

        if int(user_type) == 1:
            return AI_chatting(user_message)
        elif int(user_type) == 2:
            return correcting_grammar(user_message)
        elif int(user_type) == 3:
            return writing_leftly(user_message)
    
    except Exception as e:
        print(f"Error: {e}")
        result = {'result': 'Error processing data'}
        return jsonify(result)
    
def AI_chatting(user_message):
    conversation_history.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )

    ai_reply = response["choices"][0]["message"]["content"]

    conversation_history.append({"role": "assistant", "content": ai_reply})

    result = {'result': ai_reply}
    return jsonify(result)

def correcting_grammar(user_message):
    checkpoint = "team-writing-assistant/t5-base-c4jfleg"
    model = pipeline("text2text-generation", model=checkpoint)
    print(user_message)
    text = user_message
    text = "grammar: " + text

    output = model(text, max_length = int(len(user_message)*1.1))
    result = {'result': output[0]['generated_text']}
    print(result)
    return jsonify(result)

def writing_leftly(user_message):
    generator = pipeline('text-generation',
                     model='huggingtweets/writinglefty')
    output = generator(user_message, num_return_sequences=5)
    ans_list = str()
    for ans in output:
        ans_list += ans['generated_text'] 
        ans_list += "; " 
        ans_list += "\n"
    print(ans_list)
    result = {'result': ans_list}
    return jsonify(result)



if __name__ == '__main__':
    app.run(debug=True)
