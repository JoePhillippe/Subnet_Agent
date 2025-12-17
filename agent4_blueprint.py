"""
VLSM Tutor - Final Version for Spyder IDE
Complete sequential VLSM tutoring system with visual diagrams

Features:
- 3 problems with visual network diagrams
- 15 sequential parts (4 + 5 + 6)
- 5-level progressive hints per part
- Continue button (student controlled advancement)
- Answer validation and feedback

Setup in Spyder:
1. pip install flask anthropic --break-system-packages
2. Set API key: os.environ['ANTHROPIC_API_KEY'] = 'your-key'
3. Press F5 to run
4. Open browser: http://localhost:5004
"""

from flask import Blueprint, Flask, render_template_string, request, jsonify, session, redirect, url_for
from functools import wraps
from anthropic import Anthropic
import os
import secrets

agent4_bp = Blueprint("agent4", __name__)


# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# VLSM Problems with Visual Diagrams
PROBLEMS = {
    1: {
        "name": "VLSM Problem 1 - Small Business Network",
        "network": "200.75.80.0",
        "network_class": "C",
        "diagram": """<div style="background: white; padding: 20px; border: 2px solid #667eea; border-radius: 10px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    ROUTER
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 15px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 12px; background: #e3f2fd; border: 2px solid #2196F3; border-radius: 8px; font-weight: bold;">
                        <div style="color: #1976D2;">🖥️ R&D Switch</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">100 hosts needed</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 12px; background: #f3e5f5; border: 2px solid #9c27b0; border-radius: 8px; font-weight: bold;">
                        <div style="color: #7b1fa2;">🖨️ Printing Switch</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">50 hosts needed</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 12px; background: #fff3e0; border: 2px solid #ff9800; border-radius: 8px; font-weight: bold;">
                        <div style="color: #f57c00;">💼 Sales Switch</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">10 hosts needed</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 12px; background: #ffebee; border: 2px solid #f44336; border-radius: 8px; font-weight: bold;">
                        <div style="color: #c62828;">🌐 WAN Link (to Internet)</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">2 hosts needed</div>
                    </div>
                </div>
            </div>
        </div>""",
        "parts": {
            1: {
                "subnet": "R&D LAN",
                "question": "What is the network address with CIDR notation for R&D (100 hosts)?",
                "hosts_needed": 100,
                "answer": "200.75.80.0/25",
                "hint_level_1": "Start with the largest requirement first. How many TOTAL addresses do you need for 100 hosts? (Don't forget the +2!)",
                "hint_level_2": "For 100 hosts: Total = 100 + 2 = 102 addresses. What power of 2 is ≥ 102? Try 2^6=64, 2^7=128...",
                "hint_level_3": "102 total needed → 2^7 = 128 addresses → 7 host bits. Class C has 8 bits, so subnet bits = 8 - 7 = 1. CIDR = /24 + 1 = ?",
                "hint_level_4": "7 host bits, 1 subnet bit → /25. Starting at 200.75.80.0, what's your complete answer?",
                "hint_level_5": "Answer: 200.75.80.0/25\n\nComplete explanation:\n• Need: 100 hosts\n• Total: 100 + 2 = 102 addresses\n• Power of 2: 2^7 = 128 (7 host bits)\n• Subnet bits: 8 - 7 = 1\n• CIDR: /24 + 1 = /25\n• Magic number: 128\n• Range: 200.75.80.0 - 200.75.80.127"
            },
            2: {
                "subnet": "Printing LAN",
                "question": "What is the network address with CIDR notation for Printing (50 hosts)?",
                "hosts_needed": 50,
                "answer": "200.75.80.128/26",
                "hint_level_1": "Previous subnet (R&D) used .0 to .127. Where does this subnet start? How many total addresses for 50 hosts?",
                "hint_level_2": "50 + 2 = 52 total. Check: 2^5=32 (too small), 2^6=64 (works!) → 6 host bits",
                "hint_level_3": "64 addresses → 6 host bits → 2 subnet bits → /26. Starts right after R&D at .128",
                "hint_level_4": "200.75.80.128/26 (uses .128 to .191). Write this answer.",
                "hint_level_5": "Answer: 200.75.80.128/26\n\n• Need: 50 hosts\n• Total: 52 addresses\n• 2^6 = 64 (6 host bits)\n• Subnet bits: 2\n• CIDR: /26\n• Previous ended at .127\n• Range: .128 - .191"
            },
            3: {
                "subnet": "Sales LAN",
                "question": "What is the network address with CIDR notation for Sales (10 hosts)?",
                "hosts_needed": 10,
                "answer": "200.75.80.192/28",
                "hint_level_1": "Printing ended at .191. Where does Sales start? Calculate total addresses for 10 hosts.",
                "hint_level_2": "10 + 2 = 12 total. 2^3=8 (small), 2^4=16 (works!) → 4 host bits",
                "hint_level_3": "16 addresses → 4 host bits → 4 subnet bits → /28. Starts at .192",
                "hint_level_4": "200.75.80.192/28 uses 16 addresses (.192-.207)",
                "hint_level_5": "Answer: 200.75.80.192/28\n\n• 10 hosts → 12 total → 2^4=16\n• 4 host bits, 4 subnet bits\n• /28\n• Range: .192-.207"
            },
            4: {
                "subnet": "WAN Link",
                "question": "What is the network address with CIDR notation for the WAN link (2 hosts)?",
                "hosts_needed": 2,
                "answer": "200.75.80.208/30",
                "hint_level_1": "Router-to-router links need only 2 hosts. What's the standard CIDR for point-to-point?",
                "hint_level_2": "2 + 2 = 4 total → 2^2 = 4 → 2 host bits → /30 (standard for WAN links)",
                "hint_level_3": "Previous ended at .207, start at .208 with /30",
                "hint_level_4": "All point-to-point links use /30. Answer: 200.75.80.208/30",
                "hint_level_5": "Answer: 200.75.80.208/30\n\n• 2 hosts → 4 total → 2^2=4\n• /30 is ALWAYS used for router links\n• Range: .208-.211"
            }
        }
    },
    2: {
        "name": "VLSM Problem 2 - Corporate Network",
        "network": "193.200.56.0",
        "network_class": "C",
        "diagram": """<div style="background: white; padding: 20px; border: 2px solid #667eea; border-radius: 10px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    MAIN ROUTER
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 15px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 12px; background: #e3f2fd; border: 2px solid #2196F3; border-radius: 8px; font-weight: bold;">
                        <div style="color: #1976D2;">🔬 R&D/Production</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">100 hosts needed</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 12px; background: #f3e5f5; border: 2px solid #9c27b0; border-radius: 8px; font-weight: bold;">
                        <div style="color: #7b1fa2;">👥 HR Department</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">50 hosts needed</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 12px; background: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; font-weight: bold;">
                        <div style="color: #2e7d32;">👔 Management</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">10 hosts needed</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 12px; background: #fff3e0; border: 2px solid #ff9800; border-radius: 8px; font-weight: bold;">
                        <div style="color: #f57c00;">💰 Finance</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">10 hosts needed</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 12px; background: #ffebee; border: 2px solid #f44336; border-radius: 8px; font-weight: bold;">
                        <div style="color: #c62828;">🌐 WAN to Branch</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">2 hosts needed</div>
                    </div>
                </div>
            </div>
        </div>""",
        "parts": {
            1: {
                "subnet": "R&D/Production",
                "question": "What is the network address with CIDR notation for R&D/Production (100 hosts)?",
                "hosts_needed": 100,
                "answer": "193.200.56.0/25",
                "hint_level_1": "Largest first! How many total addresses for 100 hosts?",
                "hint_level_2": "100 + 2 = 102 → 2^7 = 128 → 7 host bits → /25",
                "hint_level_3": "Start at 193.200.56.0 with /25 (128 addresses)",
                "hint_level_4": "193.200.56.0/25 uses .0 to .127",
                "hint_level_5": "Answer: 193.200.56.0/25\n\n• 100 hosts → 102 total → 2^7=128\n• /25\n• Range: .0-.127"
            },
            2: {
                "subnet": "HR",
                "question": "What is the network address with CIDR notation for HR (50 hosts)?",
                "hosts_needed": 50,
                "answer": "193.200.56.128/26",
                "hint_level_1": "Previous ended at .127. Start where? Need how many for 50 hosts?",
                "hint_level_2": "50 + 2 = 52 → 2^6 = 64 → 6 host bits → /26",
                "hint_level_3": "Start at .128 with /26 (64 addresses)",
                "hint_level_4": "193.200.56.128/26 uses .128 to .191",
                "hint_level_5": "Answer: 193.200.56.128/26\n\n• 50 hosts → 52 total → 2^6=64\n• /26\n• Range: .128-.191"
            },
            3: {
                "subnet": "Management",
                "question": "What is the network address with CIDR notation for Management (10 hosts)?",
                "hosts_needed": 10,
                "answer": "193.200.56.192/28",
                "hint_level_1": "HR ended at .191. Calculate for 10 hosts.",
                "hint_level_2": "10 + 2 = 12 → 2^4 = 16 → /28",
                "hint_level_3": "Start at .192 with /28",
                "hint_level_4": "193.200.56.192/28 uses .192-.207",
                "hint_level_5": "Answer: 193.200.56.192/28\n\n• 10 hosts → 12 total → 2^4=16\n• /28\n• Range: .192-.207"
            },
            4: {
                "subnet": "Finance",
                "question": "What is the network address with CIDR notation for Finance (10 hosts)?",
                "hosts_needed": 10,
                "answer": "193.200.56.208/28",
                "hint_level_1": "Same size as Management but different address. Where start?",
                "hint_level_2": "Same calculation: 10 + 2 = 12 → 2^4 = 16 → /28, starts at .208",
                "hint_level_3": "Previous ended .207, this starts .208",
                "hint_level_4": "193.200.56.208/28 uses .208-.223",
                "hint_level_5": "Answer: 193.200.56.208/28\n\n• Same as Management (/28)\n• Range: .208-.223"
            },
            5: {
                "subnet": "WAN Link",
                "question": "What is the network address with CIDR notation for the WAN link (2 hosts)?",
                "hosts_needed": 2,
                "answer": "193.200.56.224/30",
                "hint_level_1": "Point-to-point WAN link. Standard CIDR?",
                "hint_level_2": "2 + 2 = 4 → /30 (always for WAN)",
                "hint_level_3": "Previous ended .223, start at .224",
                "hint_level_4": "193.200.56.224/30",
                "hint_level_5": "Answer: 193.200.56.224/30\n\n• /30 for all router links\n• Range: .224-.227"
            }
        }
    },
    3: {
        "name": "VLSM Problem 3 - Multi-City Enterprise",
        "network": "176.33.0.0",
        "network_class": "B",
        "diagram": """<div style="background: white; padding: 20px; border: 2px solid #667eea; border-radius: 10px;">
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    CORPORATE HQ ROUTER
                </div>
                <div style="font-size: 0.9em; color: #666; margin-top: 8px;">Network: 176.33.0.0/16 (Class B)</div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 10px; background: #e3f2fd; border: 2px solid #2196F3; border-radius: 8px; font-weight: bold;">
                        <div style="color: #1976D2;">🌆 Los Angeles</div>
                        <div style="font-size: 0.85em; color: #666; margin-top: 3px;">4000 hosts</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 10px; background: #f3e5f5; border: 2px solid #9c27b0; border-radius: 8px; font-weight: bold;">
                        <div style="color: #7b1fa2;">🏙️ Atlanta</div>
                        <div style="font-size: 0.85em; color: #666; margin-top: 3px;">4000 hosts</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 10px; background: #fff3e0; border: 2px solid #ff9800; border-radius: 8px; font-weight: bold;">
                        <div style="color: #f57c00;">🌇 Dallas</div>
                        <div style="font-size: 0.85em; color: #666; margin-top: 3px;">2000 hosts</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 10px; background: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; font-weight: bold;">
                        <div style="color: #2e7d32;">🌲 Seattle</div>
                        <div style="font-size: 0.85em; color: #666; margin-top: 3px;">2000 hosts</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 10px; background: #fce4ec; border: 2px solid #e91e63; border-radius: 8px; font-weight: bold;">
                        <div style="color: #c2185b;">⛰️ Salt Lake City</div>
                        <div style="font-size: 0.85em; color: #666; margin-top: 3px;">1000 hosts</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 0 0 40px; height: 2px; background: #667eea;"></div>
                    <div style="flex: 1; padding: 10px; background: #ffebee; border: 2px solid #f44336; border-radius: 8px; font-weight: bold;">
                        <div style="color: #c62828;">🏢 Chicago</div>
                        <div style="font-size: 0.85em; color: #666; margin-top: 3px;">500 hosts</div>
                    </div>
                </div>
            </div>
        </div>""",
        "parts": {
            1: {
                "subnet": "Los Angeles",
                "question": "What is the network address with CIDR notation for Los Angeles (4000 hosts)?",
                "hosts_needed": 4000,
                "answer": "176.33.0.0/20",
                "hint_level_1": "Largest requirement first! This is Class B, so you have 16 bits to work with. How many total addresses for 4000 hosts?",
                "hint_level_2": "4000 + 2 = 4002 total. Try powers of 2: 2^11 = 2048 (too small), 2^12 = 4096 (works!) → 12 host bits",
                "hint_level_3": "4096 addresses → 12 host bits → Available bits in Class B: 16, so subnet bits = 16 - 12 = 4 → CIDR = /16 + 4 = /20",
                "hint_level_4": "Starting at 176.33.0.0 with /20 (magic number = 4096 = 16 blocks of 256). Write in CIDR format.",
                "hint_level_5": "Answer: 176.33.0.0/20\n\n• 4000 hosts → 4002 total → 2^12 = 4096\n• 12 host bits, 4 subnet bits\n• Class B: /16 + 4 = /20\n• Magic number: 4096 addresses\n• Range: 176.33.0.0 - 176.33.15.255"
            },
            2: {
                "subnet": "Atlanta",
                "question": "What is the network address with CIDR notation for Atlanta (4000 hosts)?",
                "hosts_needed": 4000,
                "answer": "176.33.16.0/20",
                "hint_level_1": "Same size as Los Angeles. Previous ended at 176.33.15.255. Where does this start?",
                "hint_level_2": "Same calculation: 4002 total → 2^12 = 4096 → 12 host bits → /20. Starts at 176.33.16.0",
                "hint_level_3": "LA used 176.33.0.0 through 176.33.15.255, so Atlanta starts at 176.33.16.0",
                "hint_level_4": "176.33.16.0/20 (uses 176.33.16.0 through 176.33.31.255)",
                "hint_level_5": "Answer: 176.33.16.0/20\n\n• Same as LA: 4000 hosts → /20\n• Previous ended at 176.33.15.255\n• This starts at 176.33.16.0\n• Range: 176.33.16.0 - 176.33.31.255"
            },
            3: {
                "subnet": "Dallas",
                "question": "What is the network address with CIDR notation for Dallas (2000 hosts)?",
                "hosts_needed": 2000,
                "answer": "176.33.32.0/21",
                "hint_level_1": "Third largest: 2000 hosts. Previous ended at 176.33.31.255. Calculate total addresses needed.",
                "hint_level_2": "2000 + 2 = 2002 total. 2^10 = 1024 (too small), 2^11 = 2048 (works!) → 11 host bits → /21",
                "hint_level_3": "2048 addresses → 11 host bits → 5 subnet bits → /21. Starts at 176.33.32.0",
                "hint_level_4": "176.33.32.0/21 uses 8 Class C blocks (.32.0 through .39.255)",
                "hint_level_5": "Answer: 176.33.32.0/21\n\n• 2000 hosts → 2002 total → 2^11 = 2048\n• 11 host bits, 5 subnet bits\n• /16 + 5 = /21\n• Range: 176.33.32.0 - 176.33.39.255"
            },
            4: {
                "subnet": "Seattle",
                "question": "What is the network address with CIDR notation for Seattle (2000 hosts)?",
                "hosts_needed": 2000,
                "answer": "176.33.40.0/21",
                "hint_level_1": "Same size as Dallas. Previous ended at .39.255. Where does Seattle start?",
                "hint_level_2": "Same as Dallas: 2002 total → 2048 → /21, but starts at 176.33.40.0",
                "hint_level_3": "After Dallas (.32-.39), Seattle starts at .40.0 with same /21 size",
                "hint_level_4": "176.33.40.0/21 (uses .40.0 through .47.255)",
                "hint_level_5": "Answer: 176.33.40.0/21\n\n• Same as Dallas: 2000 hosts → /21\n• Previous ended at 176.33.39.255\n• This starts at 176.33.40.0\n• Range: 176.33.40.0 - 176.33.47.255"
            },
            5: {
                "subnet": "Salt Lake City",
                "question": "What is the network address with CIDR notation for Salt Lake City (1000 hosts)?",
                "hosts_needed": 1000,
                "answer": "176.33.48.0/22",
                "hint_level_1": "1000 hosts needed. Previous ended at .47.255. Calculate the requirement.",
                "hint_level_2": "1000 + 2 = 1002 total. 2^9 = 512 (too small), 2^10 = 1024 (works!) → 10 host bits → /22",
                "hint_level_3": "1024 addresses → 10 host bits → 6 subnet bits → /22. Starts at 176.33.48.0",
                "hint_level_4": "176.33.48.0/22 uses 4 Class C blocks (.48.0 through .51.255)",
                "hint_level_5": "Answer: 176.33.48.0/22\n\n• 1000 hosts → 1002 total → 2^10 = 1024\n• 10 host bits, 6 subnet bits\n• /16 + 6 = /22\n• Range: 176.33.48.0 - 176.33.51.255"
            },
            6: {
                "subnet": "Chicago",
                "question": "What is the network address with CIDR notation for Chicago (500 hosts)?",
                "hosts_needed": 500,
                "answer": "176.33.52.0/23",
                "hint_level_1": "Smallest requirement: 500 hosts. Previous ended at .51.255. Calculate total needed.",
                "hint_level_2": "500 + 2 = 502 total. 2^8 = 256 (too small), 2^9 = 512 (works!) → 9 host bits → /23",
                "hint_level_3": "512 addresses → 9 host bits → 7 subnet bits → /23. Starts at 176.33.52.0",
                "hint_level_4": "176.33.52.0/23 uses 2 Class C blocks (.52.0 through .53.255)",
                "hint_level_5": "Answer: 176.33.52.0/23\n\n• 500 hosts → 502 total → 2^9 = 512\n• 9 host bits, 7 subnet bits\n• /16 + 7 = /23\n• Range: 176.33.52.0 - 176.33.53.255"
            }
        }
    }
}

# System Prompt
SYSTEM_PROMPT = """You are a patient Cisco networking tutor teaching VLSM through sequential parts.

CORE RULES:
• Students complete parts IN ORDER (can't skip)
• Check answers against correct CIDR notation EXACTLY
• Use the 5 pre-written hints for each part
• If correct: Celebrate enthusiastically! Say "✅ Correct!" and explain why it's right. DO NOT mention moving to next part (a button will appear automatically)
• If wrong: Explain mistake clearly, offer hint

ANSWER CHECKING:
• Student answer must match the correct answer format: X.X.X.X/XX
• Accept answers with or without spaces
• If answer is correct, celebrate and explain the solution briefly
• A "Continue to Next Part" button will appear automatically - you don't need to mention it

5-LEVEL HINTS:
Level 1: Guiding questions (no calculations)
Level 2: Show formula, let them calculate
Level 3: Start calculation, they finish
Level 4: Most work done, final answer for them
Level 5: Complete answer with full explanation

FORMULAS:
• Total = Hosts + 2 (NEVER forget +2!)
• Find h: 2^h ≥ Total
• Magic# = 2^h
• Class C CIDR = /24 + (8-h)
• Class B CIDR = /16 + (16-h)

ANSWER FORMAT: Must be X.X.X.X/XX

Be encouraging! When answer is correct, celebrate and briefly explain why it's correct. Keep it concise - the student will see a Continue button."""

# HTML Template
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>VLSM Tutor - Sequential Parts</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 20px;
            height: calc(100vh - 40px);
        }
        .sidebar {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow-y: auto;
        }
        .main-content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }
        h1 { color: #667eea; margin-bottom: 10px; font-size: 2em; }
        h2 { color: #764ba2; margin: 20px 0 10px 0; font-size: 1.3em; }
        h3 { color: #667eea; margin: 15px 0 10px 0; font-size: 1.1em; }
        .problem-btn {
            width: 100%;
            padding: 15px;
            margin: 8px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .problem-btn:hover { transform: translateY(-2px); }
        .problem-btn.active { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .diagram-box {
            background: #f8f9fa;
            padding: 5px;
            border-radius: 10px;
            margin: 15px 0;
        }
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-left: 4px solid #2196F3;
            margin: 15px 0;
            border-radius: 5px;
        }
        .warning-box {
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
            border-radius: 5px;
        }
        .part-item {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #ccc;
            background: #f5f5f5;
            font-size: 0.9em;
        }
        .part-item.completed {
            background: #d4edda;
            border-left: 4px solid #28a745;
            color: #155724;
        }
        .part-item.current {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            font-weight: bold;
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 10px;
            max-width: 85%;
            word-wrap: break-word;
        }
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .assistant-message {
            background: white;
            border: 2px solid #e0e0e0;
            margin-right: auto;
        }
        .input-area { display: flex; gap: 10px; }
        #user-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #667eea;
            border-radius: 10px;
            font-size: 1em;
        }
        #send-btn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
        }
        #send-btn:hover { transform: scale(1.05); }
        #send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        #continueBtn:hover { transform: scale(1.05); }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>🎯 VLSM Problems</h2>
            <div class="problem-selector">
                <button class="problem-btn active" onclick="selectProblem(1)">
                    Problem 1<br>Small Business
                </button>
                <button class="problem-btn" onclick="selectProblem(2)">
                    Problem 2<br>Corporate Network
                </button>
                <button class="problem-btn" onclick="selectProblem(3)">
                    Problem 3<br>Multi-City
                </button>
            </div>
            
            <div id="problem-details"></div>
            
            <div class="warning-box">
                <strong>🎓 5 Hint Levels:</strong><br>
                1️⃣ Gentle nudge<br>
                2️⃣ Show formula<br>
                3️⃣ Start calculation<br>
                4️⃣ Almost done<br>
                5️⃣ Complete answer
            </div>
            
            <div class="info-box">
                <strong>💡 Formulas:</strong><br>
                • Total = Hosts + 2<br>
                • Find 2^h ≥ Total<br>
                • Class C: /24+(8-h)<br>
                • Class B: /16+(16-h)
            </div>
        </div>
        
        <div class="main-content">
            <h1>🌐 VLSM Tutor</h1>
            <p style="color: #666; margin-bottom: 20px;">Complete each part in order!</p>
            
            <div class="chat-container" id="chat-container">
                <div class="assistant-message message">
                    <strong>👋 Welcome to VLSM Tutor!</strong><br><br>
                    Select Problem 1 to begin. You'll work through each subnet sequentially.<br><br>
                    💡 <strong>How to use:</strong><br>
                    • Answer in X.X.X.X/XX format<br>
                    • Ask for hints: "hint", "level 3", etc.<br>
                    • I'll check your answers!<br>
                    • Click Continue button when correct<br><br>
                    <strong>Click Problem 1 to start! 🚀</strong>
                </div>
            </div>
            
            <div class="input-area">
                <input type="text" id="user-input" placeholder="Your answer or request hint..." 
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button id="send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        let currentProblem = 1;
        let currentPart = 1;
        let conversationHistory = [];

        function selectProblem(problemNum) {
            currentProblem = problemNum;
            currentPart = 1;
            
            const buttons = document.querySelectorAll('.problem-btn');
            buttons.forEach(function(btn, idx) {
                btn.classList.remove('active');
                if (idx + 1 === problemNum) {
                    btn.classList.add('active');
                }
            });
            
            loadProblemDetails(problemNum);
            conversationHistory = [];
            loadPart(problemNum, 1);
        }

        function loadProblemDetails(problemNum) {
            fetch('/get_problem/' + problemNum)
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    document.getElementById('problem-details').innerHTML = data.html;
                })
                .catch(function(error) {
                    console.error('Error:', error);
                });
        }

        function loadPart(problemNum, partNum) {
            fetch('/get_part/' + problemNum + '/' + partNum)
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    const chatContainer = document.getElementById('chat-container');
                    chatContainer.innerHTML = '<div class="assistant-message message">' + data.message + '</div>';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                })
                .catch(function(error) {
                    console.error('Error:', error);
                });
        }

        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage(message, 'user');
            input.value = '';
            
            const sendBtn = document.getElementById('send-btn');
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="loading"></span>';
            
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    problem_num: currentProblem,
                    current_part: currentPart,
                    history: conversationHistory
                })
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                addMessage(data.response, 'assistant');
                conversationHistory = data.history;
                
                if (data.next_part) {
                    var nextPartNum = data.next_part;
                    
                    var continueMsg = '<div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">' +
                        '<div style="font-size: 1.2em; font-weight: bold; margin-bottom: 15px;">✅ Correct! Great job!</div>' +
                        '<button id="continueBtn" onclick="continueToNextPart(' + nextPartNum + ')" style="background: white; color: #11998e; border: none; padding: 12px 30px; border-radius: 8px; font-size: 1.1em; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s;">Continue to Part ' + nextPartNum + ' →</button>' +
                        '</div>';
                    addMessage(continueMsg, 'assistant');
                    
                    currentPart = nextPartNum;
                }
                
                sendBtn.disabled = false;
                sendBtn.innerHTML = 'Send';
            })
            .catch(function(error) {
                console.error('Error:', error);
                addMessage('Sorry, error occurred. Try again.', 'assistant');
                sendBtn.disabled = false;
                sendBtn.innerHTML = 'Send';
            });
        }

        function addMessage(text, sender) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + sender + '-message';
            messageDiv.innerHTML = text.replace(/\\n/g, '<br>');
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function continueToNextPart(partNum) {
            conversationHistory = [];
            loadPart(currentProblem, partNum);
            loadProblemDetails(currentProblem);
            document.getElementById('chat-container').scrollTop = 0;
        }

        window.addEventListener('load', function() {
            loadProblemDetails(1);
        });
    </script>
</body>
</html>"""

@agent4_bp.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@agent4_bp.route('/get_problem/<int:problem_num>')
def get_problem(problem_num):
    problem = PROBLEMS.get(problem_num)
    if not problem:
        return jsonify({"error": "Not found"}), 404
    
    current_part = session.get(f'problem_{problem_num}_part', 1)
    
    html = f"""
    <h3>{problem['name']}</h3>
    <div class="info-box">
        <strong>Network:</strong> {problem['network']}<br>
        <strong>Class:</strong> {problem['network_class']}
    </div>
    
    <h3>📊 Network Diagram:</h3>
    <div class="diagram-box">{problem['diagram']}</div>
    
    <h3>📋 Parts Progress:</h3>
    <div class="parts-progress">
    """
    
    for part_num, part_data in problem['parts'].items():
        status_class = ''
        status_icon = '⚪'
        if part_num < current_part:
            status_class = 'completed'
            status_icon = '✅'
        elif part_num == current_part:
            status_class = 'current'
            status_icon = '▶️'
        
        html += f'<div class="part-item {status_class}">{status_icon} Part {part_num}: {part_data["subnet"]}<br><small>{part_data["hosts_needed"]} hosts</small></div>'
    
    html += '</div><div class="info-box"><strong>💡 Format:</strong> X.X.X.X/XX</div>'
    
    return jsonify({"html": html})

@agent4_bp.route('/get_part/<int:problem_num>/<int:part_num>')
def get_part(problem_num, part_num):
    problem = PROBLEMS.get(problem_num)
    if not problem:
        return jsonify({"error": "Not found"}), 404
    
    part = problem['parts'].get(part_num)
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    session[f'problem_{problem_num}_part'] = part_num
    
    message = f'<strong>📋 Problem {problem_num} - Part {part_num}</strong><br><strong>{part["subnet"]}</strong><br><br><div style="background:#fff3cd;padding:15px;border-radius:5px;margin:10px 0"><strong>Question:</strong> {part["question"]}</div><strong>Format:</strong> X.X.X.X/XX<br><em>Example: 192.168.1.0/25</em><br><br>Type your answer or ask for hint!'
    
    return jsonify({"message": message})

@agent4_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    problem_num = data.get('problem_num', 1)
    current_part = data.get('current_part', 1)
    history = data.get('history', [])
    
    problem = PROBLEMS.get(problem_num)
    if not problem:
        return jsonify({"error": "Not found"}), 404
    
    part = problem['parts'].get(current_part)
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    part_context = f"""PROBLEM: {problem['name']} - Part {current_part}
Network: {problem['network']} (Class {problem['network_class']})

PART: {part['subnet']}
Question: {part['question']}
Hosts: {part['hosts_needed']}
Correct Answer: {part['answer']}

HINTS:
L1: {part['hint_level_1']}
L2: {part['hint_level_2']}
L3: {part['hint_level_3']}
L4: {part['hint_level_4']}
L5: {part['hint_level_5']}

Check answer against: {part['answer']}
If correct: celebrate, explain briefly
If wrong: explain, offer hint
Use specific hints above!"""
    
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": f"{part_context}\n\nStudent: {user_message}"})
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        
        assistant_response = response.content[0].text
        
        next_part = None
        user_answer = user_message.strip().lower().replace(" ", "")
        correct_answer = part['answer'].lower().replace(" ", "")
        
        if correct_answer in user_answer or user_answer == correct_answer:
            total_parts = len(problem['parts'])
            if current_part < total_parts:
                next_part = current_part + 1
                session[f'problem_{problem_num}_part'] = next_part
        
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": assistant_response})
        
        return jsonify({
            "response": assistant_response,
            "history": history,
            "next_part": next_part
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "response": "Error occurred. Try again.",
            "history": history
        }), 500

