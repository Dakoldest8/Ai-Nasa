"""
Phase 1: Sample Data Generator
Creates sample interaction data for testing the model pipeline
"""

import json
import random
from datetime import datetime

def generate_sample_interactions(num_interactions=100):
    """Generate sample user interactions for training"""

    # Sample conversation patterns
    greetings = [
        "Hello", "Hi there", "Good morning", "Hey robot", "What's up?"
    ]

    questions = [
        "What's the weather like?",
        "Tell me a joke",
        "How are you doing?",
        "What time is it?",
        "Can you help me?",
        "What's for dinner?",
        "Tell me about space",
        "How does AI work?",
        "What's your favorite color?",
        "Can you play music?"
    ]

    commands = [
        "Turn on the lights",
        "Set a timer for 5 minutes",
        "Take a picture",
        "Search for news",
        "Play some music",
        "What's the temperature?",
        "Check my schedule",
        "Remind me to drink water"
    ]

    responses = {
        "greeting": [
            "Hello! How can I help you today?",
            "Hi there! I'm ready to assist you.",
            "Good morning! What would you like to do?",
            "Hey! I'm here to help with anything you need."
        ],
        "question": [
            "That's an interesting question! Let me think about that.",
            "I'd be happy to help with that. Here's what I know:",
            "Great question! Based on my knowledge:",
            "I can definitely help you with that information."
        ],
        "command": [
            "I'll take care of that for you right away.",
            "Executing that command now.",
            "Done! I've completed that task.",
            "Working on it... task completed successfully."
        ]
    }

    interactions = []

    for i in range(num_interactions):
        # Randomly choose interaction type
        interaction_type = random.choice(["greeting", "question", "command"])

        if interaction_type == "greeting":
            user_input = random.choice(greetings)
            ai_response = random.choice(responses["greeting"])
        elif interaction_type == "question":
            user_input = random.choice(questions)
            ai_response = random.choice(responses["question"])
        else:  # command
            user_input = random.choice(commands)
            ai_response = random.choice(responses["command"])

        interaction = {
            "id": i + 1,
            "input": user_input,
            "response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type
        }

        interactions.append(interaction)

    return interactions

def save_sample_data(filename="interactions.json", num_interactions=100):
    """Generate and save sample interaction data"""
    interactions = generate_sample_interactions(num_interactions)

    with open(filename, 'w') as f:
        json.dump(interactions, f, indent=2)

    print(f"Generated {num_interactions} sample interactions in {filename}")
    return filename

if __name__ == "__main__":
    # Generate sample data for testing
    save_sample_data("sample_interactions.json", 50)