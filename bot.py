import re
import uuid
import nltk
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

# Download NLTK data 
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('stopwords', quiet=True)

# Preprocessing setup 
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def tokenize_text(text):
    try:
        return nltk.word_tokenize(text)
    except:
        return re.findall(r"\b\w+\b", text)

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = tokenize_text(text)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 1]
    return " ".join(tokens)

# FAQ knowledge base
FAQS = [
    {'id': 1, 'questions': ["What are your opening hours?", "When do you close?", "What time do you open and close?", "Till what time is the restaurant open?"], 'answer': "We are open from 10 AM to 11 PM every day."},
    {'id': 2, 'questions': ["Do you have any discounts?", "Are there any offers available?", "What promotions do you have?", "Discounts for parties, festivals, weekends, or students?"], 'answer': "We offer 15% off for full bookings (party), 20% during festivals, 10% on Saturday nights (weekend), and 15% for students."},
    {'id': 3, 'questions': ["Can I see the menu?", "What food do you serve?", "Show me the dishes available", "Menu details please"], 'answer': "Our menu includes appetizers, main courses, desserts, and beverages."},
    {'id': 4, 'questions': ["What is the cancellation policy?", "Can I cancel my booking?", "Do you have refunds for cancellations?"], 'answer': "You can cancel your booking up to 24 hours before the reservation. Refunds will be processed according to the payment method."},
    {'id': 5, 'questions': ["Do you offer delivery?", "What are your delivery timings?", "Can I get food delivered?"], 'answer': "We deliver until 11 PM every day. Please provide your address for delivery."},
    {'id': 6, 'questions': ["What payment methods do you accept?", "Do you accept cards or cash?", "Payment options?"], 'answer': "We accept cash, debit/credit cards, and UPI payments."},
    {'id': 7, 'questions': ["What is the ambience like?", "Tell me about seating and environment", "Is it suitable for families or parties?"], 'answer': "Our restaurant offers a cozy, elegant ambience with warm lighting, soft music, and comfortable seating. It’s perfect for family dinners, romantic dates, and group celebrations. We also have private sections for parties and a relaxed outdoor seating area."},
    {'id': 8, 'questions': ["Can I bring outside food or drinks?", "Are outside drinks allowed?", "Do you allow external food?"], 'answer': "Outside food and drinks are not allowed in the restaurant."},
    {'id': 9, 'questions': ["Do you have facilities for senior citizens?", "Wheelchair available?", "High chair for toddlers?", "Reduced price for toddlers?"], 'answer': "We provide wheelchairs for senior citizens and high chairs for toddlers. Reduced prices are available for toddlers."},
    {'id': 10, 'questions': ["Who can enter the bar?", "Is under 18 allowed?", "Stag entry policy?", "Are there age restrictions?"], 'answer': "Persons below 18 are not allowed. For stag entry, pay-for-1 policy applies."},
    {'id': 11, 'questions': ["What is your address?", "Where are you located?", "Contact number?", "How do I contact you?", "Email address?"], 
     'answer': (
         "Asian Fusion\n"
         "Address: 27 Orchid Street, Bandra East, Mumbai, Maharashtra, India\n"
         "Phone (General & Bookings): +91-98765-43210\n"
         "Delivery: +91-98765-43210 (call to place delivery orders)\n"
         "Email: info@asianfusion.com\n\n"
         "For delivery orders please call our delivery number. Note: delivery is free within 3 km; beyond 3 km an extra charge of ₹20 per km will apply."
     )}
]

# FAQ Vectorization 
question_texts, question_map = [], []
for faq in FAQS:
    for q in faq['questions']:
        question_texts.append(preprocess(q))
        question_map.append((faq['id'], q))

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(question_texts)
faq_answer_map = {faq['id']: faq['answer'] for faq in FAQS}

def get_faq_answer(user_text):
    qv = vectorizer.transform([preprocess(user_text)])
    sims = cosine_similarity(qv, X).flatten()
    best_idx = int(sims.argmax())
    fid, _ = question_map[best_idx]
    if sims[best_idx] > 0.45:
        return faq_answer_map[fid], sims[best_idx]
    return None, 0.0

# Intent Detection 
INTENTS = ["booking", "takeaway", "delivery", "ask_discounts", "ask_opening_hours", "ask_menu", "ask_cancellation", "ask_bar_rules", "ask_ambience", "ask_special_requests", "smalltalk"]
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def detect_intent_hybrid(user_text):
    text = user_text.lower()
    if any(k in text for k in ["book", "reservation", "dine in"]): return "booking"
    if any(k in text for k in ["takeaway", "pick up", "order to go"]): return "takeaway"
    if any(k in text for k in ["delivery", "deliver", "address"]): return "delivery"
    if any(k in text for k in ["discount", "offer", "promotion"]): return "ask_discounts"
    if any(k in text for k in ["open", "close", "hours", "time"]): return "ask_opening_hours"
    if any(k in text for k in ["menu", "food", "dishes"]): return "ask_menu"
    if any(k in text for k in ["cancel", "refund"]): return "ask_cancellation"
    if any(k in text for k in ["bar", "age", "stag", "entry"]): return "ask_bar_rules"
    if any(k in text for k in ["ambience", "environment", "seating"]): return "ask_ambience"
    if any(k in text for k in ["senior", "wheelchair", "toddler", "high chair"]): return "ask_special_requests"
    if any(k in text for k in ["name", "contact", "email", "phone", "location", "where"]): return "ask_contact_info"

    try:
        result = classifier(user_text, INTENTS)
        if result['scores'][0] >= 0.5:
            return result['labels'][0]
    except:
        pass
    return "smalltalk"

# Core Chatbot Logic
bookings = []
pending_transaction = None
pending_info = {}

def handle_transaction(trans_type, info):
    booking_id = str(uuid.uuid4())[:8]
    bookings.append({"type": trans_type, "info": info, "id": booking_id})
    return f"{trans_type.capitalize()} confirmed! Your reference ID is {booking_id}"

def respond_to_user(user_text):
    global pending_transaction, pending_info

    if pending_transaction:
        try:
            info = dict(item.strip().split(":") for item in user_text.split(","))
            pending_info.update(info)
            confirmation = handle_transaction(pending_transaction, pending_info)
            pending_transaction = None
            pending_info = {}
            return confirmation
        except:
            return "Invalid format. Please provide details like: name: John, phone: 9998887777"

    intent = detect_intent_hybrid(user_text)
    if intent in ["booking", "takeaway", "delivery"]:
        pending_transaction = intent
        pending_info = {}
        return f"Please provide your details for {intent} (name, phone, and address if delivery). Example: 'name: John, phone: 9998887777'"

    answer, _ = get_faq_answer(user_text)
    if answer:
        return answer

    return "I'm here to help with your restaurant queries. Did you mean something else?"

# Command Line Run 
if __name__ == "__main__":
    print("Welcome to the restaurant chatbot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Bot: Thank you! Have a great day!")
            break
        print("Bot:", respond_to_user(user_input))
