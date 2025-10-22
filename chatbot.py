from vector_store import load_faq_embeddings, query_faq
from intents import create_booking, create_takeaway_order, create_delivery_order
from conversation import add_message, get_context, current_slots, reset_slots

# Load FAQ embeddings
load_faq_embeddings()

def handle_message(user_input):
    add_message("user", user_input)
    msg = user_input.lower()
    reply = ""

    # Determine order type
    if current_slots["order_type"] is None:
        if any(k in msg for k in ["book", "reservation"]):
            current_slots["order_type"] = "booking"
            reply = "Great! What's your name for the booking?"
            add_message("bot", reply)
            return reply
        elif "takeaway" in msg or "pick up" in msg:
            current_slots["order_type"] = "takeaway"
            reply = create_takeaway_order(current_slots)
            reset_slots()
            add_message("bot", reply)
            return reply
        elif "delivery" in msg:
            current_slots["order_type"] = "delivery"
            reply = "Sure! Please provide your delivery address."
            add_message("bot", reply)
            return reply

    # Capture slots dynamically
    if current_slots["order_type"] == "booking":
        if current_slots["customer_name"] is None:
            current_slots["customer_name"] = user_input
            reply = "How many people will be attending?"
        elif current_slots["table_size"] is None:
            try:
                current_slots["table_size"] = int(user_input)
                reply = "Please provide date and time for your booking (YYYY-MM-DD HH:MM)."
            except:
                reply = "Please enter a valid number for table size."
        elif current_slots["date_time"] is None:
            current_slots["date_time"] = user_input
            reply = create_booking(current_slots)
            reset_slots()
        else:
            reply = "Booking already completed."

    elif current_slots["order_type"] == "delivery":
        if current_slots["delivery_address"] is None:
            current_slots["delivery_address"] = user_input
            reply = "Please provide delivery time (YYYY-MM-DD HH:MM)."
        elif current_slots["date_time"] is None:
            current_slots["date_time"] = user_input
            reply = create_delivery_order(current_slots)
            reset_slots()

    else:
        # FAQ semantic search first
        faq_results = query_faq(user_input)
        if faq_results:
            reply = "\n".join([f"{r['question']} -> {r['answer']}" for r in faq_results])
        else:
            reply = "Sorry, I don't have an answer for that right now."

    add_message("bot", reply)
    return reply
