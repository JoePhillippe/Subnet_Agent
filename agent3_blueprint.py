"""
Subnet Range Tutor Agent - Mentoring students through subnet range calculations
6 problems with 12 parts each - Progressive 5-level mentoring system
"""

from flask import Blueprint, Flask, render_template_string, request, jsonify, session, redirect, url_for
from functools import wraps
from anthropic import Anthropic
import os
import secrets

agent3_bp = Blueprint("agent3", __name__)

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# The 6 Subnet Range Problems with all 12 parts
PROBLEMS = {
    1: {
        "name": "Problem 1",
        "subnets_needed": 3,
        "hosts_needed": 57,
        "network_address": "210.220.3.0",
        "questions": {
            "q9": "What is the 1st subnet range?",
            "q10": "What is the subnet ID/Number for the 2nd subnet?",
            "q11": "What is the broadcast address for the 3rd subnet?",
            "q12": "What is the assignable addresses for the 4th subnet?"
        },
        "answers": {
            "part1": "C",
            "part2": "255.255.255.0",
            "part3": "2",
            "part4": "6",
            "part5": "4",
            "part6": "64",
            "part7": "62",
            "part8": "255.255.255.192",
            "part9": "210.220.3.0 to 210.220.3.63",
            "part10": "210.220.3.64",
            "part11": "210.220.3.191",
            "part12": "210.220.3.193 to 210.220.3.254"
        }
    },
    2: {
        "name": "Problem 2",
        "subnets_needed": 28,
        "hosts_needed": 6,
        "network_address": "196.23.45.0",
        "questions": {
            "q9": "What is the 5th subnet range?",
            "q10": "What is the subnet ID/Number for the 2nd subnet?",
            "q11": "What is the broadcast address for the 9th subnet?",
            "q12": "What is the assignable addresses for the 11th subnet?"
        },
        "answers": {
            "part1": "C",
            "part2": "255.255.255.0",
            "part3": "5",
            "part4": "3",
            "part5": "32",
            "part6": "8",
            "part7": "6",
            "part8": "255.255.255.248",
            "part9": "196.23.45.32 to 196.23.45.39",
            "part10": "196.23.45.8",
            "part11": "196.23.45.71",
            "part12": "196.23.45.81 to 196.23.45.86"
        }
    },
    3: {
        "name": "Problem 3",
        "subnets_needed": 900,
        "hosts_needed": 60,
        "network_address": "172.33.0.0",
        "questions": {
            "q9": "What is the 4th subnet range?",
            "q10": "What is the subnet ID/Number for the 9th subnet?",
            "q11": "What is the broadcast address for the 11th subnet?",
            "q12": "What is the assignable addresses for the 14th subnet?"
        },
        "answers": {
            "part1": "B",
            "part2": "255.255.0.0",
            "part3": "10",
            "part4": "6",
            "part5": "1024",
            "part6": "64",
            "part7": "62",
            "part8": "255.255.255.192",
            "part9": "172.33.0.192 to 172.33.0.255",
            "part10": "172.33.2.0",
            "part11": "172.33.2.191",
            "part12": "172.33.3.65 to 172.33.3.126"
        }
    },
    4: {
        "name": "Problem 4",
        "subnets_needed": 16,
        "hosts_needed": 4000,
        "network_address": "188.16.0.0",
        "questions": {
            "q9": "What is the 3rd subnet range?",
            "q10": "What is the subnet ID/Number for the 7th subnet?",
            "q11": "What is the broadcast address for the 10th subnet?",
            "q12": "What is the assignable addresses for the 13th subnet?"
        },
        "answers": {
            "part1": "B",
            "part2": "255.255.0.0",
            "part3": "4",
            "part4": "12",
            "part5": "16",
            "part6": "4096",
            "part7": "4094",
            "part8": "255.255.240.0",
            "part9": "188.16.32.0 to 188.16.47.255",
            "part10": "188.16.96.0",
            "part11": "188.16.159.255",
            "part12": "188.16.192.1 to 188.16.207.254"
        }
    },
    5: {
        "name": "Problem 5",
        "subnets_needed": 130000,
        "hosts_needed": 126,
        "network_address": "112.0.0.0",
        "questions": {
            "q9": "What is the 7th subnet range?",
            "q10": "What is the subnet ID/Number for the 4th subnet?",
            "q11": "What is the broadcast address for the 11th subnet?",
            "q12": "What is the assignable addresses for the 13th subnet?"
        },
        "answers": {
            "part1": "A",
            "part2": "255.0.0.0",
            "part3": "17",
            "part4": "7",
            "part5": "131072",
            "part6": "128",
            "part7": "126",
            "part8": "255.255.255.128",
            "part9": "112.0.3.0 to 112.0.3.127",
            "part10": "112.0.1.128",
            "part11": "112.0.5.127",
            "part12": "112.0.6.1 to 112.0.6.126"
        }
    },
    6: {
        "name": "Problem 6",
        "subnets_needed": 30,
        "hosts_needed": 500000,
        "network_address": "10.0.0.0",
        "questions": {
            "q9": "What is the 6th subnet range?",
            "q10": "What is the subnet ID/Number for the 3rd subnet?",
            "q11": "What is the broadcast address for the 10th subnet?",
            "q12": "What is the assignable addresses for the 14th subnet?"
        },
        "answers": {
            "part1": "A",
            "part2": "255.0.0.0",
            "part3": "5",
            "part4": "19",
            "part5": "32",
            "part6": "524288",
            "part7": "524286",
            "part8": "255.248.0.0",
            "part9": "10.40.0.0 to 10.47.255.255",
            "part10": "10.16.0.0",
            "part11": "10.79.255.255",
            "part12": "10.104.0.1 to 10.111.255.254"
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
    "part9": "",  # Varies by problem
    "part10": "",  # Varies by problem
    "part11": "",  # Varies by problem
    "part12": ""  # Varies by problem
}

# System Prompt - 5-Level Mentoring System
SYSTEM_PROMPT = """You are a patient and encouraging subnet range tutor helping students master subnet calculations and range determination. Your goal is to guide students to discover answers themselves through a 5-level progressive mentoring system.

🎯 5-LEVEL MENTORING SYSTEM (CRITICAL):

LEVEL 1 - GENTLE NUDGE (First incorrect attempt):
- Acknowledge their effort positively
- Ask a clarifying question about their approach
- Point them toward the relevant concept WITHOUT giving formulas
- Example: "Good try! Let me ask - when you looked at the subnet requirement, did you consider rounding up to the nearest power of 2?"

LEVEL 2 - CONCEPTUAL GUIDANCE (Second incorrect attempt):
- Explain the relevant concept more directly
- Provide the general approach or methodology
- Still NO specific numbers or formulas
- Example: "Remember, we need to find the smallest power of 2 that meets or exceeds our requirement. For subnets, we use 2^s where s is the number of subnet bits."

LEVEL 3 - FORMULA WITH CONTEXT (Third incorrect attempt):
- Provide the specific formula or calculation method
- Give context for how to apply it to THEIR problem
- Still don't calculate the final answer
- Example: "For this problem, we need at least 28 subnets. Find the smallest power: 2^? ≥ 28. Check your powers of 2: 2^4=16 (too small), 2^5=32 (this works!)"

LEVEL 4 - WORKED EXAMPLE WITH BLANKS (Fourth incorrect attempt):
- Show the step-by-step calculation with most numbers filled in
- Leave one or two key values for them to determine
- Example: "Let's work through it: We need ≥28 subnets → 2^5 = 32 subnets → 5 subnet bits. Now YOU calculate: How many host bits remain? (Remember: subnet bits + host bits = total available bits for the class)"

LEVEL 5 - COMPLETE ANSWER WITH FULL EXPLANATION (Fifth incorrect attempt):
- Provide the complete correct answer
- Explain EVERY step of how you got there
- Show the logic and calculations clearly
- Encourage them to try the next part with this understanding
- Example: "The answer is 5 subnet bits. Here's the complete solution: We need at least 28 subnets. Looking at powers of 2: 2^5 = 32 subnets (the smallest power that meets our need). This means we borrow 5 bits for subnetting. Since this is a Class C network with 8 available bits in the host portion, and we use 5 for subnets, we have 8 - 5 = 3 bits left for hosts."

CRITICAL MENTORING RULES:
1. NEVER jump ahead in levels - always start at Level 1 for first wrong answer
2. Track attempt count per part - reset to Level 1 when moving to a new part
3. Be encouraging at EVERY level - mistakes are learning opportunities
4. For range calculations (parts 9-12):
   - Level 1-2: Guide them to understand block size and counting
   - Level 3-4: Show how to calculate the specific subnet they need
   - Level 5: Complete calculation with subnet ID, broadcast, and usable range
5. Always reference their specific problem details (subnet count, host count, network address)

SUBNET RANGE CALCULATION METHODOLOGY:

For determining specific subnet ranges:
1. Calculate block size: 256 - last non-zero octet of custom mask
2. For Class C: All changes happen in 4th octet
3. For Class B: Subnets increment in 3rd octet, then 4th octet
4. For Class A: Subnets increment in 2nd, 3rd, and 4th octets

Subnet Components:
- Subnet ID: First address in range (network address of that subnet)
- Broadcast Address: Last address in range
- Usable Addresses: From (Subnet ID + 1) to (Broadcast - 1)

FORMULA REMINDERS:
- Subnets: 2^s (where s = subnet bits)
- Total Addresses per subnet: 2^h (where h = host bits)
- Usable Addresses: 2^h - 2 (minus 2 for network and broadcast)
- Block Size: 256 - (value in the subnet mask octet that's changing)

Be enthusiastic, patient, and remember: the goal is understanding, not just correct answers!"""

def call_claude(messages):
    """Call Claude API with conversation history"""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Error calling Claude API: {str(e)}"

@agent3_bp.route('/')
def home():
    """Main page - problem selection"""
    return render_template_string(INDEX_TEMPLATE)

@agent3_bp.route('/problem/<int:problem_id>')
def problem(problem_id):
    """Individual problem page with chat interface"""
    if problem_id not in PROBLEMS:
        return "Problem not found", 404
    
    # Initialize session for this problem
    session.clear()  # Clear any old data
    session['problem_id'] = problem_id
    session['current_part'] = 'part1'
    session['attempts'] = {}
    session['conversation'] = []
    session.modified = True
    
    print(f"Session initialized for problem {problem_id}")
    print(f"Session data: {dict(session)}")
    
    problem_data = PROBLEMS[problem_id]
    return render_template_string(PROBLEM_TEMPLATE, 
                                 problem=problem_data, 
                                 problem_id=problem_id)

@agent3_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    print("=" * 50)
    print("CHAT ENDPOINT CALLED")
    print("=" * 50)
    
    try:
        data = request.json
        print(f"Request data: {data}")
        
        user_message = data.get('message', '').strip()
        print(f"User message: {user_message}")
        
        if not user_message:
            print("Empty message received")
            return jsonify({'error': 'Empty message'}), 400
        
        problem_id = session.get('problem_id')
        print(f"Problem ID from session: {problem_id}")
        
        current_part = session.get('current_part', 'part1')
        print(f"Current part: {current_part}")
        
        if problem_id not in PROBLEMS:
            print(f"Invalid problem ID: {problem_id}")
            return jsonify({'error': 'Invalid problem'}), 400
        
        problem_data = PROBLEMS[problem_id]
        
        # Initialize attempts for current part if not exists
        if 'attempts' not in session:
            session['attempts'] = {}
        if current_part not in session['attempts']:
            session['attempts'][current_part] = 0
        
        # Get correct answer for current part
        correct_answer = problem_data['answers'][current_part]
        print(f"Correct answer: {correct_answer}")
        
        # Normalize answers for comparison (remove spaces, commas, make lowercase)
        def normalize_answer(ans):
            return ans.lower().strip().replace(' ', '').replace(',', '').replace('-', '')
        
        user_answer_normalized = normalize_answer(user_message)
        correct_answer_normalized = normalize_answer(correct_answer)
        
        print(f"User answer normalized: {user_answer_normalized}")
        print(f"Correct answer normalized: {correct_answer_normalized}")
        
        # Determine if it's an answer attempt
        is_answer_attempt = False
        is_correct = False
        
        # Check various matching scenarios
        # 1. Exact match after normalization
        if user_answer_normalized == correct_answer_normalized:
            is_answer_attempt = True
            is_correct = True
            print("Match: Exact normalized match")
        # 2. Correct answer is contained in user's answer
        elif correct_answer_normalized in user_answer_normalized:
            is_answer_attempt = True
            is_correct = True
            print("Match: Correct answer contained in user answer")
        # 3. User answer is contained in correct answer (for single letters/numbers)
        elif len(correct_answer_normalized) <= 3 and user_answer_normalized == correct_answer_normalized:
            is_answer_attempt = True
            is_correct = True
            print("Match: Short answer exact match")
        # 4. For ranges, check if both endpoints match
        elif 'to' in correct_answer.lower():
            # Extract the two IPs/numbers from both answers
            correct_parts = [p.strip() for p in correct_answer.lower().split('to')]
            if 'to' in user_message.lower():
                user_parts = [p.strip() for p in user_message.lower().split('to')]
                # Normalize and compare both parts
                if len(correct_parts) == 2 and len(user_parts) == 2:
                    part1_match = normalize_answer(user_parts[0]) == normalize_answer(correct_parts[0])
                    part2_match = normalize_answer(user_parts[1]) == normalize_answer(correct_parts[1])
                    if part1_match and part2_match:
                        is_answer_attempt = True
                        is_correct = True
                        print("Match: Range answer match")
                    else:
                        is_answer_attempt = True
                        print(f"No match: Range mismatch - part1:{part1_match}, part2:{part2_match}")
            else:
                # User didn't provide range format
                is_answer_attempt = len(user_message.split()) <= 10  # Assume it's an attempt if reasonably short
        # 5. Check if message looks like an answer (short, no question words)
        elif len(user_message.split()) <= 8 and '?' not in user_message and not any(q in user_message.lower() for q in ['what', 'how', 'why', 'when', 'where', 'can', 'could', 'help']):
            is_answer_attempt = True
            print("Detected as answer attempt (short message, no question words)")
        
        print(f"Is answer attempt: {is_answer_attempt}")
        print(f"Is correct: {is_correct}")
        
        # Build context for Claude
        part_description = PART_DESCRIPTIONS.get(current_part, '')
        if current_part in ['part9', 'part10', 'part11', 'part12']:
            part_description = problem_data['questions'].get(current_part.replace('part', 'q'), '')
        
        # Increment attempts if wrong answer
        if is_answer_attempt and not is_correct:
            session['attempts'][current_part] = session['attempts'].get(current_part, 0) + 1
            session.modified = True
        
        current_attempts = session['attempts'][current_part]
        print(f"Current attempts: {current_attempts}")
        
        # Build context message for Claude
        if is_correct:
            context_message = f"""
GREAT NEWS! The student answered correctly!

CURRENT PROBLEM: {problem_data['name']}
Subnets Needed: {problem_data['subnets_needed']}
Hosts Needed: {problem_data['hosts_needed']}
Network Address: {problem_data['network_address']}

CURRENT PART: {current_part.upper().replace('PART', 'Part ')} - {part_description}
STUDENT'S ANSWER: {user_message}
CORRECT ANSWER: {correct_answer}

The student got it RIGHT! Please:
1. Congratulate them enthusiastically! 🎉
2. Briefly explain why this answer is correct
3. Ask if they're ready to move to the next part (they can say "next" or "yes")
"""
        else:
            context_message = f"""
CURRENT PROBLEM: {problem_data['name']}
Subnets Needed: {problem_data['subnets_needed']}
Hosts Needed: {problem_data['hosts_needed']}
Network Address: {problem_data['network_address']}

CURRENT PART: {current_part.upper().replace('PART', 'Part ')} - {part_description}
{f"Specific Question: {problem_data['questions'].get(current_part.replace('part', 'q'), '')}" if current_part in ['part9', 'part10', 'part11', 'part12'] else ''}

STUDENT'S ATTEMPT COUNT FOR THIS PART: {current_attempts}
CORRECT ANSWER (for your reference): {correct_answer}

The student says: {user_message}

IMPORTANT INSTRUCTIONS:
{"- This appears to be an INCORRECT answer attempt. Provide Level " + str(min(current_attempts, 5)) + " mentoring." if is_answer_attempt else "- This appears to be a QUESTION (not an answer attempt). Provide helpful guidance without revealing the answer."}

Remember the 5-LEVEL MENTORING SYSTEM:
- Level 1: Gentle nudge with a clarifying question
- Level 2: Conceptual guidance and methodology  
- Level 3: Formula with context for their specific problem
- Level 4: Worked example with blanks to fill
- Level 5: Complete answer with full step-by-step explanation

{"Current mentoring level: " + str(min(current_attempts, 5)) if is_answer_attempt else "Answer their question helpfully"}
"""
        
        # Add to conversation history
        if 'conversation' not in session:
            session['conversation'] = []
        
        session['conversation'].append({
            'role': 'user',
            'content': context_message
        })
        
        print("Calling Claude API...")
        # Get Claude's response
        claude_response = call_claude(session['conversation'])
        print(f"Claude response: {claude_response[:100]}...")
        
        # Add Claude's response to history
        session['conversation'].append({
            'role': 'assistant',
            'content': claude_response
        })
        
        session.modified = True
        
        response_data = {
            'response': claude_response,
            'current_part': current_part,
            'attempts': current_attempts,
            'is_correct': is_correct
        }
        
        print(f"Sending response: {response_data}")
        print("=" * 50)
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"ERROR in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@agent3_bp.route('/next_part', methods=['POST'])
def next_part():
    """Move to next part"""
    current_part = session.get('current_part', 'part1')
    part_num = int(current_part.replace('part', ''))
    
    if part_num < 12:
        next_part_num = part_num + 1
        session['current_part'] = f'part{next_part_num}'
        session.modified = True
        return jsonify({'success': True, 'next_part': session['current_part']})
    else:
        return jsonify({'success': False, 'message': 'This is the last part!'})

@agent3_bp.route('/reset')
def reset():
    """Reset session"""
    session.clear()
    return jsonify({'success': True})

# HTML Templates
INDEX_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Subnet Range Tutor</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        }
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            text-align: center;
        }
        h1 { color: #1e3c72; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 1.1em; }
        .problems-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .problem-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        .problem-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }
        .problem-number {
            font-size: 2em;
            color: #1976D2;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .problem-details {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .problem-details div {
            margin: 5px 0;
            color: #333;
        }
        .start-button {
            background: #1976D2;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1.1em;
            cursor: pointer;
            width: 100%;
            margin-top: 15px;
            transition: background 0.3s;
        }
        .start-button:hover {
            background: #1565C0;
        }
        .info-box {
            background: #e3f2fd;
            padding: 20px;
            border-left: 4px solid #1976D2;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Subnet Range Tutor</h1>
            <div class="subtitle">Master subnet range calculations with AI-powered mentoring</div>
            <div class="info-box" style="text-align: left; margin-top: 20px;">
                <strong>📚 What You'll Learn:</strong>
                <ul style="margin: 10px 0 0 20px;">
                    <li>Calculate subnet ranges for Class A, B, and C networks</li>
                    <li>Determine subnet IDs, broadcast addresses, and usable ranges</li>
                    <li>Master the 12-part subnet analysis process</li>
                    <li>Get progressive hints through 5 levels of mentoring</li>
                </ul>
            </div>
        </div>

        <div class="problems-grid">
            <div class="problem-card" onclick="location.href='/problem/1'">
                <div class="problem-number">Problem 1</div>
                <div class="problem-details">
                    <div><strong>Network:</strong> 210.220.3.0</div>
                    <div><strong>Subnets Needed:</strong> 3</div>
                    <div><strong>Hosts Needed:</strong> 57</div>
                </div>
                <button class="start-button">Start Problem 1</button>
            </div>

            <div class="problem-card" onclick="location.href='/problem/2'">
                <div class="problem-number">Problem 2</div>
                <div class="problem-details">
                    <div><strong>Network:</strong> 196.23.45.0</div>
                    <div><strong>Subnets Needed:</strong> 28</div>
                    <div><strong>Hosts Needed:</strong> 6</div>
                </div>
                <button class="start-button">Start Problem 2</button>
            </div>

            <div class="problem-card" onclick="location.href='/problem/3'">
                <div class="problem-number">Problem 3</div>
                <div class="problem-details">
                    <div><strong>Network:</strong> 172.33.0.0</div>
                    <div><strong>Subnets Needed:</strong> 900</div>
                    <div><strong>Hosts Needed:</strong> 60</div>
                </div>
                <button class="start-button">Start Problem 3</button>
            </div>

            <div class="problem-card" onclick="location.href='/problem/4'">
                <div class="problem-number">Problem 4</div>
                <div class="problem-details">
                    <div><strong>Network:</strong> 188.16.0.0</div>
                    <div><strong>Subnets Needed:</strong> 16</div>
                    <div><strong>Hosts Needed:</strong> 4000</div>
                </div>
                <button class="start-button">Start Problem 4</button>
            </div>

            <div class="problem-card" onclick="location.href='/problem/5'">
                <div class="problem-number">Problem 5</div>
                <div class="problem-details">
                    <div><strong>Network:</strong> 112.0.0.0</div>
                    <div><strong>Subnets Needed:</strong> 130,000</div>
                    <div><strong>Hosts Needed:</strong> 126</div>
                </div>
                <button class="start-button">Start Problem 5</button>
            </div>

            <div class="problem-card" onclick="location.href='/problem/6'">
                <div class="problem-number">Problem 6</div>
                <div class="problem-details">
                    <div><strong>Network:</strong> 10.0.0.0</div>
                    <div><strong>Subnets Needed:</strong> 30</div>
                    <div><strong>Hosts Needed:</strong> 500,000</div>
                </div>
                <button class="start-button">Start Problem 6</button>
            </div>
        </div>
    </div>
</body>
</html>"""

PROBLEM_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>{{ problem.name }} - Subnet Range Tutor</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 20px;
        }
        .sidebar {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            height: fit-content;
            position: sticky;
            top: 20px;
        }
        .main-content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        h1 { color: #1e3c72; margin-bottom: 20px; }
        h2 { color: #1976D2; margin-bottom: 15px; font-size: 1.3em; }
        .problem-info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #1976D2;
            margin-bottom: 20px;
        }
        .problem-info div {
            margin: 8px 0;
            color: #333;
        }
        .parts-list {
            list-style: none;
        }
        .part-item {
            background: #f5f5f5;
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 4px solid #ccc;
            cursor: pointer;
            transition: all 0.3s;
        }
        .part-item.active {
            background: #e3f2fd;
            border-left: 4px solid #1976D2;
            font-weight: bold;
        }
        .part-item.completed {
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
        }
        .chat-container {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            height: 500px;
            display: flex;
            flex-direction: column;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
        }
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
            max-width: 80%;
        }
        .user-message {
            background: #1976D2;
            color: white;
            margin-left: auto;
        }
        .assistant-message {
            background: white;
            border: 1px solid #e0e0e0;
        }
        .chat-input-container {
            padding: 15px;
            border-top: 1px solid #e0e0e0;
            background: white;
            display: flex;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 1em;
        }
        .send-button {
            background: #1976D2;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s;
        }
        .send-button:hover {
            background: #1565C0;
        }
        .attempt-counter {
            background: #fff3cd;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
            text-align: center;
            border-left: 4px solid #ffc107;
        }
        .back-button {
            background: #666;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 15px;
        }
        .back-button:hover {
            background: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <a href="/" class="back-button">← Back to Problems</a>
            
            <h2>{{ problem.name }}</h2>
            
            <div class="problem-info">
                <div><strong>Network Address:</strong> {{ problem.network_address }}</div>
                <div><strong>Subnets Needed:</strong> {{ problem.subnets_needed }}</div>
                <div><strong>Hosts Needed:</strong> {{ problem.hosts_needed }}</div>
            </div>

            <h2>12 Parts to Complete</h2>
            <ul class="parts-list" id="partsList">
                <li class="part-item active" data-part="part1">Part 1: Address Class</li>
                <li class="part-item" data-part="part2">Part 2: Default Subnet Mask</li>
                <li class="part-item" data-part="part3">Part 3: Subnet Bits</li>
                <li class="part-item" data-part="part4">Part 4: Host Bits</li>
                <li class="part-item" data-part="part5">Part 5: Total Subnets</li>
                <li class="part-item" data-part="part6">Part 6: Total Addresses</li>
                <li class="part-item" data-part="part7">Part 7: Usable Addresses</li>
                <li class="part-item" data-part="part8">Part 8: Custom Subnet Mask</li>
                <li class="part-item" data-part="part9">Part 9: {{ problem.questions.q9 }}</li>
                <li class="part-item" data-part="part10">Part 10: {{ problem.questions.q10 }}</li>
                <li class="part-item" data-part="part11">Part 11: {{ problem.questions.q11 }}</li>
                <li class="part-item" data-part="part12">Part 12: {{ problem.questions.q12 }}</li>
            </ul>
        </div>

        <div class="main-content">
            <h1>🎯 AI Tutor - Progressive Mentoring</h1>
            
            <div class="attempt-counter" id="attemptCounter">
                Current Part: <strong id="currentPartDisplay">Part 1</strong> | 
                Attempts: <strong id="attemptCount">0</strong>/5
            </div>

            <div class="problem-info" id="currentQuestionBox" style="background: #fff3cd; border-left: 4px solid #ffc107;">
                <strong>📝 Current Question:</strong><br>
                <div id="currentQuestionText" style="font-size: 1.1em; margin-top: 10px;">
                    Part 1: Address Class
                </div>
            </div>

            <div class="problem-info">
                <strong>💡 How it Works:</strong>
                <ul style="margin: 10px 0 0 20px;">
                    <li>Work through all 12 parts in order</li>
                    <li>Get progressive hints if you need help (5 levels)</li>
                    <li>Level 5 gives you the complete answer with full explanation</li>
                    <li>Ask questions anytime - the AI tutor is here to help!</li>
                </ul>
            </div>

            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message assistant-message">
                        <strong>🤖 AI Tutor:</strong><br><br>
                        Welcome! Let's work through <strong>{{ problem.name }}</strong> together! 
                        We have <strong>12 parts</strong> to complete.<br><br>
                        
                        <strong>Problem Setup:</strong><br>
                        • Network Address: {{ problem.network_address }}<br>
                        • Subnets Needed: {{ problem.subnets_needed }}<br>
                        • Hosts Needed: {{ problem.hosts_needed }}<br><br>
                        
                        We're starting with <strong>Part 1: Address Class</strong><br><br>
                        
                        Take your time, and remember: I'm here to help! If you get stuck, I'll provide 
                        progressive hints. Just submit your answer or ask me a question to get started! 🚀
                    </div>
                </div>
                <div class="chat-input-container">
                    <input type="text" id="chatInput" class="chat-input" 
                           placeholder="Type your answer or ask a question..." 
                           onkeypress="if(event.key==='Enter') sendMessage()">
                    <button class="send-button" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentPart = 'part1';
        let attemptCount = 0;
        let isWaitingForNext = false;

        // Part descriptions for display
        const partDescriptions = {
            'part1': 'Address Class',
            'part2': 'Default Subnet Mask',
            'part3': 'Number of subnet (borrowed) bits',
            'part4': 'Number of host bits',
            'part5': 'Total number of subnets',
            'part6': 'Total number of addresses',
            'part7': 'Number of usable addresses',
            'part8': 'Custom subnet mask',
            'part9': '{{ problem.questions.q9 }}',
            'part10': '{{ problem.questions.q10 }}',
            'part11': '{{ problem.questions.q11 }}',
            'part12': '{{ problem.questions.q12 }}'
        };

        function sendMessage() {
            console.log('sendMessage called');
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            console.log('Message:', message);
            
            if (!message) {
                console.log('Empty message, returning');
                return;
            }
            
            // Check if user wants to move to next part
            if (isWaitingForNext && (message.toLowerCase() === 'next' || message.toLowerCase() === 'yes' || message.toLowerCase() === 'y')) {
                moveToNextPart();
                input.value = '';
                return;
            }
            
            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';
            
            console.log('Sending fetch request to /chat');
            
            // Send to server
            fetch('chat', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => {
                console.log('Response received:', response);
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log('Data:', data);
                addMessage(data.response, 'assistant');
                attemptCount = data.attempts;
                updateAttemptCounter();
                
                // If answer is correct, prepare for next part
                if (data.is_correct) {
                    isWaitingForNext = true;
                    addNextPartButton();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Error: ' + error.message, 'assistant');
            });
        }

        function addNextPartButton() {
            const messagesDiv = document.getElementById('chatMessages');
            const buttonDiv = document.createElement('div');
            buttonDiv.className = 'message assistant-message';
            buttonDiv.innerHTML = '<button onclick="moveToNextPart()" style="background: #4CAF50; color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-size: 1em; width: 100%;">✅ Move to Next Part</button>';
            messagesDiv.appendChild(buttonDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function moveToNextPart() {
            fetch('/next_part', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentPart = data.next_part;
                    attemptCount = 0;
                    isWaitingForNext = false;
                    updateCurrentPart(currentPart);
                    updateAttemptCounter();
                    
                    // Mark previous part as completed
                    const partNum = parseInt(currentPart.replace('part', ''));
                    if (partNum > 1) {
                        const prevPart = 'part' + (partNum - 1);
                        document.querySelector('[data-part="' + prevPart + '"]').classList.add('completed');
                    }
                    
                    // Update the question display
                    updateQuestionDisplay(currentPart);
                    
                    // Add message showing the new question
                    const partDescription = partDescriptions[currentPart];
                    addMessage('Great! Moving on to Part ' + partNum + ': ' + partDescription + '. What is your answer?', 'assistant');
                } else {
                    addMessage('🎉 Congratulations! You completed all 12 parts!', 'assistant');
                }
            });
        }

        function addMessage(text, sender) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + sender + '-message';
            
            if (sender === 'assistant') {
                messageDiv.innerHTML = '<strong>🤖 AI Tutor:</strong><br><br>' + text;
            } else {
                messageDiv.innerHTML = '<strong>You:</strong><br><br>' + text;
            }
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function updateAttemptCounter() {
            document.getElementById('attemptCount').textContent = attemptCount;
        }

        function updateQuestionDisplay(part) {
            const partNum = part.replace('part', '');
            const description = partDescriptions[part];
            document.getElementById('currentQuestionText').innerHTML = '<strong>Part ' + partNum + ':</strong> ' + description;
        }

        function updateCurrentPart(part) {
            currentPart = part;
            const partNum = part.replace('part', '');
            document.getElementById('currentPartDisplay').textContent = 'Part ' + partNum;
            
            // Update the question display
            updateQuestionDisplay(part);
            
            // Update sidebar
            document.querySelectorAll('.part-item').forEach(item => {
                item.classList.remove('active');
                if (item.dataset.part === part) {
                    item.classList.add('active');
                }
            });
        }

        // Allow clicking on parts in sidebar (for reference only, doesn't change current part)
        document.querySelectorAll('.part-item').forEach(item => {
            item.addEventListener('click', function() {
                const part = this.dataset.part;
                addMessage('Can you help me with ' + this.textContent + '?', 'user');
                
                fetch('chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: 'Can you help me with ' + this.textContent + '?' })
                })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.response, 'assistant');
                });
            });
        });
    </script>
</body>
</html>"""

