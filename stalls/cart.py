class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get("cart", [])
        self.stall_id = self.session.get("cart_stall_id")

        if not isinstance(self.cart, list):
            self.cart = []
            self.session["cart"] = self.cart

        self.session.modified = True

    def add(self, stall_id, item_id, option_id, item_name, option_name, quantity, price, description=None):
        stall_id = str(stall_id)
        self.cart = self.session.get("cart", [])
        self.stall_id = self.session.get("cart_stall_id")

        if not self.cart:
            self.stall_id = stall_id
            self.session["cart_stall_id"] = stall_id

        elif self.stall_id != stall_id:
            raise ValueError("Cart contains items from a different stall.")

        for entry in self.cart:
            if entry["option_id"] == str(option_id):
                entry["quantity"] += quantity
                break
        else:
            self.cart.append({
                "item_id": item_id,
                "option_id": str(option_id),
                "item_name": item_name,
                "option_name": option_name,
                "description": description,
                "quantity": quantity,
                "price": float(price),
            })

        self.session["cart"] = self.cart
        self.session["cart_stall_id"] = self.stall_id
        self.session.modified = True

    def delete(self, option_id):
        option_id = str(option_id)
        self.cart = [item for item in self.cart if str(item["option_id"]) != option_id]
        self.session["cart"] = self.cart

        if not self.cart:
            self.clear()

        self.session.modified = True

    def get_items(self):
        return self.cart

    def get_total(self):
        return sum(item["quantity"] * item["price"] for item in self.cart)

    def clear(self):
        self.session["cart"] = []
        self.session["cart_stall_id"] = None
        self.cart = []
        self.stall_id = None
        self.session.modified = True
