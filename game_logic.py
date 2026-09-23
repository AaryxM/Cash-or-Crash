import random

# --- Recipes Dictionary 
recipes = {
    "Mango Smoothie": ["mango", "milk", "ice"],
    "Lemonade": ["lemon", "sugar", "water"],
    "Iced Tea": ["tea", "ice", "lemon"]
}

# --- Generate Random Order
def get_random_order():
    #Return a random drink name from recipes.
    return random.choice(list(recipes.keys()))

# --- Check Correctness ---
def check_order(drink, chosen_ingredients):
    """Compare chosen ingredients with recipe."""
    return set(recipes[drink]) == set(chosen_ingredients)

# --- Update Balance ---
def update_balance(balance, success):
    """Update balance based on correctness."""
    if success:
        return balance + 10   # earn coins
    else:
        return balance - 5    # lose coins

# --- End of Day Rent ---
def end_day(balance, rent=30):
    """Deduct rent and return net balance."""
    return balance - rent

# --- Summary Stats ---
def get_summary(orders):
    """
    orders = list of dicts like:
    [{"drink":"Mango Smoothie","success":True}, ...]
    """
    total = len(orders)
    correct = sum(1 for o in orders if o["success"])
    wrong = total - correct
    return {
        "total_orders": total,
        "correct_orders": correct,
        "wrong_orders": wrong
    }
