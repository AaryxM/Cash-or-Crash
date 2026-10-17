import random

# --- Recipes Dictionary 
# recipes = {
#     "Citrus Harmony": ["orange", "lemon", "sugar", "mint"],
#     "Sweet Sunrise" : ["orange", "watermelon", "sugar"],
#     "Lemon Spark" : ["lemon", "sugar", "mint", "ice"],
#     "Citrus Burst" : ["orange", "lemon", "ice", "mint"],
#     "Mint Whisper" : ["mint", "water", "sugar", "ice"],
#     "Orange Cream" : ["orange", "milk", "ice"],
#     "Lemon Cream" : ["lemon", "milk", "ice"],
#     "Cold water" : ["water", "ice"],
#     "Orange Splash" : ["orange", "ice", "water"],
#     "Lemonade": ["lemon", "sugar", "water"],
# }
recipes = {
    "Citrus Harmony": {
        "ingredients": ["orange", "lemon", "sugar", "mint"],
        "price": 16
    },
    "Sweet Sunrise": {
        "ingredients": ["orange", "watermelon", "sugar"],
        "price": 12
    },
    "Lemon Spark": {
        "ingredients": ["lemon", "sugar", "mint", "ice"],
        "price": 16
    },
    "Orange Cream": {
        "ingredients": ["orange", "milk", "ice"],
        "price": 14
    },
    "Lemon Cream": {
        "ingredients": ["lemon", "milk", "ice"],
        "price": 14
    },
    "Cold Water": {
        "ingredients": ["water", "ice"],
        "price": 4
    }
}

# --- Generate Random Order
def get_random_order():
    #Return a random drink name from recipes.
    return random.choice(list(recipes.keys()))

#Check if correct order
def check_order(drink, chosen_ingredients):
    return set(recipes[drink]["ingredients"]) == set(chosen_ingredients)



    
def update_balance(balance, drink, success):
    if success:
        return balance + recipes[drink]["price"]
    else:
        return balance - recipes[drink]["price"] * 0.5   # penalty stays fixed, or make it per-drink too


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

#temporary 
if __name__ == "__main__":
    drink = get_random_order()
    print("Customer ordered:", drink)

    ingredients = recipes[drink]
    print("Required ingredients:", ingredients)

    result = check_order(drink, ingredients)
    print("Correct:", result)

    balance = 100
    balance = update_balance(balance, result)
    print("Balance after order:", balance)

    balance = end_day(balance)
    print("Balance after rent:", balance)
