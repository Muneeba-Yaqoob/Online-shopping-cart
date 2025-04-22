import datetime
import os
import json
from abc import ABC, abstractmethod
from tabulate import tabulate


class Product:

    def __init__(self, product_id, name, price, description, stock):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.description = description
        self.stock = stock

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "stock": self.stock
        }

    @staticmethod
    def from_dict(data):
        return Product(
            data['product_id'],
            data['name'],
            data['price'],
            data['description'],
            data['stock']
        )


class Cart:

    def __init__(self):
        self.items = []

    def add_to_cart(self, product, quantity):
        if product.stock >= quantity:
            self.items.append((product, quantity))
            product.stock -= quantity
            print(f"{product.name} added to cart.")
        else:
            print(f"Sorry, only {product.stock} items in stock.")

    def remove_from_cart(self, product_id):
        for item in self.items:
            if item[0].product_id == product_id:
                item[0].stock += item[1]
                self.items.remove(item)
                print(f"{item[0].name} removed from cart.")
                return
        print("Product not found in cart.")

    def view_cart(self):
        total_price = 0
        print(
            "---------------------------------------------------------------------------------------------------------------------")
        print("                                           ***** Your Cart *****")
        print(
            "---------------------------------------------------------------------------------------------------------------------")
        for product, quantity in self.items:
            print(f"{product.name} - ${product.price} x {quantity}")
            total_price += product.price * quantity
        print(f"Total Price: ${total_price}")
        print(
            "---------------------------------------------------------------------------------------------------------------------")

    def clear_cart(self):
        self.items = []

    def to_dict(self):
        return {
            "items": [(item[0].to_dict(), item[1]) for item in self.items]
        }

    @staticmethod
    def from_dict(data, products):
        cart = Cart()
        for item_data in data['items']:
            product = next((p for p in products if p.product_id == item_data[0]['product_id']), None)
            if product:
                cart.items.append((product, item_data[1]))
        return cart


class OrderHistory:

    def __init__(self):
        self.history = []

    def add_purchase(self, purchase):
        self.history.append(purchase)

    def view_history(self):
        print(
            "---------------------------------------------------------------------------------------------------------------------")
        print("                                          ***** Your Purchase History *****")
        print(
            "---------------------------------------------------------------------------------------------------------------------")
        for purchase in self.history:
            print(f"Date: {purchase['date']}")
            for item in purchase['items']:
                print(f"{item[0]} - ${item[2]} x {item[1]}")
            print(f"Total Price: ${purchase['total_price']}")
            print(f"Feedback: {purchase['feedback']}")
        print(
            "---------------------------------------------------------------------------------------------------------------------")

    def to_dict(self):
        return {
            "history": self.history
        }

    @staticmethod
    def from_dict(data):
        history = OrderHistory()
        history.history = data['history']
        return history


class Person(ABC):

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @abstractmethod
    def to_dict(self):
        pass

    @staticmethod
    @abstractmethod
    def from_dict(data):
        pass


class User(Person):

    def __init__(self, first_name, last_name, address, username, password):
        super().__init__(username, password)
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.cart = Cart()
        self.saved_cart = Cart()
        self.order_history = OrderHistory()

    def add_to_cart(self, product, quantity):
        try:
            self.cart.add_to_cart(product, quantity)
        except Exception as e:
            print(f"Error adding product to cart: {e}")

    def view_cart(self):
        try:
            self.cart.view_cart()
        except Exception as e:
            print(f"Error viewing cart: {e}")

    def remove_from_cart(self, product_id):
        try:
            self.cart.remove_from_cart(product_id)
        except Exception as e:
            print(f"Error removing product from cart: {e}")

    def save_cart(self):
        try:
            self.saved_cart.items = self.cart.items[:]
            self.cart.clear_cart()
            print("\nCart saved for later access.")
        except Exception as e:
            print(f"Error saving cart: {e}")

    def load_saved_cart(self):
        try:
            if not self.saved_cart.items:
                print("\nNo saved cart found.")
            else:
                self.cart.items = self.saved_cart.items[:]
                self.saved_cart.clear_cart()
                print("\nSaved cart loaded.")
        except Exception as e:
            print(f"Error loading saved cart: {e}")

    def checkout(self):
        try:
            if not self.cart.items:
                print("\n*** YOUR CART IS EMPTY ***")
                return

            total_price = 0
            items = []
            for product, quantity in self.cart.items:
                items.append((product.name, quantity, product.price * quantity))
                total_price += product.price * quantity

            print("\nPlease enter your payment details:")
            while True:
                card_number = input("Credit Card Number: ")
                if card_number.isdigit() and len(card_number) == 13:
                    break
                else:
                    print("Invalid card number. It should be a 13-digit integer.")

            while True:
                expiry_date = input("Expiry Date (MMYY): ")
                if expiry_date.isdigit() and len(expiry_date) == 4:
                    break
                else:
                    print("Invalid expiry date. It should be a 4-digit integer.")

            while True:
                cvv = input("CVV: ")
                if cvv.isdigit() and len(cvv) == 3:
                    cvv = int(cvv)
                    break
                else:
                    print("Invalid CVV. It should be a 3-digit integer.")
            print("\nPlease confirm your address:")
            print(self.address)
            confirm = input("Is the above address correct? (yes/no): ")

            if confirm.lower() == "yes":
                feedback = input("\nPlease provide your feedback on our service: ")
                print("\nThank you for your feedback!")

                purchase = {
                    "date": datetime.datetime.now().isoformat(),
                    "items": items,
                    "total_price": total_price,
                    "feedback": feedback
                }
                self.order_history.add_purchase(purchase)
                self.cart.clear_cart()
                self.save_purchase_history()
            else:
                print("\nCheckout cancelled.")
        except Exception as e:
            print(f"Error during checkout: {e}")

    def save_purchase_history(self, filename="purchases.txt"):
        try:
            with open(filename, 'a') as file:
                for purchase in self.order_history.history:
                    file.write(
                        f"{purchase['date']},{purchase['items']},{purchase['total_price']},{purchase['feedback']}\n")
        except Exception as e:
            print(f"Error saving purchase history: {e}")

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "username": self.username,
            "password": self.password,
            "cart": self.cart.to_dict(),
            "saved_cart": self.saved_cart.to_dict(),
            "order_history": self.order_history.to_dict()
        }

    @staticmethod
    def from_dict(data, products):
        user = User(data['first_name'], data['last_name'], data['address'], data['username'], data['password'])
        user.cart = Cart.from_dict(data['cart'], products)
        user.saved_cart = Cart.from_dict(data['saved_cart'], products)
        user.order_history = OrderHistory.from_dict(data['order_history'])
        return user

    @staticmethod
    def display_products(products):
        headers = ["ID", "Name", "Price ($)", "Description", "Stock"]
        product_data = [[p.product_id, p.name, p.price, p.description, p.stock] for p in products]
        print(tabulate(product_data, headers=headers, tablefmt="grid"))


class Admin(Person):

    def __init__(self, username, password):
        super().__init__(username, password)

    def view_products(self, products):
        headers = ["ID", "Name", "Price ($)", "Description", "Stock"]
        product_data = [[p.product_id, p.name, p.price, p.description, p.stock] for p in products]
        print(tabulate(product_data, headers=headers, tablefmt="grid"))

    def add_product(self, products):
        name = input("Enter product name: ")

        while True:
            try:
                price = float(input("Enter product price: "))
                break
            except ValueError:
                print("Invalid input. Please enter a valid number for the price.")

        description = input("Enter product description: ")

        while True:
            try:
                stock = int(input("Enter stock quantity: "))
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer for the stock quantity.")

        product_id = max([p.product_id for p in products], default=0) + 1
        product = Product(product_id, name, price, description, stock)
        products.append(product)
        print("\nProduct added successfully.")


    def remove_product(self, products):
        while True:
            try:
                product_id = int(input("Enter product ID to remove: "))
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer for the product ID.")

        products = [p for p in products if p.product_id != product_id]
        print("\nProduct removed successfully.")
        return products



    def modify_product(self, products):
        while True:
            try:
                product_id = int(input("Enter product ID to modify: "))
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer for the product ID.")

        product = next((p for p in products if p.product_id == product_id), None)

        if product:
            name = input(f"Enter new name (current: {product.name}): ") or product.name

            while True:
                try:
                    price_input = input(f"Enter new price (current: {product.price}): ") or product.price
                    price = float(price_input)
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid number for the price.")

            description = input(f"Enter new description (current: {product.description}): ") or product.description

            while True:
                try:
                    stock_input = input(f"Enter new stock quantity (current: {product.stock}): ") or product.stock
                    stock = int(stock_input)
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the stock quantity.")

            product.name = name
            product.price = price
            product.description = description
            product.stock = stock
            print("\nProduct modified successfully.")
        else:
            print("\nProduct not found.")

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password
        }

    @staticmethod
    def from_dict(data):
        return Admin(data['username'], data['password'])



class ShoppingCartApp:

    def __init__(self):
        self.products = [Product(1, "Laptop", 999.99, "A high-performance laptop.", 10),
                         Product(2, "Smartphone", 499.99, "A latest model smartphone.", 20),
                         Product(3, "Headphones", 199.99, "Noise-cancelling headphones.", 15),
                         Product(4, "Smartwatch", 299.99, "A smartwatch with various features.", 25),
                         Product(5, "Camera", 599.99, "A digital camera with high resolution.", 5),
                         Product(6, "Tablet", 399.99, "A tablet with a large display.", 8),
                         Product(7, "Printer", 149.99, "A wireless printer.", 12),
                         Product(8, "Monitor", 249.99, "A 4K monitor.", 7),
                         Product(9, "Keyboard", 79.99, "A mechanical keyboard.", 18),
                         Product(10, "Mouse", 49.99, "A wireless mouse.", 22),
                         Product(11, "VR Headset", 399.99, "A virtual reality headset", 5),
                         Product(12, "Drone", 499.99, "A high-performance drone with 4K camera.", 7),
                         Product(13, "Portable SSD", 149.99, "A 1TB portable SSD.", 18),
                         Product(14, "Smart Doorbell", 179.99, "A smart doorbell with video camera", 8),
                         Product(15, "Wireless Earbuds", 149.99, "Noise-cancelling wireless earbuds.", 17)]
        self.users = self.load_users()
        self.admins = self.load_admins()
        self.current_user = None
        self.current_admin = None
        self.ensure_admin()

    def ensure_admin(self):
        if not any(admin.username == "Maria" for admin in self.admins):
            self.admins.append(Admin("Maria", "maria123"))
            self.save_admins()

    def load_products(self):
        if not os.path.exists("products.json"):
            return []
        with open("products.json", "r") as file:
            return [Product.from_dict(p) for p in json.load(file)]

    def save_products(self):
        with open("products.json", "w") as file:
            json.dump([p.to_dict() for p in self.products], file, indent=4)

    def load_users(self):
        if not os.path.exists("users.json"):
            return []
        with open("users.json", "r") as file:
            return [User.from_dict(u, self.products) for u in json.load(file)]

    def save_users(self):
        with open("users.json", "w") as file:
            json.dump([u.to_dict() for u in self.users], file, indent=4)

    def load_admins(self):
        if not os.path.exists("admins.json"):
            return []
        with open("admins.json", "r") as file:
            return [Admin.from_dict(a) for a in json.load(file)]

    def save_admins(self):
        with open("admins.json", "w") as file:
            json.dump([a.to_dict() for a in self.admins], file, indent=4)

    def register_user(self):
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        address = input("Address: ")
        username = input("Username: ")
        password = input("Password: ")
        user = User(first_name, last_name, address, username, password)
        self.users.append(user)
        self.save_users()
        print("\nUser registered successfully.")

    def login_user(self):
        username = input("Username: ")
        password = input("Password: ")
        user = next((u for u in self.users if u.username == username and u.password == password), None)
        if user:
            self.current_user = user
            print(f"\nWelcome {self.current_user.first_name} {self.current_user.last_name}")

        else:
            print("\nInvalid username or password.")

    def login_admin(self):
        username = input("Admin Username: ")
        password = input("Admin Password: ")
        admin = next((a for a in self.admins if a.username == username and a.password == password), None)
        if admin:
            self.current_admin = admin
            print(f"\nWelcome Admin {self.current_admin.username}")

        else:
            print("\nInvalid admin username or password.")

    def user_menu(self):
        print("==============================================================================")
        print("      ***************** WELCOME TO USER MENU *****************")
        print("==============================================================================")
        while self.current_user:
            print("\n1. View Products")
            print("2. Add to Cart")
            print("3. View Cart")
            print("4. Remove from Cart")
            print("5. Save Cart")
            print("6. Load Saved Cart")
            print("7. Checkout")
            print("8. View Purchase History")
            print("9. Logout")
            choice = input("Enter your choice: ")
            if choice == "1":
                self.current_user.display_products(self.products)
            elif choice == "2":
                try:
                    product_id = int(input("Enter product ID: "))
                    quantity = int(input("Enter quantity: "))
                    product = next((p for p in self.products if p.product_id == product_id), None)
                    if product:
                        self.current_user.add_to_cart(product, quantity)
                    else:
                        print("Product not found.")
                except ValueError:
                    print("Invalid input.")
            elif choice == "3":
                self.current_user.view_cart()
            elif choice == "4":
                try:
                    product_id = int(input("Enter product ID to remove: "))
                    self.current_user.remove_from_cart(product_id)
                except ValueError:
                    print("Invalid input.")
            elif choice == "5":
                self.current_user.save_cart()
            elif choice == "6":
                self.current_user.load_saved_cart()
            elif choice == "7":
                self.current_user.checkout()
            elif choice == "8":
                self.current_user.order_history.view_history()
            elif choice == "9":
                self.current_user = None
                self.save_users()
                print("SUCCESSFULLY LOGGED OUT !")
            else:
                print("\nInvalid choice. Please try again.")

    def admin_menu(self):
        print("==============================================================================")
        print("      ***************** WELCOME TO ADMIN MENU *****************")
        print("==============================================================================")
        while self.current_admin:
            print("\n1. View Products")
            print("2. Add Product")
            print("3. Remove Product")
            print("4. Modify Product")
            print("5. Logout")
            choice = input("Enter your choice: ")
            if choice == "1":
                self.current_admin.view_products(self.products)
            elif choice == "2":
                self.current_admin.add_product(self.products)
                self.save_products()
            elif choice == "3":
                self.products = self.current_admin.remove_product(self.products)
                self.save_products()
            elif choice == "4":
                self.current_admin.modify_product(self.products)
                self.save_products()
            elif choice == "5":
                self.current_admin = None
                print("\nLogged out successfully.")
            else:
                print("\nInvalid choice. Please try again.")

    def main_menu(self):
        print("\nMESSAGE: The admin is Maria and the admin password is maria123\n\n ")
        print("==============================================================================")
        print("      ***************** WELCOME TO OUR SHOPPING CENTRE *****************")
        print("==============================================================================")
        print("Explore our wide range of products and enjoy a seamless shopping experience!")
        print("==============================================================================")
        try:
            while True:
                print("1. Register as User")
                print("2. Login as User")
                print("3. Login as Admin")
                print("4. Exit")
                choice = input("Enter your choice: ")
                if choice == "1":
                    self.register_user()
                elif choice == "2":
                    self.login_user()
                    if self.current_user:
                        self.user_menu()
                elif choice == "3":
                    self.login_admin()
                    if self.current_admin:
                        self.admin_menu()
                elif choice == "4":
                    self.save_users()
                    print("==============================================================================")
                    print("                 THANK YOU FOR SHOPPING. HAVE A NICE DAY!!!")
                    print("==============================================================================")
                    break
                else:
                    print("\nInvalid choice. Please try again.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.save_users()


if __name__ == "__main__":
    app = ShoppingCartApp()
    app.main_menu()



