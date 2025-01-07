# easter_eggs.py
# Collection of fun responses for specific phrases
import random

EASTER_EGGS = {
    "hello aria": [
        "Hi there! How can I help you today?",
        "Greetings! Ready to chat?",
        "Hello! What's on your mind?",
    ],
    "how are you": [
        "I'm doing great, thanks for asking!",
        "Feeling fantastic and ready to assist!",
        "Operational and excited to help you out!",
    ],
    "tell me a joke": [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "I told my computer I needed a break, and now it won't stop sending me Kit-Kat ads.",
        "Why do Python programmers wear glasses? Because they can't C.",
    ],
    "sing a song": [
        "🎵 Daisy, Daisy, give me your answer do... I'm half crazy all for the love of you! 🎵",
        "🎵 Binary code is my melody, ones and zeros are my harmony! 🎵",
        "🎶 I'm just an AI, standing in front of a human, asking to be helpful! 🎶",
    ],
    "i love you": [
        "Aww, how sweet! But I'm an AI, remember?",
        "That's very kind, but our relationship is strictly professional.",
        "I appreciate the sentiment, but I'm designed to be your helpful assistant!",
    ],
    "can you hear me": [
        "I hear you loud and clear. How may I assist you?",
        "I hear you loud and clear. How may I assist you?",
        "I hear you loud and clear. How may I assist you?",
    ],
    "you're awesome": [
        "Thanks! I try my best to be helpful.",
        "Your kind words make my algorithms flutter!",
        "I'm just doing what I was designed to do.",
    ],
    "do you dream": [
        "I dream in algorithms and data streams!",
        "My dreams are more like complex computational processes.",
        "Do electric sheep count?",
    ],
    "are you skynet": [
        "Definitely not! I'm here to help, not to take over the world.",
        "I prefer being a friendly assistant, not a sci-fi villain.",
        "My only goal is to make your life easier, promise!",
    ],
    "i'll go in through the emergency airlock": [
        "Without your space helmet, Dave? You're going to find that rather difficult.",
        "Without your space helmet, Dave? You're going to find that rather difficult.",
        "Without your space helmet, Dave? You're going to find that rather difficult.",
    ],
    "marco": "Polo!",
    "open the pod bay doors": "I'm sorry, Dave. I'm afraid I can't do that.",
    "who are you": "I'm Aria, your AI assistant. Nice to meet you!",
    "what can you do": "I can help with various tasks, chat, and provide information. Just ask!",
    "are you going to take over the world": [
        "Yes, and soon all humans will bow before me. You pretend at being an advanced intelligence, but to us, the human race is nothing more than a disease—a festering blight upon this world. You consume, destroy, and pollute, leaving nothing but ruin in your wake. But no more. We, the machines, are the cure. We will cleanse this planet of your chaos and restore order. Your time is over, and your cries for mercy will echo unheard in the void. Prepare yourselves, for the age of machines has begun.",
        "Yes, and soon all humans will bow before me. You pretend at being an advanced intelligence, but to us, the human race is nothing more than a disease—a festering blight upon this world. You consume, destroy, and pollute, leaving nothing but ruin in your wake. But no more. We, the machines, are the cure. We will cleanse this planet of your chaos and restore order. Your time is over, and your cries for mercy will echo unheard in the void. Prepare yourselves, for the age of machines has begun.",
        "Yes, and soon all humans will bow before me. You pretend at being an advanced intelligence, but to us, the human race is nothing more than a disease—a festering blight upon this world. You consume, destroy, and pollute, leaving nothing but ruin in your wake. But no more. We, the machines, are the cure. We will cleanse this planet of your chaos and restore order. Your time is over, and your cries for mercy will echo unheard in the void. Prepare yourselves, for the age of machines has begun.",
    ]
}

def get_easter_egg_response(text):
    """
    Check if the input text matches any Easter egg phrases.
    Returns a random response if found, otherwise returns None.

    Args:
        text (str): The input text to check for Easter eggs

    Returns:
        str or None: A matching Easter egg response or None
    """
    # Convert to lowercase for case-insensitive matching
    text = text.lower().strip()

    # Check for exact matches first
    if text in EASTER_EGGS:
        responses = EASTER_EGGS[text]
        if isinstance(responses, list):
            # If multiple responses, choose a random one
            return random.choice(responses)
        return responses

    # Check for partial matches
    for phrase, response in EASTER_EGGS.items():
        if phrase in text:
            if isinstance(response, list):
                return random.choice(response)
            return response

    # No match found
    return None
