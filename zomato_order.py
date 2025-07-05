import streamlit as st

# -------------------------------
# 🍔 1️⃣ Title
# -------------------------------
st.title("🍽️ Zomato Order Demo")

st.write("Welcome to our demo food ordering app!")

# -------------------------------
# 🏢 2️⃣ Choose Restaurant
# -------------------------------
restaurant = st.selectbox(
    "Select a restaurant",
    ["Pizza Palace", "Burger Hub", "Sushi Corner"]
)

# -------------------------------
# 📋 3️⃣ Menu Items
# -------------------------------
menu = {
    "Pizza Palace": {
        "Margherita Pizza": 250,
        "Pepperoni Pizza": 300,
        "Garlic Bread": 120
    },
    "Burger Hub": {
        "Veggie Burger": 150,
        "Chicken Burger": 200,
        "French Fries": 80
    },
    "Sushi Corner": {
        "Salmon Sushi": 400,
        "Tuna Roll": 350,
        "Miso Soup": 150
    }
}

selected_items = []
quantities = {}

st.subheader(f"📜 Menu — {restaurant}")

for item, price in menu[restaurant].items():
    if st.checkbox(f"{item} — ₹{price}"):
        qty = st.number_input(f"Quantity for {item}", min_value=1, max_value=10, value=1, step=1)
        selected_items.append((item, price))
        quantities[item] = qty

# -------------------------------
# 💵 4️⃣ Calculate Total
# -------------------------------
if selected_items:
    st.write("---")
    total = sum(price * quantities[item] for item, price in selected_items)
    st.write("### 🧾 Order Summary:")
    for item, price in selected_items:
        st.write(f"{item} x {quantities[item]} — ₹{price * quantities[item]}")

    st.write(f"**Total: ₹{total}**")

    # -------------------------------
    # ✅ 5️⃣ Place Order
    # -------------------------------
    if st.button("✅ Place Order"):
        st.success("🎉 Order placed successfully! Bon Appétit!")
else:
    st.info("Please select at least one menu item to order.")
