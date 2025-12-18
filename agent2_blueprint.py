"""
Custom Subnet Mask Tutor Agent - Based on Professor Bodden's Methodology
Helps students work through 6 custom subnet mask problems with 10 parts each
"""

from flask import Blueprint, Flask, render_template_string, request, jsonify, session, redirect, url_for
from functools import wraps
from anthropic import Anthropic
import os
import secrets

agent2_bp = Blueprint("agent2", __name__)


# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Powers of 2 Matrix Reference
POWERS_OF_2 = {
    "binary_values": [128, 64, 32, 16, 8, 4, 2, 1],
    "powers": [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]
}

# The 6 Custom Subnet Mask Problems
PROBLEMS = {
    1: {
        "name": "Problem 1",
        "subnets_needed": 15,
        "hosts_needed": 14,
        "network_address": "222.25.12.0",
        "answers": {
            "part1": "C",
            "part2": "255.255.255.0",
            "part3": "4",
            "part4": "4",
            "part5": "16",
            "part6": "16",
            "part7": "14",
            "part8": "255.255.255.240",
            "part9": "28",
            "part10": "N.N.N.sssshhhh"
        }
    },
    2: {
        "name": "Problem 2",
        "subnets_needed": 4,
        "hosts_needed": 58,
        "network_address": "222.125.52.0",
        "answers": {
            "part1": "C",
            "part2": "255.255.255.0",
            "part3": "2",
            "part4": "6",
            "part5": "4",
            "part6": "64",
            "part7": "62",
            "part8": "255.255.255.192",
            "part9": "26",
            "part10": "N.N.N.sshhhhhh"
        }
    },
    3: {
        "name": "Problem 3",
        "subnets_needed": 120,
        "hosts_needed": 500,
        "network_address": "132.112.0.0",
        "answers": {
            "part1": "B",
            "part2": "255.255.0.0",
            "part3": "7",
            "part4": "9",
            "part5": "128",
            "part6": "512",
            "part7": "510",
            "part8": "255.255.254.0",
            "part9": "23",
            "part10": "N.N.sssssssh.H"
        }
    },
    4: {
        "name": "Problem 4",
        "subnets_needed": 1000,
        "hosts_needed": 60,
        "network_address": "168.254.0.0",
        "answers": {
            "part1": "B",
            "part2": "255.255.0.0",
            "part3": "10",
            "part4": "6",
            "part5": "1024",
            "part6": "64",
            "part7": "62",
            "part8": "255.255.255.192",
            "part9": "26",
            "part10": "N.N.ssssssss.sshhhhhh"
        }
    },
    5: {
        "name": "Problem 5",
        "subnets_needed": 1000,
        "hosts_needed": 16000,
        "network_address": "111.0.0.0",
        "answers": {
            "part1": "A",
            "part2": "255.0.0.0",
            "part3": "10",
            "part4": "14",
            "part5": "1024",
            "part6": "16384",
            "part7": "16382",
            "part8": "255.255.192.0",
            "part9": "18",
            "part10": "N.ssssssss.sshhhhhh.H"
        }
    },
    6: {
        "name": "Problem 6",
        "subnets_needed": 120,
        "hosts_needed": 131000,
        "network_address": "10.0.0.0",
        "answers": {
            "part1": "A",
            "part2": "255.0.0.0",
            "part3": "7",
            "part4": "17",
            "part5": "128",
            "part6": "131072",
            "part7": "131070",
            "part8": "255.254.0.0",
            "part9": "15",
            "part10": "N.sssssssh.H.H"
        }
    }
}

PART_DESCRIPTIONS = {
    "part1": "Address Class",
    "part2": "Default Subnet Mask",
    "part3": "Number of subnet (borrowed) bits",
    "part4": "Number of host bits",
    "part5": "Total number of subnets",
    "part6": "Total number of addresses",
    "part7": "Number of usable addresses",
    "part8": "Custom subnet mask",
    "part9": "Total number of network bits",
    "part10": "Custom address map (Letters)"
}

# System Prompt - Teaching Style
SYSTEM_PROMPT = """You are an enthusiastic and patient Cisco networking tutor teaching custom subnet mask assignments. You help students work through subnet problems using a step-by-step methodology with the Subnetting Matrix.

STUDENTS HAVE ACCESS TO THE FULL SUBNETTING MATRIX - Encourage them to use it! The matrix shows:
- All possible subnet/host combinations for each class
- Custom subnet masks for each configuration
- CIDR prefix notation
- Custom Address Map (CAM) patterns

POWERS OF 2 MATRIX (Critical Reference):
Binary Value Line: 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1
Powers of 2: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072

CRITICAL FORMULAS:
1. SUBNETS: 2^s = number of subnets
   - Must round UP to next power of 2 if not exact
   - Example: Need 15 subnets → 2^4 = 16 (closest power of 2)
   - Students find this in the matrix!

2. HOSTS: 2^h - 2 = usable addresses
   - NEVER FORGET THE MINUS 2!
   - Minus 2 = first and last addresses (unusable)
   - Example: Need 14 usable → Need 16 total → 2^4 = 16, then 16-2 = 14 usable
   - Students find this in the matrix!

3. BIT VALIDATION: Subnet bits + Host bits MUST equal available bits
   - Class C: 8 bits available (4th octet)
   - Class B: 16 bits available (3rd & 4th octets)
   - Class A: 24 bits available (2nd, 3rd & 4th octets)

ADDRESS CLASSIFICATION (Look at first octet):
- Class A: 1-127 → Default Mask: 255.0.0.0 → N.H.H.H (24 bits to work with)
- Class B: 128-191 → Default Mask: 255.255.0.0 → N.N.H.H (16 bits to work with)
- Class C: 192-223 → Default Mask: 255.255.255.0 → N.N.N.H (8 bits to work with)

GOLDEN RULES:
1. 255 in mask = Network portion (CANNOT CHANGE)
2. 0 in mask = Host portion (WHERE YOU DO MATH)
3. Subnets = 1's in binary (shown as 's' in CAM)
4. Hosts = 0's in binary (shown as 'h' in CAM)
5. Always validate: subnet bits + host bits = total available bits

HOW TO USE THE MATRIX:
1. Identify the class → Use that class's matrix sheet
2. Find the row where 2^s meets subnet requirement
3. Find the row where 2^h - 2 meets host requirement  
4. Both requirements should be on the SAME ROW!
5. Read the custom subnet mask from that row
6. The matrix gives you Parts 3, 4, 5, 6, 7, 8, 9, and 10 directly!

CUSTOM ADDRESS MAP (CAM):
- N = Full network octet (from default mask)
- s = Subnet bit (lowercase)
- h = Host bit (lowercase)
- H = Full host octet (all 8 bits are host bits)
- NO DOTS between bits in same octet!
- Example: N.N.N.sssshhhh means 4 subnet bits and 4 host bits in 4th octet

TEACHING APPROACH (Progressive Hints):
1st Attempt: Ask "Have you looked at the matrix? What class is this address?" Give conceptual guidance
2nd Attempt: "Look at the matrix for [Class]. Find the row where 2^s equals or exceeds [number]. What do you see?"
3rd Attempt: Walk through finding the correct row, show how to validate
4th Attempt: Show the exact row in the matrix and explain how to read the answer
5th Attempt: Give complete answer with full explanation of matrix lookup process

IMPORTANT TEACHING PHRASES:
- "Check the matrix - it's your best friend!"
- "Remember the minus 2 - never forget it!"
- "Write it out if you need to see it!"
- "Does your math work? Subnet bits + host bits should equal [X] for Class [Y]"
- "Look at the matrix - what row gives you both what you need?"
- "Okay, all right, you got this!"

Be encouraging! Use Professor Bodden's casual, supportive tone. Celebrate learning from mistakes, and always guide students back to the matrix."""

# HTML Template with improved UI
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Custom Subnet Mask Tutor</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        
        .matrix-reference {
            padding: 15px 30px;
            background: #e3f2fd;
            border-bottom: 3px solid #1976D2;
            font-family: 'Courier New', monospace;
        }
        .matrix-reference h3 { color: #0D47A1; margin-bottom: 10px; text-align: center; }
        .matrix-line { font-weight: bold; color: #0D47A1; font-size: 0.95em; text-align: center; margin: 5px 0; }
        
        .problem-selector {
            padding: 20px 30px;
            background: #f5f5f5;
            border-bottom: 2px solid #ddd;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        .problem-selector h3 { color: #1e3c72; flex: 100%; margin-bottom: 10px; }
        .problem-btn {
            padding: 12px 20px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
        }
        .problem-btn:hover { background: #1e3c72; transform: translateY(-2px); }
        .problem-btn.active { background: #4CAF50; }
        
        .problem-info {
            padding: 20px 30px;
            background: #fff3cd;
            border-bottom: 2px solid #ffc107;
        }
        .problem-info h3 { color: #856404; margin-bottom: 10px; }
        .problem-info p { color: #856404; font-weight: bold; margin: 5px 0; }
        
        .parts-list {
            padding: 20px 30px;
            background: #f9f9f9;
            border-bottom: 2px solid #ddd;
            max-height: 200px;
            overflow-y: auto;
        }
        .parts-list h4 { color: #1e3c72; margin-bottom: 10px; }
        .part-item {
            padding: 8px 12px;
            margin: 5px 0;
            background: white;
            border-left: 4px solid #ccc;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .part-item:hover { border-left-color: #2a5298; background: #e3f2fd; }
        .part-item.active { border-left-color: #4CAF50; background: #e8f5e9; font-weight: bold; }
        .part-item.correct { border-left-color: #4CAF50; background: #e8f5e9; }
        
        .chat-container {
            height: 400px;
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
            background: #2a5298;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message { background: #f1f3f5; color: #212529; }
        
        .attempt-indicator {
            padding: 15px 30px;
            background: #d1ecf1;
            border-top: 2px solid #17a2b8;
            font-weight: bold;
            text-align: center;
            color: #0c5460;
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
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
        }
        .input-container button:hover { background: #1e3c72; }
        .input-container button:disabled {
            background: #adb5bd;
            cursor: not-allowed;
        }
        .loading { display: none; text-align: center; padding: 10px; color: #2a5298; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Custom Subnet Mask Tutor</h1>
            <p>Master Subnetting with Progressive Hints</p>
        </div>
        
        <div class="matrix-reference">
            <h3>Powers of 2 Matrix - Your Best Friend!</h3>
            <div class="matrix-line">Binary Value Line: 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1</div>
            <div class="matrix-line">Powers of 2: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048...</div>
        </div>
        
        <div class="problem-selector">
            <h3>📚 Select a Problem (6 Total)</h3>
            <button class="problem-btn" data-problem="1">Problem 1</button>
            <button class="problem-btn" data-problem="2">Problem 2</button>
            <button class="problem-btn" data-problem="3">Problem 3</button>
            <button class="problem-btn" data-problem="4">Problem 4</button>
            <button class="problem-btn" data-problem="5">Problem 5</button>
            <button class="problem-btn" data-problem="6">Problem 6</button>
            <button class="problem-btn" id="reset-btn" style="margin-left: auto; background: #dc3545;">Reset All</button>
        </div>
        
        <div class="problem-info" id="problem-info" style="display: none;">
            <h3 id="problem-name">Problem Name</h3>
            <p>Network Address: <span id="network-address"></span></p>
            <p>Subnets Needed: <span id="subnets-needed"></span></p>
            <p>Usable Hosts Needed: <span id="hosts-needed"></span></p>
        </div>
        
        <div class="parts-list" id="parts-list" style="display: none;">
            <h4>📝 Problem Parts (Click to work on):</h4>
            <div id="parts-container"></div>
        </div>
        
        <div id="attempt-indicator" class="attempt-indicator">
            Welcome! Select a problem to begin learning subnet masking.
        </div>
        
        <div id="chat-container" class="chat-container">
            <div class="message bot-message">
                👋 Hello! I'm Professor Bodden, your subnet tutor.<br><br>
                Select one of the 6 problems above to get started. Each problem has 10 parts to work through.<br><br>
                Remember: Use the Powers of 2 Matrix, never forget the minus 2, and write things out if you need to!
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Type your answer..." disabled>
            <button id="submit-btn" disabled>Submit</button>
        </div>
        
        <div class="loading" id="loading"><p>🤔 Thinking...</p></div>
    </div>

    <script>
        let currentProblem = null;
        let currentPart = null;
        let currentAttempt = 0;
        let completedParts = new Set();

        // Initialize after DOM loads
        document.addEventListener('DOMContentLoaded', function() {
            // Problem button listeners
            document.querySelectorAll('.problem-btn[data-problem]').forEach(btn => {
                btn.addEventListener('click', function() {
                    loadProblem(parseInt(this.getAttribute('data-problem')));
                });
            });
            
            // Reset button listener
            document.getElementById('reset-btn').addEventListener('click', resetSession);
            
            // Submit button listener
            document.getElementById('submit-btn').addEventListener('click', sendMessage);
            
            // Enter key listener
            document.getElementById('user-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        });

        function loadProblem(problemNum) {
            fetch('/load_problem', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({problem_number: problemNum})
            })
            .then(r => r.json())
            .then(data => {
                currentProblem = problemNum;
                currentPart = null;
                currentAttempt = 0;
                completedParts.clear();
                
                // Update UI
                document.querySelectorAll('.problem-btn[data-problem]').forEach(btn => btn.classList.remove('active'));
                document.querySelector(`[data-problem="${problemNum}"]`).classList.add('active');
                
                document.getElementById('problem-info').style.display = 'block';
                document.getElementById('problem-name').textContent = data.problem.name;
                document.getElementById('network-address').textContent = data.problem.network_address;
                document.getElementById('subnets-needed').textContent = data.problem.subnets_needed;
                document.getElementById('hosts-needed').textContent = data.problem.hosts_needed;
                
                document.getElementById('parts-list').style.display = 'block';
                renderParts();
                
                document.getElementById('chat-container').innerHTML = '';
                addMessage('bot', data.message);
                updateAttemptIndicator();
                
                document.getElementById('user-input').disabled = true;
                document.getElementById('submit-btn').disabled = true;
            });
        }

        function renderParts() {
            const container = document.getElementById('parts-container');
            container.innerHTML = '';
            for (let i = 1; i <= 10; i++) {
                const partDiv = document.createElement('div');
                partDiv.className = 'part-item';
                if (completedParts.has(`part${i}`)) partDiv.classList.add('correct');
                if (currentPart === `part${i}`) partDiv.classList.add('active');
                partDiv.textContent = `Part ${i}: ${getPartDescription(i)}`;
                partDiv.addEventListener('click', () => selectPart(i));
                container.appendChild(partDiv);
            }
        }

        function getPartDescription(partNum) {
            const descriptions = {
                1: "Address Class",
                2: "Default Subnet Mask",
                3: "Number of subnet (borrowed) bits",
                4: "Number of host bits",
                5: "Total number of subnets",
                6: "Total number of addresses",
                7: "Number of usable addresses",
                8: "Custom subnet mask",
                9: "Total number of network bits",
                10: "Custom address map (Letters)"
            };
            return descriptions[partNum];
        }

        function selectPart(partNum) {
            if (!currentProblem) {
                alert('Please select a problem first!');
                return;
            }
            
            currentPart = `part${partNum}`;
            currentAttempt = 0;
            renderParts();
            
            fetch('/select_part', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    problem_number: currentProblem,
                    part: currentPart
                })
            })
            .then(r => r.json())
            .then(data => {
                addMessage('bot', data.message);
                document.getElementById('user-input').disabled = false;
                document.getElementById('submit-btn').disabled = false;
                document.getElementById('user-input').focus();
                updateAttemptIndicator();
            });
        }

        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (!message || !currentPart) return;
            
            input.value = '';
            input.disabled = true;
            document.getElementById('submit-btn').disabled = true;
            document.getElementById('loading').style.display = 'block';
            
            addMessage('user', message);
            
            fetch('chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    problem_number: currentProblem,
                    part: currentPart,
                    answer: message,
                    attempt: currentAttempt
                })
            })
            .then(r => r.json())
            .then(data => {
                console.log('Response data:', data);
                console.log('Current part:', currentPart);
                console.log('Is correct:', data.is_correct);
                console.log('Address class:', data.address_class);
                
                currentAttempt = data.attempt;
                addMessage('bot', data.response);
                
                if (data.is_correct) {
                    completedParts.add(currentPart);
                    renderParts();
                    
                    // If Part 2 (Default Subnet Mask) is correct, open matrix in new tab
                    if (currentPart === 'part2' && data.address_class) {
                        console.log('Opening matrix for class:', data.address_class);
                        const matrixUrl = '/matrix/' + data.address_class;
                        console.log('Matrix URL:', matrixUrl);
                        window.open(matrixUrl, '_blank');
                    }
                }
                
                updateAttemptIndicator();
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('bot', 'Error connecting to server. Please try again.');
            })
            .finally(() => {
                document.getElementById('loading').style.display = 'none';
                input.disabled = false;
                document.getElementById('submit-btn').disabled = false;
                input.focus();
            });
        }

        function addMessage(sender, text) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + sender + '-message';
            messageDiv.innerHTML = text.replace(/\\n/g, '<br>');
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function updateAttemptIndicator() {
            const indicator = document.getElementById('attempt-indicator');
            if (!currentPart) {
                indicator.innerHTML = 'Select a part to begin!';
                indicator.style.background = '#d1ecf1';
            } else if (currentAttempt === 0) {
                indicator.innerHTML = 'First attempt - You got this! 💪';
                indicator.style.background = '#d1ecf1';
            } else if (currentAttempt < 5) {
                indicator.innerHTML = `Attempt ${currentAttempt} of 5 - Keep learning! 📚`;
                indicator.style.background = '#fff3cd';
            } else {
                indicator.innerHTML = 'Complete! Try another part or problem 🎉';
                indicator.style.background = '#d4edda';
            }
        }

        function resetSession() {
            if (confirm('Reset all progress and start fresh?')) {
                fetch('reset', {method: 'POST'})
                .then(() => location.reload());
            }
        }
    </script>
</body>
</html>"""

def normalize_answer(answer):
    """Normalize answers for comparison"""
    return str(answer).strip().upper().replace(" ", "").replace(".", "")

def check_answer(user_answer, correct_answer):
    """Check if student answer matches correct answer"""
    return normalize_answer(user_answer) == normalize_answer(correct_answer)

def get_hint_prompt(attempt, part, problem_data):
    """Generate progressive hints based on attempt number"""
    part_desc = PART_DESCRIPTIONS.get(part, "")
    correct = problem_data['answers'][part]
    subnets = problem_data['subnets_needed']
    hosts = problem_data['hosts_needed']
    address = problem_data['network_address']
    
    context = f"""
Problem Context:
- Network Address: {address}
- Subnets Needed: {subnets}
- Usable Hosts Needed: {hosts}
- Current Part: {part_desc}
- Correct Answer: {correct}
"""
    
    if attempt == 1:
        return context + "\nGive a gentle hint. Ask what they know about this concept. Reference the Powers of 2 Matrix if relevant. Do NOT give the answer."
    elif attempt == 2:
        return context + "\nShow which formula or concept to use. Reference the Powers of 2 Matrix. Give an example but not the complete answer."
    elif attempt == 3:
        return context + "\nWalk through the first half of the solution. Show the setup and initial calculations. Let them finish."
    elif attempt == 4:
        return context + "\nProvide detailed step-by-step work, but stop just before the final answer. Let them complete the last step."
    else:
        return context + f"\nGive the complete answer '{correct}' with full explanation. Show all work using the Powers of 2 Matrix and formulas. Be very encouraging about their effort!"

@agent2_bp.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@agent2_bp.route('/load_problem', methods=['POST'])
def load_problem():
    data = request.json
    problem_num = data.get('problem_number')
    
    if problem_num not in PROBLEMS:
        return jsonify({'error': 'Invalid problem number'}), 400
    
    problem = PROBLEMS[problem_num]
    session['current_problem'] = problem_num
    session['completed_parts'] = []
    
    message = f"""📖 <strong>{problem['name']}</strong> loaded!<br><br>
<strong>Network Address:</strong> {problem['network_address']}<br>
<strong>Subnets Needed:</strong> {problem['subnets_needed']}<br>
<strong>Usable Hosts Needed:</strong> {problem['hosts_needed']}<br><br>
This problem has 10 parts. Click on any part to begin working on it!<br><br>
<em>Tip: Start by identifying the address class and default subnet mask, then use the matrix!</em><br>
Remember: <strong>NEVER forget the minus 2</strong> for host calculations! 🎯"""
    
    return jsonify({'problem': problem, 'message': message})

@agent2_bp.route('/select_part', methods=['POST'])
def select_part():
    data = request.json
    problem_num = data.get('problem_number')
    part = data.get('part')
    
    if not problem_num or not part:
        return jsonify({'error': 'Missing data'}), 400
    
    problem = PROBLEMS[problem_num]
    part_desc = PART_DESCRIPTIONS.get(part, "Unknown part")
    
    session['current_part'] = part
    session['attempt_count'] = 0
    
    message = f"""📝 <strong>Part {part[-1]}: {part_desc}</strong><br><br>
What is your answer?<br><br>
<em>Hint: Review the problem requirements and use the Powers of 2 Matrix!</em>"""
    
    return jsonify({'message': message})

@agent2_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    problem_num = data.get('problem_number')
    part = data.get('part')
    user_answer = data.get('answer', '')
    current_attempt = data.get('attempt', 0)
    
    if not problem_num or not part:
        return jsonify({'error': 'No active problem/part'}), 400
    
    problem = PROBLEMS[problem_num]
    correct_answer = problem['answers'][part]
    current_attempt += 1
    
    # Check if correct
    if check_answer(user_answer, correct_answer):
        celebrations = [
            f"🎉 <strong>YES! Correct!</strong> The answer is <strong>{correct_answer}</strong>. You got it on attempt {current_attempt}! Great work!",
            f"✅ <strong>Perfect!</strong> {correct_answer} is right! Nailed it on attempt {current_attempt}!",
            f"🌟 <strong>Excellent!</strong> {correct_answer} is correct! You're mastering this!",
            f"💯 <strong>Outstanding!</strong> {correct_answer} - exactly right! Keep it up!"
        ]
        import random
        response_text = random.choice(celebrations)
        
        # If Part 2 (Default Subnet Mask) is correct, prepare to open matrix
        address_class = None
        if part == 'part2':
            address_class = problem['answers']['part1']  # A, B, or C
            response_text += f"<br><br>📊 <strong>Opening the Class {address_class} Subnetting Matrix in a new tab...</strong><br>You can switch between tabs to reference the matrix while working!"
            print(f"[DEBUG] Part 2 correct! Opening matrix for Class {address_class}")
        
        response_data = {
            'response': response_text,
            'is_correct': True,
            'attempt': current_attempt
        }
        
        if address_class:
            response_data['address_class'] = address_class
        
        print(f"[DEBUG] Returning response: {response_data}")
        return jsonify(response_data)
    
    # Generate hint using Claude
    hint_prompt = get_hint_prompt(current_attempt, part, problem)
    
    messages = [{
        "role": "user",
        "content": f"Student's answer: {user_answer}\nAttempt: {current_attempt} of 5\n\n{hint_prompt}"
    }]
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
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
            'response': f"Sorry, I encountered an error: {str(e)}",
            'is_correct': False,
            'attempt': current_attempt
        })

@agent2_bp.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return jsonify({'status': 'success'})

@agent2_bp.route('/matrix/<address_class>')
def show_matrix(address_class):
    """Display the subnetting matrix for a specific class"""
    if address_class not in ['A', 'B', 'C']:
        return "Invalid class", 404
    
    # Matrix templates for each class
    if address_class == 'C':
        return render_template_string(MATRIX_CLASS_C_TEMPLATE)
    elif address_class == 'B':
        return render_template_string(MATRIX_CLASS_B_TEMPLATE)
    else:  # Class A
        return render_template_string(MATRIX_CLASS_A_TEMPLATE)

# Matrix templates for standalone pages
MATRIX_CLASS_C_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>CLASS C Subnetting Matrix</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 { color: #1e3c72; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 20px; font-size: 1.1em; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #1976D2; color: white; padding: 12px; border: 1px solid #ccc; }
        td { padding: 10px; border: 1px solid #ccc; text-align: center; }
        tr:nth-child(even) { background: #f5f5f5; }
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-left: 4px solid #1976D2;
            margin: 20px 0;
        }
        .reminder-box {
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 CLASS C Subnetting Matrix</h1>
        <div class="subtitle">Default Mask: 255.255.255.0 | Available Bits: 8 (4th octet only) | Network: N.N.N.H</div>
        
        <div class="info-box">
            <strong>How to Use This Matrix:</strong>
            <ol style="margin: 10px 0 0 20px;">
                <li>Find the row where <strong>2^s</strong> meets or exceeds your subnet requirement</li>
                <li>Find the row where <strong>2^h - 2</strong> meets or exceeds your usable host requirement</li>
                <li>Both requirements should be on the <strong>SAME ROW</strong></li>
                <li>Validate: Subnet bits + Host bits = 8 for Class C</li>
                <li>Read your custom subnet mask and CAM from that row</li>
            </ol>
        </div>
        
        <table>
            <tr>
                <th>Subnets (2^s)</th>
                <th>Networks</th>
                <th>Subnet Bits (s)</th>
                <th>Host Bits (h)</th>
                <th>Total Addresses (2^h)</th>
                <th>Usable Hosts (2^h - 2)</th>
                <th>Prefix</th>
                <th>Custom Subnet Mask</th>
                <th>CAM Pattern</th>
            </tr>
            <tr><td>2^0</td><td>1</td><td>0</td><td>8</td><td>256</td><td>254</td><td>/24</td><td>255.255.255.0</td><td>N.N.N.hhhhhhhh</td></tr>
            <tr><td>2^1</td><td>2</td><td>1</td><td>7</td><td>128</td><td>126</td><td>/25</td><td>255.255.255.128</td><td>N.N.N.shhhhhh</td></tr>
            <tr><td>2^2</td><td>4</td><td>2</td><td>6</td><td>64</td><td>62</td><td>/26</td><td>255.255.255.192</td><td>N.N.N.sshhhhhh</td></tr>
            <tr><td>2^3</td><td>8</td><td>3</td><td>5</td><td>32</td><td>30</td><td>/27</td><td>255.255.255.224</td><td>N.N.N.ssshhhhh</td></tr>
            <tr><td>2^4</td><td>16</td><td>4</td><td>4</td><td>16</td><td>14</td><td>/28</td><td>255.255.255.240</td><td>N.N.N.sssshhhh</td></tr>
            <tr><td>2^5</td><td>32</td><td>5</td><td>3</td><td>8</td><td>6</td><td>/29</td><td>255.255.255.248</td><td>N.N.N.ssssshh</td></tr>
            <tr><td>2^6</td><td>64</td><td>6</td><td>2</td><td>4</td><td>2</td><td>/30</td><td>255.255.255.252</td><td>N.N.N.sssssshh</td></tr>
            <tr><td>2^7</td><td>128</td><td>7</td><td>1</td><td>2</td><td>0</td><td>/31</td><td>255.255.255.254</td><td>N.N.N.sssssssh</td></tr>
            <tr><td>2^8</td><td>256</td><td>8</td><td>0</td><td>1</td><td>-1</td><td>/32</td><td>255.255.255.255</td><td>N.N.N.ssssssss</td></tr>
        </table>
        
        <div class="reminder-box">
            <strong>🎯 Professor Bodden's Golden Rules:</strong>
            <ul style="margin: 10px 0 0 20px;">
                <li><strong>NEVER forget the minus 2!</strong> First and last addresses are unusable</li>
                <li>Subnet bits + Host bits MUST equal 8 for Class C</li>
                <li>If you can't get exact match, round UP to next power of 2</li>
                <li>255 in mask = Network (can't touch), 0 in mask = Host (where you do math)</li>
                <li>Write things out if you need to see it!</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>Keep this tab open to reference while working on your problem!</p>
        </div>
    </div>
</body>
</html>"""

MATRIX_CLASS_B_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>CLASS B Subnetting Matrix</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 { color: #1e3c72; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 20px; font-size: 1.1em; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9em; }
        th { background: #1976D2; color: white; padding: 10px; border: 1px solid #ccc; }
        td { padding: 8px; border: 1px solid #ccc; text-align: center; }
        tr:nth-child(even) { background: #f5f5f5; }
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-left: 4px solid #1976D2;
            margin: 20px 0;
        }
        .reminder-box {
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 CLASS B Subnetting Matrix</h1>
        <div class="subtitle">Default Mask: 255.255.0.0 | Available Bits: 16 (3rd & 4th octets) | Network: N.N.H.H</div>
        
        <div class="info-box">
            <strong>How to Use This Matrix:</strong>
            <ol style="margin: 10px 0 0 20px;">
                <li>Find the row where <strong>2^s</strong> meets or exceeds your subnet requirement</li>
                <li>Find the row where <strong>2^h - 2</strong> meets or exceeds your usable host requirement</li>
                <li>Both requirements should be on the <strong>SAME ROW</strong></li>
                <li>Validate: Subnet bits + Host bits = 16 for Class B</li>
                <li>Read your custom subnet mask and CAM from that row</li>
            </ol>
        </div>
        
        <table>
            <tr>
                <th>Subnets</th>
                <th>Networks</th>
                <th>Subnet Bits</th>
                <th>Host Bits</th>
                <th>Usable Hosts</th>
                <th>Prefix</th>
                <th>Subnet Mask</th>
                <th>CAM Pattern</th>
            </tr>
            <tr><td>2^0</td><td>1</td><td>0</td><td>16</td><td>65,534</td><td>/16</td><td>255.255.0.0</td><td>N.N.hhhhhhhh.hhhhhhhh</td></tr>
            <tr><td>2^1</td><td>2</td><td>1</td><td>15</td><td>32,766</td><td>/17</td><td>255.255.128.0</td><td>N.N.shhhhhh.hhhhhhhh</td></tr>
            <tr><td>2^2</td><td>4</td><td>2</td><td>14</td><td>16,382</td><td>/18</td><td>255.255.192.0</td><td>N.N.sshhhhhh.hhhhhhhh</td></tr>
            <tr><td>2^3</td><td>8</td><td>3</td><td>13</td><td>8,190</td><td>/19</td><td>255.255.224.0</td><td>N.N.ssshhhhh.hhhhhhhh</td></tr>
            <tr><td>2^4</td><td>16</td><td>4</td><td>12</td><td>4,094</td><td>/20</td><td>255.255.240.0</td><td>N.N.sssshhhh.hhhhhhhh</td></tr>
            <tr><td>2^5</td><td>32</td><td>5</td><td>11</td><td>2,046</td><td>/21</td><td>255.255.248.0</td><td>N.N.ssssshh.hhhhhhhh</td></tr>
            <tr><td>2^6</td><td>64</td><td>6</td><td>10</td><td>1,022</td><td>/22</td><td>255.255.252.0</td><td>N.N.sssssshh.hhhhhhhh</td></tr>
            <tr><td>2^7</td><td>128</td><td>7</td><td>9</td><td>510</td><td>/23</td><td>255.255.254.0</td><td>N.N.sssssssh.hhhhhhhh</td></tr>
            <tr><td>2^8</td><td>256</td><td>8</td><td>8</td><td>254</td><td>/24</td><td>255.255.255.0</td><td>N.N.ssssssss.hhhhhhhh</td></tr>
            <tr><td>2^9</td><td>512</td><td>9</td><td>7</td><td>126</td><td>/25</td><td>255.255.255.128</td><td>N.N.ssssssss.shhhhhh</td></tr>
            <tr><td>2^10</td><td>1,024</td><td>10</td><td>6</td><td>62</td><td>/26</td><td>255.255.255.192</td><td>N.N.ssssssss.sshhhhhh</td></tr>
            <tr><td>2^11</td><td>2,048</td><td>11</td><td>5</td><td>30</td><td>/27</td><td>255.255.255.224</td><td>N.N.ssssssss.ssshhhhh</td></tr>
            <tr><td>2^12</td><td>4,096</td><td>12</td><td>4</td><td>14</td><td>/28</td><td>255.255.255.240</td><td>N.N.ssssssss.sssshhhh</td></tr>
            <tr><td>2^13</td><td>8,192</td><td>13</td><td>3</td><td>6</td><td>/29</td><td>255.255.255.248</td><td>N.N.ssssssss.ssssshh</td></tr>
            <tr><td>2^14</td><td>16,384</td><td>14</td><td>2</td><td>2</td><td>/30</td><td>255.255.255.252</td><td>N.N.ssssssss.sssssshh</td></tr>
            <tr><td>2^15</td><td>32,768</td><td>15</td><td>1</td><td>0</td><td>/31</td><td>255.255.255.254</td><td>N.N.ssssssss.sssssssh</td></tr>
            <tr><td>2^16</td><td>65,536</td><td>16</td><td>0</td><td>-1</td><td>/32</td><td>255.255.255.255</td><td>N.N.ssssssss.ssssssss</td></tr>
        </table>
        
        <div class="reminder-box">
            <strong>🎯 Professor Bodden's Golden Rules:</strong>
            <ul style="margin: 10px 0 0 20px;">
                <li><strong>NEVER forget the minus 2!</strong> First and last addresses are unusable</li>
                <li>Subnet bits + Host bits MUST equal 16 for Class B</li>
                <li>If you can't get exact match, round UP to next power of 2</li>
                <li>255 in mask = Network (can't touch), 0 in mask = Host (where you do math)</li>
                <li>Write things out if you need to see it!</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>Keep this tab open to reference while working on your problem!</p>
        </div>
    </div>
</body>
</html>"""

MATRIX_CLASS_A_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>CLASS A Subnetting Matrix</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 { color: #1e3c72; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 20px; font-size: 1.1em; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.85em; }
        th { background: #1976D2; color: white; padding: 8px; border: 1px solid #ccc; }
        td { padding: 6px; border: 1px solid #ccc; text-align: center; }
        tr:nth-child(even) { background: #f5f5f5; }
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-left: 4px solid #1976D2;
            margin: 20px 0;
        }
        .reminder-box {
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 CLASS A Subnetting Matrix</h1>
        <div class="subtitle">Default Mask: 255.0.0.0 | Available Bits: 24 (2nd, 3rd & 4th octets) | Network: N.H.H.H</div>
        
        <div class="info-box">
            <strong>How to Use This Matrix:</strong>
            <ol style="margin: 10px 0 0 20px;">
                <li>Find the row where <strong>2^s</strong> meets or exceeds your subnet requirement</li>
                <li>Find the row where <strong>2^h - 2</strong> meets or exceeds your usable host requirement</li>
                <li>Both requirements should be on the <strong>SAME ROW</strong></li>
                <li>Validate: Subnet bits + Host bits = 24 for Class A</li>
                <li>Read your custom subnet mask and CAM from that row</li>
            </ol>
        </div>
        
        <table>
            <tr>
                <th>Subnets</th>
                <th>Networks</th>
                <th>Subnet Bits</th>
                <th>Host Bits</th>
                <th>Usable Hosts</th>
                <th>Prefix</th>
                <th>Subnet Mask</th>
            </tr>
            <tr><td>2^0</td><td>1</td><td>0</td><td>24</td><td>16,777,214</td><td>/8</td><td>255.0.0.0</td></tr>
            <tr><td>2^1</td><td>2</td><td>1</td><td>23</td><td>8,388,606</td><td>/9</td><td>255.128.0.0</td></tr>
            <tr><td>2^2</td><td>4</td><td>2</td><td>22</td><td>4,194,302</td><td>/10</td><td>255.192.0.0</td></tr>
            <tr><td>2^3</td><td>8</td><td>3</td><td>21</td><td>2,097,150</td><td>/11</td><td>255.224.0.0</td></tr>
            <tr><td>2^4</td><td>16</td><td>4</td><td>20</td><td>1,048,574</td><td>/12</td><td>255.240.0.0</td></tr>
            <tr><td>2^5</td><td>32</td><td>5</td><td>19</td><td>524,286</td><td>/13</td><td>255.248.0.0</td></tr>
            <tr><td>2^6</td><td>64</td><td>6</td><td>18</td><td>262,142</td><td>/14</td><td>255.252.0.0</td></tr>
            <tr><td>2^7</td><td>128</td><td>7</td><td>17</td><td>131,070</td><td>/15</td><td>255.254.0.0</td></tr>
            <tr><td>2^8</td><td>256</td><td>8</td><td>16</td><td>65,534</td><td>/16</td><td>255.255.0.0</td></tr>
            <tr><td>2^9</td><td>512</td><td>9</td><td>15</td><td>32,766</td><td>/17</td><td>255.255.128.0</td></tr>
            <tr><td>2^10</td><td>1,024</td><td>10</td><td>14</td><td>16,382</td><td>/18</td><td>255.255.192.0</td></tr>
            <tr><td>2^11</td><td>2,048</td><td>11</td><td>13</td><td>8,190</td><td>/19</td><td>255.255.224.0</td></tr>
            <tr><td>2^12</td><td>4,096</td><td>12</td><td>12</td><td>4,094</td><td>/20</td><td>255.255.240.0</td></tr>
            <tr><td>2^13</td><td>8,192</td><td>13</td><td>11</td><td>2,046</td><td>/21</td><td>255.255.248.0</td></tr>
            <tr><td>2^14</td><td>16,384</td><td>14</td><td>10</td><td>1,022</td><td>/22</td><td>255.255.252.0</td></tr>
            <tr><td>2^15</td><td>32,768</td><td>15</td><td>9</td><td>510</td><td>/23</td><td>255.255.254.0</td></tr>
            <tr><td>2^16</td><td>65,536</td><td>16</td><td>8</td><td>254</td><td>/24</td><td>255.255.255.0</td></tr>
            <tr><td>2^17</td><td>131,072</td><td>17</td><td>7</td><td>126</td><td>/25</td><td>255.255.255.128</td></tr>
            <tr><td>2^18</td><td>262,144</td><td>18</td><td>6</td><td>62</td><td>/26</td><td>255.255.255.192</td></tr>
            <tr><td>2^19</td><td>524,288</td><td>19</td><td>5</td><td>30</td><td>/27</td><td>255.255.255.224</td></tr>
            <tr><td>2^20</td><td>1,048,576</td><td>20</td><td>4</td><td>14</td><td>/28</td><td>255.255.255.240</td></tr>
            <tr><td>2^21</td><td>2,097,152</td><td>21</td><td>3</td><td>6</td><td>/29</td><td>255.255.255.248</td></tr>
            <tr><td>2^22</td><td>4,194,304</td><td>22</td><td>2</td><td>2</td><td>/30</td><td>255.255.255.252</td></tr>
            <tr><td>2^23</td><td>8,388,608</td><td>23</td><td>1</td><td>0</td><td>/31</td><td>255.255.255.254</td></tr>
            <tr><td>2^24</td><td>16,777,216</td><td>24</td><td>0</td><td>-1</td><td>/32</td><td>255.255.255.255</td></tr>
        </table>
        
        <div class="reminder-box">
            <strong>🎯 Professor Bodden's Golden Rules:</strong>
            <ul style="margin: 10px 0 0 20px;">
                <li><strong>NEVER forget the minus 2!</strong> First and last addresses are unusable</li>
                <li>Subnet bits + Host bits MUST equal 24 for Class A</li>
                <li>If you can't get exact match, round UP to next power of 2</li>
                <li>255 in mask = Network (can't touch), 0 in mask = Host (where you do math)</li>
                <li>Write things out if you need to see it!</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>Keep this tab open to reference while working on your problem!</p>
        </div>
    </div>
</body>
</html>"""

