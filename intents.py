import uuid
from datetime import datetime

bookings = []
orders = []

def apply_discounts(slots):
    discount = 0
    if slots.get("table_size", 0) > 10:
        discount += 15
    if "festival" in slots.get("requests", []):
        discount += 20
    if slots.get("date_time", "").lower().startswith("saturday"):
        discount += 10
    if "student" in slots.get("requests", []):
        discount += 15
    return discount

def validate_delivery_time(date_time):
    try:
        dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        return dt.hour < 23
    except:
        return False

def create_booking(slots):
    booking_id = str(uuid.uuid4())[:8]
    discount = apply_discounts(slots)
    bookings.append({"id": booking_id, **slots, "discount": discount})
    return f"Booking confirmed ✅. ID: {booking_id}. Discount applied: {discount}%"

def create_takeaway_order(slots):
    order_number = str(uuid.uuid4())[:6]
    orders.append({"order_number": order_number, "type": "takeaway"})
    return f"Takeaway order {order_number} confirmed ✅."

def create_delivery_order(slots):
    if not validate_delivery_time(slots.get("date_time", "")):
        return "Delivery cannot be scheduled after 11 PM. Please provide an earlier time."
    order_number = str(uuid.uuid4())[:6]
    orders.append({"order_number": order_number, "type": "delivery", "address": slots.get("delivery_address")})
    return f"Delivery order {order_number} to {slots.get('delivery_address')} confirmed ✅."
