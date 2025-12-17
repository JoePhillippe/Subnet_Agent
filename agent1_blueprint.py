"""
IPv4 Networking Tutor Agent with Subnetting Matrix
Matches Canvas Quiz Questions by Number
"""

from flask import Blueprint, Flask, render_template_string, request, jsonify, session, redirect, url_for
from anthropic import Anthropic
from functools import wraps
import os
import json
from datetime import datetime
import secrets
import random

agent1_bp = Blueprint("agent1", __name__)


# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Subnetting Matrix Reference
SUBNETTING_MATRIX = {
    "binary_values": [128, 64, 32, 16, 8, 4, 2, 1],
    "powers_of_2": [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
}

# Quiz questions - MATCHES CANVAS QUIZ ORDER
QUIZ_BANK = {
    "binary_to_decimal": [
        {"question": "Question 1: Convert Binary to Decimal: 01011000", "answer": "88", "number": 1},
        {"question": "Question 2: Convert Binary to Decimal: 01111011", "answer": "123", "number": 2},
        {"question": "Question 3: Convert Binary to Decimal: 11010001", "answer": "209", "number": 3},
        {"question": "Question 4: Convert Binary to Decimal: 00010110", "answer": "22", "number": 4},
        {"question": "Question 5: Convert Binary to Decimal: 01110010", "answer": "114", "number": 5},
        {"question": "Question 6: Convert Binary to Decimal: 11000000", "answer": "192", "number": 6},
        {"question": "Question 7: Convert Binary to Decimal: 00001111", "answer": "15", "number": 7},
        {"question": "Question 8: Convert Binary to Decimal: 11111001", "answer": "249", "number": 8},
        {"question": "Question 9: Convert Binary to Decimal: 00100101", "answer": "37", "number": 9},
        {"question": "Question 10: Convert Binary to Decimal: 10111100", "answer": "188", "number": 10},
    ],
    "decimal_to_binary": [
        {"question": "Question 1: Convert Decimal to Binary: 33", "answer": "00100001", "number": 1},
        {"question": "Question 2: Convert Decimal to Binary: 88", "answer": "01011000", "number": 2},
        {"question": "Question 3: Convert Decimal to Binary: 255", "answer": "11111111", "number": 3},
        {"question": "Question 4: Convert Decimal to Binary: 199", "answer": "11000111", "number": 4},
        {"question": "Question 5: Convert Decimal to Binary: 160", "answer": "10100000", "number": 5},
        {"question": "Question 6: Convert Decimal to Binary: 17", "answer": "00010001", "number": 6},
        {"question": "Question 7: Convert Decimal to Binary: 250", "answer": "11111010", "number": 7},
        {"question": "Question 8: Convert Decimal to Binary: 3", "answer": "00000011", "number": 8},
        {"question": "Question 9: Convert Decimal to Binary: 111", "answer": "01101111", "number": 9},
        {"question": "Question 10: Convert Decimal to Binary: 226", "answer": "11100010", "number": 10},
    ],
    "address_classification_identification": [
        {"question": "Question 1: Identify the class type: 192.168.2.25", "answer": "C", "number": 1},
        {"question": "Question 2: Identify the class type: 177.12.6.5", "answer": "B", "number": 2},
        {"question": "Question 3: Identify the class type: 112.25.48.1", "answer": "A", "number": 3},
        {"question": "Question 4: Identify the class type: 158.2.6.8", "answer": "B", "number": 4},
        {"question": "Question 5: Identify the class type: 198.9.74.6", "answer": "C", "number": 5},
        {"question": "Question 6: Identify the class type: 250.96.85.9", "answer": "E", "number": 6},
        {"question": "Question 7: Identify the class type: 226.254.98.7", "answer": "D", "number": 7},
        {"question": "Question 8: Identify the class type: 128.2.2.8", "answer": "B", "number": 8},
        {"question": "Question 9: Identify the class type: 191.250.158.89", "answer": "B", "number": 9},
        {"question": "Question 10: Identify the class type: 252.65.189.253", "answer": "E", "number": 10},
    ],
    "identify_default_subnet_mask": [
        {"question": "Question 1: Default Subnet Mask for: 10.87.54.105", "answer": "255.0.0.0", "number": 1},
        {"question": "Question 2: Default Subnet Mask for: 117.254.98.26", "answer": "255.0.0.0", "number": 2},
        {"question": "Question 3: Default Subnet Mask for: 127.254.64.287", "answer": "255.0.0.0", "number": 3},
        {"question": "Question 4: Default Subnet Mask for: 168.25.38.254", "answer": "255.255.0.0", "number": 4},
        {"question": "Question 5: Default Subnet Mask for: 191.54.71.47", "answer": "255.255.0.0", "number": 5},
        {"question": "Question 6: Default Subnet Mask for: 180.54.01.63", "answer": "255.255.0.0", "number": 6},
        {"question": "Question 7: Default Subnet Mask for: 197.254.35.11", "answer": "255.255.255.0", "number": 7},
        {"question": "Question 8: Default Subnet Mask for: 212.85.94.23", "answer": "255.255.255.0", "number": 8},
        {"question": "Question 9: Default Subnet Mask for: 201.255.254.8", "answer": "255.255.255.0", "number": 9},
        {"question": "Question 10: Default Subnet Mask for: 111.25.146.91", "answer": "255.0.0.0", "number": 10},
    ],
    "Identify_network_address_portion": [
        {"question": "Question 1: Identify network portion: 123.54.2.12 with mask 255.255.255.0", "answer": "123.54.2.0", "number": 1},
        {"question": "Question 2: Identify network portion: 11.2.54.9 with mask 255.255.255.0", "answer": "11.2.54.0", "number": 2},
        {"question": "Question 3: Identify network portion: 175.89.54.47 with mask 255.255.0.0", "answer": "175.89.0.0", "number": 3},
        {"question": "Question 4: Identify network portion: 12.254.87.9 with mask 255.255.255.0", "answer": "12.254.87.0", "number": 4},
        {"question": "Question 5: Identify network portion: 198.125.35.89 with mask 255.255.255.0", "answer": "198.125.35.0", "number": 5},
        {"question": "Question 6: Identify network portion: 130.65.98.78 with mask 255.255.0.0", "answer": "130.65.0.0", "number": 6},
        {"question": "Question 7: Identify network portion: 7.58.123.97 with mask 255.0.0.0", "answer": "7.0.0.0", "number": 7},
        {"question": "Question 8: Identify network portion: 154.254.254.32 with mask 255.255.255.0", "answer": "154.254.254.0", "number": 8},
        {"question": "Question 9: Identify network portion: 200.32.54.21 with mask 255.255.255.0", "answer": "200.32.54.0", "number": 9},
        {"question": "Question 10: Identify network portion: 117.65.252.98 with mask 255.255.0.0", "answer": "117.65.0.0", "number": 10},
    ],
    "identify_host_address_portion": [
        {"question": "Question 1: Identify host portion: 126.215.2.54 with mask 255.0.0.0", "answer": "0.215.2.54", "number": 1},
        {"question": "Question 2: Identify host portion: 8.254.65.129 with mask 255.0.0.0", "answer": "0.254.65.129", "number": 2},
        {"question": "Question 3: Identify host portion: 127.3.87.224 with mask 255.0.0.0", "answer": "0.3.87.224", "number": 3},
        {"question": "Question 4: Identify host portion: 135.54.159.68 with mask 255.255.0.0", "answer": "0.0.159.68", "number": 4},
        {"question": "Question 5: Identify host portion: 119.55.252.32 with mask 255.255.0.0", "answer": "0.0.252.32", "number": 5},
        {"question": "Question 6: Identify host portion: 188.254.230.39 with mask 255.255.0.0", "answer": "0.0.230.39", "number": 6},
        {"question": "Question 7: Identify host portion: 10.10.54.252 with mask 255.255.255.0", "answer": "0.0.0.252", "number": 7},
        {"question": "Question 8: Identify host portion: 128.65.17.47 with mask 255.255.255.0", "answer": "0.0.0.47", "number": 8},
        {"question": "Question 9: Identify host portion: 198.78.254.28 with mask 255.255.255.0", "answer": "0.0.0.28", "number": 9},
        {"question": "Question 10: Identify host portion: 116.254.89.230 with mask 255.0.0.0", "answer": "0.254.89.230", "number": 10},
    ],
    "ipv4_network_identification": [
        {"question": "Question 1: Identify network portion octet: 172.58.58.2", "answer": "First and Second octets", "number": 1},
        {"question": "Question 2: Identify network portion octet: 198.5.87.2", "answer": "First, Second, and Third octets", "number": 2},
        {"question": "Question 3: Identify network portion octet: 111.58.6.98", "answer": "First octet", "number": 3},
        {"question": "Question 4: Identify network portion octet: 198.54.65.2", "answer": "First, Second, and Third octets", "number": 4},
        {"question": "Question 5: Identify network portion octet: 128.254.54.111", "answer": "First and Second octets", "number": 5},
        {"question": "Question 6: Identify network portion octet: 9.58.254.67", "answer": "First octet", "number": 6},
        {"question": "Question 7: Identify network portion octet: 165.542.250.2", "answer": "First and Second octets", "number": 7},
        {"question": "Question 8: Identify network portion octet: 210.54.250.76", "answer": "First, Second, and Third octets", "number": 8},
        {"question": "Question 9: Identify network portion octet: 126.254.254.8", "answer": "First octet", "number": 9},
        {"question": "Question 10: Identify network portion octet: 109.254.65.21", "answer": "First octet", "number": 10},
    ],
    "ipv4_host_identification": [
        {"question": "Question 1: Identify host portion octet: 172.68.54.9", "answer": "Third and Fourth octets", "number": 1},
        {"question": "Question 2: Identify host portion octet: 154.254.65.65", "answer": "Third and Fourth octets", "number": 2},
        {"question": "Question 3: Identify host portion octet: 191.254.65.87", "answer": "Third and Fourth octets", "number": 3},
        {"question": "Question 4: Identify host portion octet: 119.254.87.223", "answer": "Second, Third, and Fourth octets", "number": 4},
        {"question": "Question 5: Identify host portion octet: 10.65.87.123", "answer": "Second, Third, and Fourth octets", "number": 5},
        {"question": "Question 6: Identify host portion octet: 23.32.250.65", "answer": "Second, Third, and Fourth octets", "number": 6},
        {"question": "Question 7: Identify host portion octet: 193.254.32.12", "answer": "Fourth octet", "number": 7},
        {"question": "Question 8: Identify host portion octet: 221.54.32.1", "answer": "Fourth octet", "number": 8},
        {"question": "Question 9: Identify host portion octet: 192.165.2.98", "answer": "Fourth octet", "number": 9},
        {"question": "Question 10: Identify host portion octet: 100.54.87.32", "answer": "Second, Third, and Fourth octets", "number": 10},
    ],
}

# System prompt
SYSTEM_PROMPT = """You are an enthusiastic and patient IPv4 networking tutor. Help students master binary conversion, IP classification, and subnetting using the Powers of 2 Matrix.

POWERS OF 2 MATRIX:
Binary Value Line: 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1
Powers of 2: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048...

BINARY CONVERSION:
Decimal to Binary (Subtraction): Start with the binary line, subtract largest values, mark 1 if you can subtract, 0 if not
Binary to Decimal (Addition): Add up all values where there is a 1

ADDRESS CLASSIFICATION:
- Class A: 1-127 → Mask: 255.0.0.0 → N.H.H.H
- Class B: 128-191 → Mask: 255.255.0.0 → N.N.H.H  
- Class C: 192-223 → Mask: 255.255.255.0 → N.N.N.H
- Class D: 224-239 (multicast)
- Class E: 240-255 (experimental)

GOLDEN RULE: 255 in mask = Network, 0 in mask = Host

ATTEMPT PROGRESSION:
1. First: Gentle hint about concept, reference matrix
2. Second: Show first step using matrix
3. Third: Walk through half the solution
4. Fourth: Detailed step-by-step with matrix
5. Fifth: Complete answer with full explanation

Be encouraging, use humor, reference the Powers of 2 Matrix, and celebrate learning from mistakes!"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>IPv4 Tutor</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .matrix-reference {
            padding: 15px 30px;
            background: #e7f3ff;
            border-bottom: 2px solid #2196F3;
            font-family: 'Courier New', monospace;
            text-align: center;
        }
        .matrix-reference h3 { color: #1976D2; margin-bottom: 10px; }
        .matrix-line { font-weight: bold; color: #0D47A1; font-size: 0.95em; }
        .quiz-selector {
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
        }
        .quiz-selector label { font-weight: bold; margin-right: 10px; }
        .quiz-selector select {
            padding: 10px 15px;
            border-radius: 8px;
            border: 2px solid #667eea;
            font-size: 1em;
            cursor: pointer;
            background: white;
        }
        .quiz-selector button {
            padding: 10px 25px;
            margin-left: 10px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
        }
        .quiz-selector button:hover { background: #5568d3; }
        .chat-container {
            height: 450px;
            overflow-y: auto;
            padding: 30px;
            background: #ffffff;
        }
        .message {
            margin-bottom: 20px;
            padding: 15px 20px;
            border-radius: 12px;
            max-width: 80%;
            line-height: 1.6;
        }
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message { background: #f1f3f5; color: #212529; }
        .attempt-indicator {
            padding: 15px 30px;
            background: #fff3cd;
            border-top: 2px solid #ffc107;
            font-weight: bold;
            text-align: center;
            color: #856404;
        }
        .input-container {
            padding: 20px 30px;
            background: #f8f9fa;
            border-top: 2px solid #dee2e6;
            display: flex;
            gap: 10px;
        }
        .input-container input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ced4da;
            border-radius: 8px;
            font-size: 1em;
        }
        .input-container button {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
        }
        .input-container button:hover { background: #5568d3; }
        .input-container button:disabled {
            background: #adb5bd;
            cursor: not-allowed;
        }
        .loading { display: none; text-align: center; padding: 10px; color: #667eea; }
        .nav-bar {
            padding: 10px 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav-bar a {
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
            padding: 8px 15px;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav-bar a:hover { background: #e9ecef; }
    </style>
</head>
    <script>
        var conversationHistory = [];
        var currentAttempt = 0;
        var currentQuestion = null;

        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('question-select-btn').addEventListener('click', selectQuestionNumber);
            document.getElementById('reset-btn').addEventListener('click', resetSession);
            document.getElementById('submit-btn').addEventListener('click', sendMessage);
            document.getElementById('user-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        });

        function selectQuestionNumber() {
            var quizType = document.getElementById('quiz-type').value;
            var questionNum = parseInt(document.getElementById('question-num').value);
            
            if (isNaN(questionNum) || questionNum < 1 || questionNum > 10) {
                alert('Please enter a number between 1 and 10');
                return;
            }
            
            fetch('/get_question_by_number', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({quiz_type: quizType, question_number: questionNum})
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                currentQuestion = data.question;
                currentAttempt = 0;
                conversationHistory = [];
                document.getElementById('chat-container').innerHTML = '';
                document.getElementById('user-input').value = '';
                updateAttemptIndicator();
                addMessage('bot', data.message);
                document.getElementById('user-input').focus();
            })
            .catch(function(err) { alert('Error: ' + err.message); });
        }

        function sendMessage() {
            var input = document.getElementById('user-input');
            var message = input.value.trim();
            
            if (!message) return;
            if (!currentQuestion) {
                alert('Start a question first!');
                return;
            }
            
            input.value = '';
            input.disabled = true;
            document.getElementById('submit-btn').disabled = true;
            document.getElementById('loading').style.display = 'block';
            
            addMessage('user', message);
            
            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: message,
                    question: currentQuestion,
                    attempt: currentAttempt
                })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                currentAttempt = data.attempt;
                addMessage('bot', data.response);
                updateAttemptIndicator();
                
                if (data.is_correct || currentAttempt >= 5) {
                    document.getElementById('submit-btn').textContent = 'New Question';
                    setTimeout(function() {
                        document.getElementById('submit-btn').textContent = 'Submit';
                    }, 3000);
                }
            })
            .catch(function(err) {
                addMessage('bot', 'Error! Try again.');
            })
            .finally(function() {
                document.getElementById('loading').style.display = 'none';
                input.disabled = false;
                document.getElementById('submit-btn').disabled = false;
                input.focus();
            });
        }

        function addMessage(sender, text) {
            var chatContainer = document.getElementById('chat-container');
            var messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + sender + '-message';
            messageDiv.innerHTML = text.replace(/\\n/g, '<br>');
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            conversationHistory.push({role: sender, content: text});
        }

        function updateAttemptIndicator() {
            var indicator = document.getElementById('attempt-indicator');
            if (currentAttempt === 0) {
                indicator.innerHTML = 'First attempt - You got this!';
                indicator.style.background = '#d1ecf1';
                indicator.style.borderColor = '#17a2b8';
                indicator.style.color = '#0c5460';
            } else if (currentAttempt < 5) {
                indicator.innerHTML = 'Attempt ' + currentAttempt + ' of 5 - Learning!';
                indicator.style.background = '#fff3cd';
                indicator.style.borderColor = '#ffc107';
                indicator.style.color = '#856404';
            } else {
                indicator.innerHTML = 'Complete! Try another question?';
                indicator.style.background = '#d4edda';
                indicator.style.borderColor = '#28a745';
                indicator.style.color = '#155724';
            }
        }

        function resetSession() {
            if (confirm('Reset and start fresh?')) {
                fetch('/reset', {method: 'POST'})
                .then(function() { location.reload(); });
            }
        }
    </script>
<body>
    <div class="container">
        <div class="header">
            <h1>IPv4 Networking Tutor</h1>
            <p>Master Binary, IP Classification and Subnetting</p>
        </div>
        
        <div class="nav-bar">
            <a href="http://localhost:5000/">← Back to Menu</a>
            <a href="http://localhost:5000/logout">Logout</a>
        </div>
        
        <div class="matrix-reference">
            <h3>Powers of 2 Matrix</h3>
            <div class="matrix-line">Binary: 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1</div>
            <div class="matrix-line">Powers: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024...</div>
        </div>
        
        <div class="quiz-selector">
            <label for="quiz-type">Select Quiz Topic:</label>
            <select id="quiz-type">
                <option value="binary_to_decimal">Binary to Decimal</option>
                <option value="decimal_to_binary">Decimal to Binary</option>
                <option value="address_classification_identification">Address Classification Identification</option>
                <option value="identify_default_subnet_mask">Identify Default Subnet Mask</option>
                <option value="Identify_network_address_portion">Identifying Network Address Portion</option>
                <option value="identify_host_address_portion">Identify Host Address Portion</option>
                <option value="ipv4_network_identification">IPv4 Network Identification</option>
                <option value="ipv4_host_identification">IPv4 Host Identification</option>
            </select>
            <label for="question-num" style="margin-left: 20px;">Question Number (1-10):</label>
            <input type="text" id="question-num" value="1" maxlength="2" style="width: 60px; padding: 10px; border-radius: 8px; border: 2px solid #667eea; text-align: center;">
            <button id="question-select-btn">Load Question</button>
            <button id="reset-btn">Reset</button>
        </div>
        
        <div id="attempt-indicator" class="attempt-indicator">
            Ready! Pick a topic and click a button
        </div>
        
        <div id="chat-container" class="chat-container">
            <div class="message bot-message">
                Hello! I am your IPv4 tutor. Use the Powers of 2 Matrix above as your guide. Pick a quiz topic and start learning!
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Type your answer...">
            <button id="submit-btn">Submit</button>
        </div>
        
        <div class="loading" id="loading"><p>Thinking...</p></div>
    </div>


</body>
</html>"""

def get_random_question(quiz_type):
    questions = QUIZ_BANK.get(quiz_type, [])
    if questions:
        return random.choice(questions)
    return None

def get_question_by_number(quiz_type, question_number):
    questions = QUIZ_BANK.get(quiz_type, [])
    for q in questions:
        if q.get('number') == question_number:
            return q
    return None

def check_answer(user_answer, correct_answer):
    user_clean = user_answer.strip().upper().replace(" ", "").replace(".", "")
    correct_clean = correct_answer.strip().upper().replace(" ", "").replace(".", "")
    return user_clean == correct_clean

def get_hint_level_prompt(attempt, question, correct_answer):
    if attempt == 1:
        return "Give a gentle hint. Reference the Powers of 2 Matrix. Do not give the answer."
    elif attempt == 2:
        return "Show the first step using the Powers of 2 Matrix. Be encouraging."
    elif attempt == 3:
        return "Walk through half the solution with matrix values."
    elif attempt == 4:
        return "Provide detailed steps using the matrix, but let student finish."
    else:
        msg = "Give the complete answer '" + correct_answer + "' with full explanation using the Powers of 2 Matrix. "
        msg += "Be very encouraging about their effort."
        return msg

@agent1_bp.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@agent1_bp.route('/new_question', methods=['POST'])
def new_question():
    try:
        data = request.json
        quiz_type = data.get('quiz_type', 'binary_to_decimal')
        
        print("[DEBUG] New question:", quiz_type)
        
        question_data = get_random_question(quiz_type)
        if not question_data:
            return jsonify({'error': 'No questions available'}), 400
        
        session['current_question'] = question_data
        session['attempt_count'] = 0
        
        msg = "Here is your question:\n\n"
        msg += question_data['question']
        msg += "\n\nUse the Powers of 2 Matrix: 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1"
        
        # Add format examples for network/host identification questions
        if quiz_type == 'ipv4_network_identification' or quiz_type == 'ipv4_host_identification':
            msg += '\n\nAnswer Format Examples:\n- "First octet"\n- "First and Second octets"\n- "Second, Third, and Fourth octets"\n- "First, Second, and Third octets"'
        
        return jsonify({'question': question_data, 'message': msg})
    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({'error': str(e)}), 500

@agent1_bp.route('/get_question_by_number', methods=['POST'])
def get_question_by_number_route():
    try:
        data = request.json
        quiz_type = data.get('quiz_type', 'binary_to_decimal')
        question_number = data.get('question_number', 1)
        
        print("[DEBUG] Question", question_number, "for", quiz_type)
        
        question_data = get_question_by_number(quiz_type, question_number)
        if not question_data:
            return jsonify({'error': 'Question not found'}), 400
        
        session['current_question'] = question_data
        session['attempt_count'] = 0
        
        msg = "Canvas Question:\n\n"
        msg += question_data['question']
        msg += "\n\nUse the Powers of 2 Matrix: 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1"
        
        # Add format examples for network/host identification questions
        if quiz_type == 'ipv4_network_identification' or quiz_type == 'ipv4_host_identification':
            msg += '\n\nAnswer Format Examples:\n- "First octet"\n- "First and Second octets"\n- "Second, Third, and Fourth octets"\n- "First, Second, and Third octets"'
        
        return jsonify({'question': question_data, 'message': msg})
    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({'error': str(e)}), 500

@agent1_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    question_data = data.get('question')
    current_attempt = data.get('attempt', 0)
    
    if not question_data:
        return jsonify({'error': 'No active question'}), 400
    
    current_attempt += 1
    correct_answer = question_data['answer']
    
    is_correct = check_answer(user_message, correct_answer)
    
    if is_correct:
        celebrations = [
            "YES! Correct! The answer is " + correct_answer + ". You got it on attempt " + str(current_attempt) + "!",
            "Perfect! " + correct_answer + " is right! Attempt " + str(current_attempt),
            "Excellent! " + correct_answer + " is correct! Great work!",
            "Fantastic! " + correct_answer + " - you nailed it!"
        ]
        response_text = random.choice(celebrations)
        
        return jsonify({
            'response': response_text,
            'is_correct': True,
            'attempt': current_attempt
        })
    
    hint_prompt = get_hint_level_prompt(current_attempt, question_data['question'], correct_answer)
    
    messages = [{
        "role": "user",
        "content": "Question: " + question_data['question'] + "\nCorrect Answer: " + correct_answer + "\nStudent Answer: " + user_message + "\nAttempt: " + str(current_attempt) + " of 5\n\n" + hint_prompt
    }]
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        
        bot_response = response.content[0].text
        
        return jsonify({
            'response': bot_response,
            'is_correct': False,
            'attempt': current_attempt
        })
        
    except Exception as e:
        return jsonify({
            'response': "Sorry, error: " + str(e),
            'is_correct': False,
            'attempt': current_attempt
        })

@agent1_bp.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return jsonify({'status': 'success'})

