conversation_history = []

current_slots = {
    "customer_name": None,
    "table_size": None,
    "date_time": None,
    "requests": [],
    "order_type": None,  # booking, delivery, takeaway
    "delivery_address": None,
    "age": None
}

def add_message(role, message):
    conversation_history.append({"role": role, "message": message})

def get_context(last_n=5):
    return conversation_history[-last_n:]

def reset_slots():
    global current_slots
    current_slots = {
        "customer_name": None,
        "table_size": None,
        "date_time": None,
        "requests": [],
        "order_type": None,
        "delivery_address": None,
        "age": None
    }
