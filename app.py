import os
from flask import Flask, render_template, session, redirect, url_for, g, request
from flask_session import Session
from database import get_db, close_db
from forms import LoginForm, RegistrationForm, SortForm, ContactForm, DiscountForm, AddProductForm, RemoveProductForm, UpdateProductForm, AddImageToProductForm, UpdateImageForm, EditDiscountForm, ChangePasswordForm, ActivitiesSortForm, AccessScoutGroupForm, BookActivityForm, WriteProductReviewForm, AddActivityForm, CancelActivityForm, ActivitiesAdminSortForm, ProductSalesSortForm, AddEventForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import date, datetime
import string
import random

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "083mrg1904"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1000 * 1000    # 4MB - max size of file uploads
Session(app)




# ~~~~~~~~~~ SMALL NOTES ~~~~~~~~~~~~

# The web app has 3 main things: a small shop with scout products, an outdoors activity booking tool and a private area where scout members can see upcoming events.
# As there is no payment process, when you buy a product/book an activity, that step is bypassed and pretends that the user has paid the full price or the booking fee.
# Active shop discount codes (You can see and change them in the admin account too)
        # 'SPRING_23' - 10% OFF
        # 'SCOUT_NEW' - 25% OFF
        # '1MSC0UTER' - 15% OFF

# My recommendation Derek is to first explore as a regular user, then access as an admin and look around (here is where most interesting functions are), and last you can use the daily access codes in the admin account page to activate the first user and become a scout member.

# To access as an admin:
"""
        Username: admin
        Password: hermes123
"""

# LASTLY, I leave here 10 things that might not be seen on a first look but that I did go around to make it work in a specific way:

'''

    1. The shop always orders the items by most popular (monthly sales are being tracked in the database).
        - This means that even if the user selects to sort by price, it still displays items in order of popularity according to the sales on top of the order by price).

    2. The monthly sales being tracked happens when any user enters the shop. It checks if the current month is a new one compared to the last record in the database. If it is, it transfer all the sales data for that month into the database table "product_sales" and resets the count for monthly sales to 0 for every product.
        - As it's hard to prove this on the school server as we cannot change it's time and date, it can be done running the flask app in your pc and manually changing the month. Note: This function considers that the shop is accessed at least once every month.

    3. You can log in with both the user_id or the email. User_id will be used across the site regardless to refer to the user.

    4. If you click to buy a product and you aren't logged in, the item(s) you wanted to buy will appear in the cart when you log in. This will prevent having to go back searching to add the products again.

    5. The admin can delete products from the database AND delete the image files associated with them in the hard disk. If the image file is the default "no_image_available", this won't be performed.

    6. Now, if the user wants to delete a product's image from the system that more than one product shares, the program fetches all those products from the database and updates them with the "no_image_available" path so they always have an image displayed.

    7. There are multiple instances like this where the program is checking for different user input possibilities and amends the outcome. Other examples: 
            - If a product doesn't have stock, the buy button doesn't appear in the product page. But this could be bypassed writing add_to_cart/<product_id> in the url if the user knows the product id. Even like that, the product won't be added to the cart.
            - Similarly happens when the user has already added all available products in stock into the cart. He won't be able and a message will tell him so (I've added a lot of messages to give feedback to the user and make navigation more intuitive).
            - If you type a URL that only is allowed for admin or a scout member or a leader (ie. accessing "add_product" path as a regular user), the site tells the regular user that the area is forbidden unless you have that type of account.
            - In the same way, if a user types "cancel_activity/10", it could cancel another person's activity. Instead, it checks that the user is the one who booked that activity before continuing. If it is not his booking, he is redirected to the activities page.

    8. When deleting a product from the shop as an admin, there is actually a "soft delete" happening. I used a history table in the database to save the product details when removed so that they can still appear in the user order history. This way, the order details aren't lost if a product is removed from the shop.

    9. You can only review products that you have bought. And you can only review a product once.
    
    10. Scout access codes are randomized each day so they cannot be easily transferable (inspired but Wordle, but here I don't get the codes from a text file but they are randomly generated. And there is no seed, they are stored in the database.). These codes can be found in the admin or scout leader account. Once a user registers, he can use the code to access the scouts member sections for his group.

'''




@app.before_request
def logged_in_user():
    g.user = session.get("user_id", None)

@app.before_request
def user_role():
    g.user_role = session.get("user_role", None)

@app.before_request
def scout_role():
    g.scout_role_id = session.get("scout_role_id", None)

@app.before_request
def scout_role():
    g.scout_group = session.get("scout_group", None)

@app.before_request
def cart_total():
    g.cart = session.get("cart_total", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

def scout_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user_role < 2:
            return redirect(url_for("login", message="The area you are trying to access requires a scout member account. Login with one to access.", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

def scout_leader_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.scout_role_id != 4:
            return redirect(url_for("login", message="The area you are trying to access requires a scout leader or Admin account. Login with one to access.", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user_role != 3:
            return redirect(url_for("login",  message="The area you are trying to access requires an ADMIN account. Login with one to access.", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

#function to validate the extension of the image file wanting to be uploaded by the admin
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_admin():
    db = get_db()
    password = "hermes123"
    clashing_admin = db.execute("""SELECT * FROM users
                                    WHERE user_id = 'admin';""").fetchone()
    if clashing_admin is None:
        db.execute("""INSERT INTO users (user_id, password, email, role_id, scout_role_id)
                    VALUES ('admin', ?, 'admin@bigadventure.com', 3, 4);""", (generate_password_hash(password),))
        db.commit()
    return

@app.route("/home")
@app.route("/")
def index():
    random_access_codes()
    db = get_db()
    items = db.execute("""SELECT * FROM shop ORDER BY RANDOM() LIMIT 4;""").fetchall()
    return render_template("index.html", title="Home", items=items)

@app.route("/login", methods=["GET", "POST"])
def login():
    create_admin()
    form = LoginForm()
    message = request.args.get("message")
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        possible_clashing_user = db.execute("""SELECT * FROM users
                                               WHERE user_id = ? or email = ?;""", (user_id, user_id)).fetchone()
        if possible_clashing_user is None:
            form.user_id.errors.append("User doesn't exist.")
        elif not check_password_hash(possible_clashing_user["password"], password):
            form.password.errors.append("Incorrect password.")
        else:
            user_id = possible_clashing_user["user_id"] #in case logged in with email, assign the user_id
            try:    # if cart session created previously, save the contents in a variable to recover when logged in
                cart = session["cart"]
                cart_total = session["cart_total"]
            finally:
                session.clear()
                session["user_id"] = user_id    # Adds the user id to the session. You are logged in while your user_id is part of the session.
                session["user_role"] = possible_clashing_user["role_id"]
                session["scout_role_id"] = possible_clashing_user["scout_role_id"]
                scout_group = db.execute("""SELECT scout_roles.name 
                                            FROM scout_roles, users 
                                            WHERE users.user_id = ? AND users.scout_role_id=scout_roles.scout_role_id;""", (user_id,)).fetchone()
                if scout_group:
                    session["scout_group"] = scout_group["name"]
                try:
                    session["cart"] = cart
                    session["cart_total"] = cart_total
                finally:
                    next_page = request.args.get("next")
                    if not next_page:
                        next_page = url_for("account")
                    return redirect(next_page)
    return render_template("login.html", form=form, title="Login", message=message)


@app.route("/register", methods=["GET","POST"])
def register():
    create_admin()
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        password2 = form.password2.data
        email = form.email.data
        email2 = form.email2.data
        db = get_db()
        clashing_user = db.execute("""SELECT * FROM users
                                      WHERE user_id = ?;""", (user_id,)).fetchone()
        clashing_email = db.execute("""SELECT * FROM users
                                       WHERE email = ?;""", (email,)).fetchone()
        if clashing_user is not None:
            form.user_id.errors.append("User id clashes with another")
        elif clashing_email is not None:
            form.email.errors.append("Email already exists")
        else:
            db.execute("""INSERT INTO users (user_id, password, email, role_id)
                            VALUES (?, ?, ?, 1);""", (user_id, generate_password_hash(password), email)) 
            db.commit()
            return redirect( url_for("login") )
    return render_template("register.html", form=form, title="Register")

@app.route("/logout")
def logout():
    session.clear()
    return redirect( url_for("index"))

@app.route("/account", methods=["GET","POST"])
@login_required
def account():
    return render_template("account.html", tittle="Account")


@app.route("/activities", methods=["GET", "POST"])
def activities():
    form = ActivitiesSortForm()
    db = get_db()
    activities = db.execute("""SELECT * FROM activities WHERE capacity > 0 ORDER BY date""").fetchall()
    category_choices_dict = db.execute("""SELECT DISTINCT category FROM activities""").fetchall()
    choices = ["ALL"]
    for row in category_choices_dict:
        choices.append((row["category"]))
    form.category.choices = choices
    if form.validate_on_submit():
        from_date = form.from_date.data
        to_date = form.to_date.data
        category = form.category.data
        adults = form.adults.data
        if from_date <= date.today():
            form.from_date.errors.append("Date must be in the future")
        elif to_date <= from_date:
            form.to_date.errors.append("Date must be later than first date")
        elif to_date <= date.today():
            form.to_date.errors.append("Date must be in the future")
        elif category == "ALL":
            activities = db.execute("""SELECT * FROM activities WHERE date < ? and date > ? and capacity >= ? ORDER BY date;""", (to_date, from_date, adults)).fetchall()
        else:
            activities = db.execute("""SELECT * FROM activities WHERE date < ? and date > ? and category = ? and capacity >= ? ORDER BY date;""", (to_date, from_date, category, adults)).fetchall()
    return render_template("activities.html", form=form, title="Activities", activities=activities)


@app.route("/book_activity/<int:activity_id>", methods=["GET", "POST"])
@login_required
def book_activity(activity_id):
    form = BookActivityForm()
    db = get_db()
    activity = db.execute("""SELECT * FROM activities WHERE activity_id = ?;""", (activity_id,)).fetchone()
    # Limit the choices to the max places left in the activity
    choices = []
    for number in range(1, 9):
        if number <= activity["capacity"]:
            choices.append(number)
        else:
            break
    booking_fee = round(activity["price"] * 0.30, 1)
    form.adults.choices = choices
    if form.validate_on_submit():
        adults = form.adults.data
        confirmation = form.confirmation.data
        updated_capacity = activity["capacity"] - int(adults)
        db.execute("""INSERT INTO booked_activities (activity_id, user_id, quantity, booking_fee, booking_date)
                      VALUES (?,?,?,?,?);""", (activity_id, session["user_id"], adults, booking_fee, date.today()))
        db.commit()
        db.execute("""UPDATE activities SET capacity = ? WHERE activity_id = ?;""", (updated_capacity, activity_id))
        db.commit()
        return redirect(url_for("booked_activities", title="Booked activities", message="Your activity has been booked! We are looking forward to seeing you!"))
    return render_template("book_activity.html", title="Book activity", form=form, activity=activity, booking_fee=booking_fee)


@app.route("/contact", methods=["GET","POST"])
def contact():
    form = ContactForm()
    message = request.args.get("message")
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        subject = form.subject.data
        form_message = form.message.data
        preference = form.preference.data
        actual_date = date.today()
        if subject == "":
            form.subject.errors.append("Subject required")
        else:
            if preference == True:
                preference = "Phone call"
            else:
                preference = "Unspecified"
            db = get_db()
            db.execute("""INSERT INTO contact (date, name, email, phone, subject, message,  preference)
                            VALUES (?, ?, ?, ?, ?, ?, ?);""", (actual_date, name, email, phone, subject, form_message, preference)) 
            db.commit()
            return redirect(url_for("contact", message="Thanks for you message! We will get back to you as soon as we can."))
    return render_template("contact_form.html", form=form, title="Contact", message=message)

def initialize_cart():
    #Starts the session set of cookies related to the shop cart.
    if "cart" not in session:
        session["cart"] = {}
    if "cart_total" not in session:
        session["cart_total"] = 0
    if "discount" not in session:
        session["discount"] = 0
    return

@app.route("/shop", methods=["GET", "POST"])
def shop():
    form = SortForm()
    initialize_cart()
    record_month_sales()
    db = get_db()
    items = db.execute("""SELECT * FROM shop ORDER BY month_sales DESC;""").fetchall()

    #Set the search bar choices for category and colour
    colour_choices_dict = db.execute("""SELECT DISTINCT colour FROM shop ORDER BY colour;""").fetchall()
    choices = ["ALL"]
    for row in colour_choices_dict:
        choices.append((row["colour"]))
    form.colour.choices = choices
    category_choices_dict = db.execute("""SELECT DISTINCT category FROM shop ORDER BY category;""").fetchall()
    choices = ["ALL"]
    for row in category_choices_dict:
        choices.append((row["category"]))
    form.category.choices = choices

    if form.validate_on_submit():
        search = form.search.data
        if search:
            search = "%" + search + "%"
        order = form.sort.data
        colour = form.colour.data
        category = form.category.data
        items = sort_shop(order, colour, category, search)
    return render_template("shop.html", form=form, title="Shop", items=items)


#Function definition to record month sales to database when we are in new month.
def record_month_sales():
    db = get_db()
    # Get the last date recorded in the sales table of the database
    last_date = db.execute("""SELECT date FROM product_sales ORDER BY date DESC;""").fetchone()
    # Date to string understanding https://www.programiz.com/python-programming/datetime/strftime
    # Increase the month of that date by 1 to get an updated date.
    year = last_date["date"].strftime("%Y")
    month = last_date["date"].strftime("%m")
    month = int(month) + 1
    if month == 13:
        month = "01"
        year = int(year) + 1
        updated_last_date = str(year) + "-" + month
    elif month < 10:
        month = "0" + str(month)
        updated_last_date = year + "-" + month
    else:
        updated_last_date = year + "-" + str(month)
    current_year_month = date.today().strftime("%Y-%m")
    print(current_year_month)
    print(updated_last_date)

    # Check if the updated date isn't the same as the date right now.
    if updated_last_date != current_year_month:
        #Add the first day of the month to be able to insert it into the sales table.
        updated_last_date = updated_last_date + "-01"

        all_products = db.execute("""SELECT product_id, month_sales FROM shop;""").fetchall()
        for product in all_products:
                db.execute("""INSERT INTO product_sales (product_id, sales, date)
                              VALUES (?, ?, ?);""", (product["product_id"], product["month_sales"], updated_last_date))
                db.commit()
        db.execute("""UPDATE shop SET month_sales = 0;""") #reset all month sales to 0.
        db.commit()
    return

@app.route("/product/<int:product_id>")
def product(product_id):
    db = get_db()
    product = db.execute("""SELECT * FROM shop WHERE product_id = ?;""", (product_id,)).fetchone()
    if not product:
        message = "This product doesn't exist."
        return render_template("product.html", message=message)
    message = ""
    mean_rating = ""
    flag_half_star = ""
    available_stock = product["stock"]
    if available_stock == 0:
        message = "No units left. Come back soon!"
    elif available_stock <= 15:
        message = "Only %s units left!" % available_stock

    #Show 5 more products below product
    items = db.execute("""SELECT * FROM shop WHERE product_id != ? ORDER BY RANDOM() LIMIT 5;""", (product_id,)).fetchall()

    product_reviews = db.execute("""SELECT * FROM product_reviews WHERE product_id = ?""", (product_id,)).fetchall()
    
    total_reviews = len(product_reviews)
    if total_reviews > 0:
        ratings = []
        for review in product_reviews:
            ratings.append(review["rating"])
        mean_rating = mean(ratings)
        #validation for mean rating, setting flag for printing a half star if mean rating is not a whole number
        flag_half_star = mean_rating.is_integer()
        mean_rating = int(mean_rating)

    return render_template("product.html", title=product["name"], product=product, items=items, message=message, available_stock=available_stock, product_reviews=product_reviews, mean_rating=mean_rating, flag_half_star=flag_half_star, total_reviews=total_reviews)

# Calculate mean - Function borrowed from introduction lecture of semester 2
def mean(numbers):
    sum = 0
    size = len(numbers)
    for n in numbers:
        sum = sum + n
    return sum / size

@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    form = DiscountForm()
    initialize_cart()
    message = request.args.get("message")
    products = {}
    discount = 0
    price_sum = 0   #sum of all items in cart
    discounted_price = 0    #price after applying discount to price_sum
    SHIPPING_COST = 3.99
    free_delivery = False
    db = get_db()
    for product_id in session["cart"]:
        product = db.execute("""SELECT * FROM shop WHERE product_id = ?;""", (product_id,)).fetchone()
        product_price = product["price"]
        products[product_id] = product
        price_sum = price_sum + product_price * session["cart"][product_id]
    price_sum = round(price_sum, 2)
    final_price = price_sum

    if session["discount"] != 0:
        discounted_price = discount_calc(price_sum, session["discount"])
        final_price = discounted_price
        if discounted_price < 30:
            final_price = round(discounted_price + SHIPPING_COST, 2)
        else:
            free_delivery = True
    else:
        if final_price < 30:
            final_price = round(final_price + SHIPPING_COST, 2)
        else:
            free_delivery = True

    if form.validate_on_submit():
        discount = form.discount.data
        possible_clashing_discount = db.execute("""SELECT * FROM shop_discount WHERE discount_id = ?""", (discount,)).fetchone()
        if possible_clashing_discount is None:
            form.discount.errors.append("Code not valid")
        else:
            session["discount"] =  possible_clashing_discount["percentage_off"]
            discounted_price = discount_calc(price_sum, session["discount"])
            final_price = discounted_price
            if discounted_price < 30:
                final_price = round(discounted_price + SHIPPING_COST, 2)
                free_delivery = False
    session["cart_prices"] = {"price_sum":price_sum, "discounted_price":discounted_price, "final_price":final_price}
    if free_delivery == True:
        session["cart_prices"]["shipping_cost"] = 0
    else:
        session["cart_prices"]["shipping_cost"] = SHIPPING_COST
    return render_template("cart.html", form=form, title="Cart", message=message, cart=session["cart"], products=products, cart_prices=session["cart_prices"], discount=session["discount"], free_delivery=free_delivery)

def discount_calc(price, discount_percentage):
    discounted_price = price - (discount_percentage * price / 100)
    discounted_price = round(discounted_price, 2)
    return discounted_price

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    initialize_cart()
    db = get_db()
    product = db.execute("""SELECT * FROM shop WHERE product_id = ?;""", (product_id,)).fetchone()
    available_stock = product["stock"]
    if (product_id in session["cart"] and available_stock <= session["cart"][product_id]) or available_stock == 0:
        return redirect(url_for("cart", message="No more units in stock. Looks like you have the last ones in your cart."))
    elif product_id not in session["cart"]:
        session["cart"][product_id] = 1
        session["cart_total"] = session["cart_total"] + 1
    else:
        session["cart"][product_id] = session["cart"][product_id] + 1
        session["cart_total"] = session["cart_total"] + 1
    return redirect(url_for("cart"))

@app.route("/remove_from_cart/<int:product_id>")
@login_required
def remove_from_cart(product_id):
    if product_id in session["cart"]:
        session["cart_total"] = session["cart_total"] - session["cart"][product_id]
        cart = session.get("cart", {})
        cart.pop(product_id, None)  
        session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/remove_discount")
@login_required
def remove_discount():
    session["discount"] = 0
    return redirect(url_for("cart"))

@app.route("/increase_product/<int:product_id>")
@login_required
def increase_product(product_id):
    db = get_db()
    product = db.execute("""SELECT * FROM shop WHERE product_id = ?;""", (product_id,)).fetchone()
    available_stock = product["stock"]
    if available_stock <= session["cart"][product_id]:
        return redirect(url_for("cart", message="No more units in stock. Looks like you have the last ones in your cart."))
    else:
        session["cart_total"] += 1
        session["cart"][product_id] += 1
    return redirect(url_for("cart"))

@app.route("/decrease_product/<int:product_id>")
@login_required
def decrease_product(product_id):
    session["cart_total"] -= 1
    session["cart"][product_id] -= 1
    if session["cart"][product_id] == 0:
        return redirect(url_for("remove_from_cart", product_id=product_id))
    return redirect(url_for("cart"))

@app.route("/payment")
@login_required
def payment():
    if session["cart_total"] == 0:
            return render_template("cart.html")
    db = get_db()
    user_id = session["user_id"]
    order_date = date.today()
    discount = session["discount"]
    if discount == 0:
        discount = "None"
    shipping_cost = session["cart_prices"]["shipping_cost"]
    total_price = session["cart_prices"]["final_price"]
    shipment_status = "Pending shipment"
    #Insert order into orders table in database.
    db.execute("""INSERT INTO orders (user_id, order_date, discount, shipping_cost, total_price, shipment_status)
                VALUES (?, ?, ?, ?, ?, ?);""", (user_id, order_date, discount, shipping_cost, total_price, shipment_status))
    db.commit()

    # Get the order id.
    order = db.execute("""SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1""").fetchone()
    order_id = order["order_id"]

    # Iterate through products in cart to get details of the order
    for product_id in session["cart"]:
        product = db.execute("""SELECT * FROM shop WHERE product_id = ?;""", (product_id,)).fetchone()
        product_quantity = session["cart"][product_id]
        product_price_sum = round(product_quantity * product["price"], 2)
        # Insert order details into database.
        db.execute("""INSERT INTO order_details (order_id, product_id, product_quantity, product_price_sum)
                    VALUES (?, ?, ?, ?);""", (order_id, product_id, product_quantity, product_price_sum ))
        db.commit()
        # Update stock of product.
        updated_stock = product["stock"] - session["cart"][product_id]
        db.execute("""UPDATE shop SET stock = ? WHERE product_id = ?;""", (updated_stock, product_id))
        db.commit()
        # Update monthly sales for product
        updated_sales = product["month_sales"] + session["cart"][product_id]
        db.execute("""UPDATE shop SET month_sales = ? WHERE product_id = ?;""", (updated_sales, product_id))
        db.commit()


    message = "Payment processed correctly. Your order will be posted as soon as we implement a real payment service ;)"
    # Clear the cart contents and cart total:
    session["cart"].clear()
    session["cart_total"] = 0
    session["discount"] = 0

    return redirect(url_for("order_history", message=message))



# GENERAL USER ACCOUNT ROUTES

@app.route("/account_config", methods=["GET", "POST"])
@login_required
def account_config():
    form = ChangePasswordForm()
    message = ""
    if form.validate_on_submit():
        old_password = form.old_password.data
        new_password = form.new_password.data
        new_password2 = form.new_password2.data
        user_id = session.get("user_id")
        db = get_db()
        user = db.execute("""SELECT * FROM users WHERE user_id = ?;""", (user_id,)).fetchone()
        if check_password_hash(user["password"], old_password) == False:
            form.old_password.errors.append("The password doesn't match the current password")
        elif check_password_hash(user["password"], new_password):
            form.new_password.errors.append("The entered password is the same as the current one.")
        else:
            db.execute("""UPDATE users SET password = ? WHERE user_id = ?;""", (generate_password_hash(new_password), user_id))
            db.commit()
            message = "Password updated"
    return render_template("account_config.html", title="Account config.", form=form, message=message)


@app.route("/order_history", methods=["GET", "POST"])
@login_required
def order_history():
    message = request.args.get("message")
    user_id = session["user_id"]
    db = get_db()
    # Fetch all orders (order_id) done by this user.
    order_id_list = db.execute("""SELECT order_id FROM orders WHERE user_id = ?""", (user_id,)).fetchall()
    order_id_list.reverse()
    # Fetch all items inside tables (shop, orders and order_details) for each order_id and add to a dictionary.
    order_dict = {}
    counter = 0
    while counter < len(order_id_list):
        product_details = db.execute("""SELECT orders.order_id, orders.order_date, shop.name, shop.colour, shop.price, details.product_quantity, details.product_price_sum, orders.discount, orders.shipping_cost, orders.total_price, orders.shipment_status, orders.shipment_date
                            FROM orders, order_details AS details, shop
                            WHERE orders.order_id = details.order_id AND details.product_id = shop.product_id
                            and orders.order_id = ?;""", (order_id_list[counter]),).fetchall()
        order_dict[order_id_list[counter]] = product_details
        counter += 1

    counter = 0
    # CHeck if products in order appearing in deleted_products table. If so, add them into the dictionary with the products that are already in the order_id list
    while counter < len(order_id_list):
        product_details_deleted_product = db.execute("""SELECT orders.order_id, orders.order_date, deleted.name, deleted.colour, deleted.price, details.product_quantity, details.product_price_sum, orders.discount, orders.shipping_cost, orders.total_price, orders.shipment_status, orders.shipment_date
                            FROM orders, order_details AS details, deleted_products AS deleted
                            WHERE (orders.order_id = details.order_id) and details.product_id = deleted.product_id
                            and orders.order_id = ? 
                            ORDER BY orders.order_id DESC""", (order_id_list[counter]),).fetchall()
        print(product_details_deleted_product)
        if len(product_details_deleted_product) != 0:
            order_dict[order_id_list[counter]].extend(product_details_deleted_product)
        counter += 1

    return render_template("order_history.html", title="Order history", order_dict=order_dict, order_id_list=order_id_list, message=message)

@app.route("/user_product_reviews", methods=["GET", "POST"])
@login_required
def user_product_reviews():
    form = WriteProductReviewForm()
    message = request.args.get("message")
    db = get_db()
    user_id = session["user_id"]
    user_reviews = db.execute("""SELECT shop.name, reviews.product_id, reviews.review_title, reviews.review, reviews.rating, reviews.date, reviews.review_id
                                 FROM product_reviews AS reviews, shop
                                 WHERE shop.product_id=reviews.product_id AND user_id = ?;""", (user_id,)).fetchall()
    total_reviews = len(user_reviews)

    #Select products bought by the user that hasn't been yet reviewed by user.
    not_reviewed_products = db.execute("""SELECT shop.name
                                          FROM shop, orders, order_details AS ord_det
                                          WHERE (orders.order_id = ord_det.order_id) AND (shop.product_id = ord_det.product_id) AND 
                                                orders.user_id = ? 
                                          EXCEPT
                                          SELECT shop.name
                                          FROM product_reviews AS reviews, shop
                                          WHERE shop.product_id=reviews.product_id AND user_id = ?;""", (user_id, user_id)).fetchall()
    product_choices = [""]
    for row in not_reviewed_products:
        product_choices.append((row["name"]))
    form.bought_product.choices = product_choices

    if form.validate_on_submit():
        bought_product = form.bought_product.data
        rating = form.rating.data
        title = form.title.data
        review = form.review.data

        product = db.execute("""SELECT * FROM shop WHERE name = ?;""", (bought_product,)).fetchone()

        db.execute("""INSERT INTO product_reviews (user_id, product_id, rating, date, review_title, review)
                      VALUES (?,?,?,?,?,?);""", (user_id, product["product_id"], rating, date.today(), title, review))
        db.commit()
        return redirect(url_for("user_product_reviews", message="Review submitted. Thanks!"))
    return render_template("user_product_reviews.html", title="Written reviews", form=form, message=message, user_reviews=user_reviews, total_reviews=total_reviews, product_choices=product_choices)

@app.route("/delete_review/<int:review_id>")
@login_required
def delete_review(review_id):
    db = get_db()
    db.execute("""DELETE FROM product_reviews WHERE review_id = ?;""", (review_id,))
    db.commit()
    return redirect(url_for("user_product_reviews"))

@app.route("/booked_activities")
@login_required
def booked_activities():
    message = request.args.get("message")
    db = get_db()
    user_id = session["user_id"]
    today = date.today()
    booked_activities = db.execute("""SELECT *
                                      FROM activities AS act, booked_activities AS b_act
                                      WHERE act.activity_id = b_act.activity_id AND user_id = ? AND act.date >= ? 
                                      ORDER BY date ASC;""", (user_id, today)).fetchall()
    
    past_activities = db.execute("""SELECT *
                                    FROM activities AS act, booked_activities AS b_act
                                    WHERE act.activity_id = b_act.activity_id AND user_id = ? AND act.date < ?
                                    ORDER BY date DESC;""", (user_id, today)).fetchall()
    
    return render_template("booked_activities.html", title="Booked activities", message=message, booked_activities=booked_activities, past_activities=past_activities)


@app.route("/cancel_activity/<int:booking_id>", methods=["GET", "POST"])
@login_required
def cancel_activity(booking_id):
    form = CancelActivityForm()
    db = get_db()
    user_id = session["user_id"]
    activity = db.execute("""SELECT * FROM activities, booked_activities
                             WHERE activities.activity_id = booked_activities.activity_id AND booked_activities.booking_id = ? AND booked_activities.user_id = ?;""", (booking_id, user_id)).fetchone()
    if activity is None:
        return redirect(url_for("activities"))
    if form.validate_on_submit():
        confirmation = form.confirmation.data
        db.execute("""DELETE FROM booked_activities WHERE booking_id = ?;""", (booking_id,))
        db.commit()
        db.execute("""UPDATE activities SET capacity = ?
                      WHERE activity_id = ?;""", (activity["capacity"] + activity["quantity"], activity["activity_id"]))
        db.commit()
        return redirect(url_for("booked_activities", message="Activity canceled. We are sorry that you can't attend and we hope to see you in the future."))
    return render_template ("cancel_activity.html", title="Cancel activity", form=form, activity=activity)

@app.route("/scout_group_access", methods=["GET", "POST"])
@login_required
def scout_group_access():
    form = AccessScoutGroupForm()
    if form.validate_on_submit():
        code = form.code.data
        db = get_db()
        all_codes = db.execute("""SELECT * FROM scout_codes;""").fetchall()
        user_id = session["user_id"]
        count = 0
        for activation_code in all_codes:
            if activation_code["code"] == code:
                print(count)
                db.execute("""UPDATE users SET scout_role_id = ?, role_id = 2
                              WHERE user_id = ?;""", (activation_code["scout_role_id"], user_id))
                db.commit()
                session["user_role"] = 2
                session["scout_role_id"] = activation_code["scout_role_id"]
                scout_role = db.execute("""SELECT name FROM scout_roles
                                           WHERE scout_role_id = ?;""", (activation_code["scout_role_id"],)).fetchone()
                session["scout_group"] = scout_role["name"]
                scout_role = scout_role["name"].upper()
                return redirect(url_for("welcome_note"))
            else:
                count += 1
                print("final count", count)
        if count == 5:
            form.code.errors.append("Code not valid")
    return render_template("scout_group_access.html", title="Access to Scout Group", form=form)




# MEMBER GROUP ROUTES

@app.route("/welcome_note")
@scout_required
def welcome_note():
    db = get_db()
    scout_role = db.execute("""SELECT name FROM scout_roles
                            WHERE scout_role_id = ?;""", (session["scout_role_id"],)).fetchone()
    scout_role = scout_role["name"].upper()
    return render_template("welcome_note.html", title="Welcome to the group!", scout_role=scout_role)

@app.route("/events_upcoming")
@scout_required
def events_upcoming():
    db = get_db()
    future_events = db.execute("""SELECT events.name, events.date , events.time
                                  FROM events, event_details AS details
                                  WHERE events.event_id = details.event_id AND details.scout_role_id = ? AND date > ? 
                                  ORDER BY DATE;""", (session["scout_role_id"], date.today())).fetchall()
    return render_template("events_upcoming.html", title="Events administration", future_events=future_events)

@app.route("/events_past")
@scout_required
def events_past():
    db = get_db()
    past_events = db.execute("""SELECT * 
                                FROM events, event_details AS details
                                WHERE events.event_id = details.event_id AND details.scout_role_id = ? AND date <= ? 
                                ORDER BY DATE;""", (session["scout_role_id"], date.today())).fetchall()
    return render_template("events_past.html", title="Events administration", past_events=past_events)

# LEADER GROUP ROUTES

@app.route("/leader_access_codes")
@scout_leader_required
def leader_access_codes():
    random_access_codes()
    db = get_db()
    today_access_codes = db.execute("""SELECT scout_codes.code, scout_roles.name 
                                        FROM scout_codes, scout_roles 
                                        WHERE scout_roles.scout_role_id = scout_codes.scout_role_id and scout_codes.scout_role_id != 4""").fetchall()
    return render_template("leader_access_codes.html", title="Access codes", today_access_codes=today_access_codes)

@app.route("/admin_events")
@scout_leader_required
def admin_events():
    message = request.args.get("message")
    db = get_db()
    future_events = db.execute("""SELECT details.details_id, events.name, events.date, events.time, scout_roles.name AS scout_group
                                  FROM events, event_details AS details, scout_roles
                                  WHERE events.event_id = details.event_id AND date > ? AND scout_roles.scout_role_id = details.scout_role_id
                                  ORDER BY DATE;""", (date.today(),)).fetchall()
    
    return render_template("admin_events.html", title="Events administration", future_events=future_events, message=message)

@app.route("/delete_event/<int:details_id>")
@scout_leader_required
def delete_event(details_id):
    db = get_db()
    db.execute("""DELETE FROM event_details WHERE details_id = ?;""", (details_id,))
    db.commit()
    return redirect(url_for("admin_events", message="Event deleted for that group."))

@app.route("/add_event", methods=["GET", "POST"])
@scout_leader_required
def add_event():
    form = AddEventForm()
    db = get_db()
    message = request.args.get("message")
    
    if form.validate_on_submit():
        date = form.date.data
        time = form.time.data
        name = form.name.data
        group = form.group.data

        #Error validation:
        if date <= date.today():
            form.date.errors.append("Select a future date")
        if not form.errors:
            time_formatted = time.strftime("%H:%M:%S")
            db.execute("""INSERT INTO events (date, time, name) 
                    VALUES (?,?,?);""", (date, time_formatted, name))
            db.commit()
            event = db.execute("""SELECT event_id FROM events ORDER BY event_id DESC LIMIT 1""").fetchone()
            scout_groups_dict = {"Beaver":0, "Cub":1, "Scout":2, "Venture":3}
            for scout_group in group:
                scout_role_id = scout_groups_dict[scout_group]
                db.execute("""INSERT INTO event_details (event_id, scout_role_id) 
                              VALUES (?,?);""", (event["event_id"], scout_role_id))
                db.commit()
            return redirect(url_for("add_event", message="Event added successfully."))
    return render_template("add_event.html", form=form, title="Events administration", message=message)

# ADMIN ROUTES

@app.route("/admin_delete_review/<int:review_id><int:product_id>")
@admin_required
def admin_delete_review(review_id, product_id):
    db = get_db()
    db.execute("""DELETE FROM product_reviews WHERE review_id = ?;""", (review_id,))
    db.commit()
    return redirect(url_for("product", product_id=product_id))


@app.route("/outstanding_orders")
@admin_required
def outstanding_orders():
    db = get_db()
    # Fetch all orders (order_id) done by this user.
    order_id_list = db.execute("""SELECT order_id FROM orders WHERE shipment_status = 'Pending shipment';""").fetchall()
    # Fetch all items inside tables (shop, orders and order_details) for each order_id and add to a dictionary.
    order_dict = {}
    counter = 0
    while counter < len(order_id_list):
        product_details = db.execute("""SELECT orders.order_id, orders.user_id, orders.order_date, shop.name, shop.colour, shop.price, details.product_quantity, details.product_price_sum, orders.discount, orders.shipping_cost, orders.total_price
                                        FROM orders, order_details AS details, shop
                                        WHERE orders.order_id = details.order_id AND details.product_id = shop.product_id
                                        and orders.order_id = ?;""", (order_id_list[counter]),).fetchall()
        order_dict[order_id_list[counter]] = product_details
        counter += 1

    counter = 0
    # Check if products in order appearing in deleted_products table. If so, add them into the dictionary with the products that are already in the order_id list
    while counter < len(order_id_list):
        product_details_deleted_product = db.execute("""SELECT orders.order_id, orders.user_id, orders.order_date, deleted.name, deleted.colour, deleted.price, details.product_quantity, details.product_price_sum, orders.discount, orders.shipping_cost, orders.total_price
                                                        FROM orders, order_details AS details, deleted_products AS deleted
                                                        WHERE (orders.order_id = details.order_id) and details.product_id = deleted.product_id
                                                        and orders.order_id = ? 
                                                        ORDER BY orders.order_id DESC""", (order_id_list[counter]),).fetchall()
        
        if len(product_details_deleted_product) != 0:
            order_dict[order_id_list[counter]].extend(product_details_deleted_product)
        counter += 1

    return render_template("outstanding_orders.html", order_dict=order_dict, order_id_list=order_id_list)

@app.route("/shipped_orders", methods=["GET", "POST"])
@admin_required
def shipped_orders():
    db = get_db()
    # Fetch all orders (order_id) done by this user.
    order_id_list = db.execute("""SELECT order_id FROM orders WHERE shipment_status = 'Shipped' ORDER BY shipment_date DESC, order_id DESC;""").fetchall()
    # Fetch all items inside tables (shop, orders and order_details) for each order_id and add to a dictionary.
    order_dict = {}
    counter = 0
    while counter < len(order_id_list):
        product_details = db.execute("""SELECT orders.order_id, orders.user_id, orders.order_date, shop.name, shop.colour, shop.price, details.product_quantity, details.product_price_sum, orders.discount, orders.shipping_cost, orders.total_price, orders.shipment_date
                                        FROM orders, order_details AS details, shop
                                        WHERE orders.order_id = details.order_id AND details.product_id = shop.product_id
                                        and orders.order_id = ?;""", (order_id_list[counter]),).fetchall()
        order_dict[order_id_list[counter]] = product_details
        counter += 1

    counter = 0
    #CHeck if products in order appearing in deleted_products table. If so, add them into the dictionary with the products that are already in the order_id list
    while counter < len(order_id_list):
        product_details_deleted_product = db.execute("""SELECT orders.order_id, orders.user_id, orders.order_date, deleted.name, deleted.colour, deleted.price, details.product_quantity, details.product_price_sum, orders.discount, orders.shipping_cost, orders.total_price, orders.shipment_date
                                                        FROM orders, order_details AS details, deleted_products AS deleted
                                                        WHERE (orders.order_id = details.order_id) and details.product_id = deleted.product_id
                                                        and orders.order_id = ? 
                                                        ORDER BY orders.order_id DESC""", (order_id_list[counter]),).fetchall()
        
        if len(product_details_deleted_product) != 0:
            order_dict[order_id_list[counter]].extend(product_details_deleted_product)
        counter += 1

    return render_template("shipped_orders.html", order_dict=order_dict, order_id_list=order_id_list)


@app.route("/update_order_status/<int:order_id>")
@admin_required
def update_order_status(order_id):
    db = get_db()
    db.execute("""UPDATE orders SET shipment_status = 'Shipped', shipment_date = ? WHERE order_id = ?;""", (date.today(), order_id))
    db.commit()
    return redirect(url_for('outstanding_orders'))

@app.route("/add_product", methods=["GET", "POST"])
@admin_required
def add_product():
    form = AddProductForm()
    image_path = ""
    db = get_db()
    category_choices_dict = db.execute("""SELECT DISTINCT category FROM shop""").fetchall()
    cat_choices = [""]
    for row in category_choices_dict:
        cat_choices.append((row["category"]))
    form.category.choices = cat_choices
    colour_choices_dict = db.execute("""SELECT DISTINCT colour FROM shop""").fetchall()
    col_choices = [""]
    for row in colour_choices_dict:
        col_choices.append((row["colour"]))
    form.colour.choices = col_choices

    if form.validate_on_submit():
        name = form.name.data
        category = form.category.data
        other_category = form.other_category.data
        price = form.price.data
        colour = form.colour.data
        other_colour = form.other_colour.data
        description = form.description.data
        stock = form.stock.data

        # Error validation:
        if not (form.category.data or form.other_category.data):
            form.other_category.errors.append("*No category details, please fill one box.")
        elif form.category.data and form.other_category.data:
            form.other_category.errors.append("*Fill only ONE category box.")
        if not (form.colour.data or form.other_colour.data):
            form.other_colour.errors.append("*No colour details, please fill one box.")
        elif form.colour.data and form.other_colour.data:
            form.other_colour.errors.append("*Fill only ONE colour box.")

        if not form.errors:
            if other_colour:
                colour = other_colour
            if other_category:
                category = other_category
            image_path = "no_image_available.png"
            # Database insertion
            db.execute("""INSERT INTO shop (name, category, price, colour, description, image_path, stock, month_sales) 
                    VALUES (?,?,?,?,?,?,?, 0);""", (name, category, price, colour, description, image_path, stock))
            db.commit()
            # Search in the database for the id of the inserted product to pass it on to the add_image_to_product route
            product = db.execute("""SELECT * FROM shop ORDER BY product_id DESC LIMIT 1;""").fetchone()
            product_id = product["product_id"]
            return redirect(url_for("add_image_to_product", product_id=product_id))
    return render_template("add_product.html", form=form, title="Shop management")

@app.route("/add_image_to_product/<int:product_id>", methods=["GET", "POST"])
@admin_required
def add_image_to_product(product_id):
    form = AddImageToProductForm()
    form2 = AddProductForm()   #to redirect to add_product page
    message = ""
    image_path = ""
    db = get_db()

    if form.validate_on_submit():
        #Upload image file. #://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
        file = form.file.data
        if 'file' in request.files:     
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
                    # Database insertion of image path
                db.execute("""UPDATE shop SET image_path = ? WHERE product_id = ?""", (image_path, product_id))
                db.commit()
                message = "The product has been updated with the image."
                return render_template("add_product.html", form=form2, title="Shop management", message=message)
            elif allowed_file(file.filename) == False:
                form.file.errors.append("*File not found or format not valid")
                return render_template("add_image_to_product.html", form=form)
            
    return render_template("add_image_to_product.html", form=form, title="Shop management", message=message)

@app.route("/update_remove_product", methods=["GET", "POST"])
@admin_required
def update_remove_product():
    return render_template("update_remove_product.html", Title="Shop administration")

@app.route("/remove_product_confirmation/<int:product_id>", methods=["GET", "POST"])
@admin_required
def remove_product_confirmation(product_id):
    form = RemoveProductForm()
    db = get_db()
    product = db.execute("""SELECT * FROM shop WHERE product_id = ?""", (product_id,)).fetchone()
    if not product:
        message = "The product you want to remove doesn't exist."
        return render_template("update_remove_product.html", message=message, Title="Shop management")
    if form.validate_on_submit():
        confirmation = form.confirmation.data
        image_removal = form.image_removal.data
        if image_removal is True:   # User wants image file to be removed
            product = db.execute("""SELECT * FROM shop WHERE product_id = ?;""", (product_id,)).fetchone()
            image_filename = product["image_path"]
            if image_filename != "no_image_available.png":      # Prevents deleting default no_image_available file for products without an image
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                    # Look for other products that had this image (if any) and change that for "no_available_image.jpg"
                    db.execute("""UPDATE shop SET image_path = "no_image_available.png" WHERE image_path = ?;""", (image_filename,))
                    db.commit()
                finally:    #ERROR: FILE NOT EXISTENT ( PROBABLY DELETED PREVIOUSLY THROUGH THIS FORM or DELETED OR MOVED FROM FOLDER)
                    pass
        db.execute("""INSERT INTO deleted_products (product_id, name, category, price, colour, description, image_path, month_sales) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?);""", (product["product_id"], product["name"], product["category"], product["price"], product["colour"], product["description"], product["image_path"], product["month_sales"]))
        db.commit()
        db.execute("""DELETE FROM shop WHERE product_id = ?;""", (product_id,))
        db.commit()
        message = "The product has been successfully deleted from the database."
        if product_id in session["cart"]:  #we remove from cart in session too so the site doesn't crash if the cart is visited and the eliminated product was in in the session cart.
            remove_from_cart(product_id)
        return render_template("update_remove_product.html", message=message, Title="Shop management")
    return render_template("remove_product_confirmation.html", form=form, product=product, Title="Remove product")


@app.route("/update_product_form/<int:product_id>", methods=["GET", "POST"])
@admin_required
def update_product_form(product_id):
    form = UpdateProductForm()
    form2 = UpdateImageForm()
    message = ""
    message_stock = ""
    db = get_db()
    product = db.execute("""SELECT * FROM shop WHERE product_id = ?""", (product_id,)).fetchone()
    if not product:
        message = "The product you want to update doesn't exist."
        return render_template("update_remove_product.html", message=message, Title="Shop management")
    category_choices_dict = db.execute("""SELECT DISTINCT category FROM shop""").fetchall()
    cat_choices = [""]
    for row in category_choices_dict:
        cat_choices.append((row["category"]))
    form.category.choices = cat_choices
    colour_choices_dict = db.execute("""SELECT DISTINCT colour FROM shop""").fetchall()
    col_choices = [""]
    for row in colour_choices_dict:
        col_choices.append((row["colour"]))
    form.colour.choices = col_choices

    if form.validate_on_submit() and form.submit1.data:   # Admin wanting to update product's information
        name = form.name.data
        category = form.category.data
        other_category = form.other_category.data
        price = form.price.data
        colour = form.colour.data
        other_colour = form.other_colour.data
        description = form.description.data
        stock = form.stock.data

        # Error validation:
        if form.category.data and form.other_category.data:
            form.other_category.errors.append("*Fill only ONE category box.")
        if form.colour.data and form.other_colour.data:
            form.other_colour.errors.append("*Fill only ONE colour box.")

        if not form.errors:     # All form fields are optional (therefore no InputRequired() validation). Only execute the following if no errors from category or colour clashing
            
            if other_colour:
                colour = other_colour
            if other_category:
                category = other_category
                
            # Database update. Save in a dictionary the attributes in the sql database as keys, and the value of the key is the variable's value from the user form submitted
            my_dict = {}
            if form.name.data:
                my_dict["name"] = name
            if form.category.data or form.other_category.data:
                my_dict["category"] = category
            if form.price.data:
                my_dict["price"] = price
            if form.colour.data or form.other_colour.data:
                my_dict["colour"] = colour
            if form.description.data:
                my_dict["description"] = description
            if form.stock.data:
                my_dict["stock"] = stock
            if len(my_dict) != 0:
                for key, value in my_dict.items():
                    db.execute(f"""UPDATE shop SET {key} = ? WHERE product_id = ?;""", (value, product_id))
                    db.commit()
                    message = "Product updated correctly"
            else:
                message = "ERROR: The submitted form is empty"

    elif form2.validate_on_submit() and form2.submit2.data:   # Admin wanting to update image
        file = form2.file.data
        #Upload image file.
        if 'file' in request.files:     
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
                    # Database insertion of image path
                db.execute("""UPDATE shop SET image_path = ? WHERE product_id = ?;""", (image_path, product_id))
                db.commit()
                message = "The product has been updated with the image."
            elif allowed_file(file.filename) == False:
                form2.file.errors.append("No file submitted/wrong format")
    product = db.execute("""SELECT * FROM shop WHERE product_id = ?;""" ,(product_id,)).fetchone()
    return render_template("update_product_form.html", form=form, form2=form2, title="Shop management", product=product, message=message, message_stock=message_stock)

@app.route("/discount_management", methods=["GET", "POST"])
@admin_required
def discount_management():
    form = EditDiscountForm()
    message = ""
    found_discount = False
    db = get_db()
    all_discount_codes = db.execute("""SELECT * FROM shop_discount;""").fetchall()

    if form.validate_on_submit():
        discount_id = form.discount_id.data
        percentage_off = form.percentage_off.data
        add_submit = form.add_submit.data
        delete_submit = form.delete_submit.data
        update_submit = form.update_submit.data
        discount_id = discount_id.upper()

        for discount in all_discount_codes:
            if discount["discount_id"] == discount_id:
                found_discount = True
                break

        if form.add_submit.data:
            if len(discount_id) != 9:
                form.discount_id.errors.append("Length of code has to be 9 characters")
            elif percentage_off is None:
                form.percentage_off.errors.append("This field is required")
            elif found_discount == True:
                form.discount_id.errors.append("Can't add discount: already in list. If wanting to update that discount press Update submit button.")
            else:
                db.execute("""INSERT INTO shop_discount (discount_id, percentage_off)
                            VALUES (?, ?);""", (discount_id, percentage_off))
                db.commit()
                message = "Discount added"

        elif form.delete_submit.data:
            if found_discount == True:
                db.execute("""DELETE FROM shop_discount WHERE discount_id = ?;""", (discount_id,))
                db.commit()
                message = "Discount removed"
            else:
                form.discount_id.errors.append("Name of discount not found")
        
        elif form.update_submit.data:
            if percentage_off is None:
                form.percentage_off.errors.append("New percentage is needed to update the discount code")
            if found_discount == True:
                db.execute("""UPDATE shop_discount SET percentage_off = ? WHERE discount_id = ?;""", (percentage_off, discount_id))
                db.commit()
                message = "Discount updated"
            else:
                form.discount_id.errors.append("Name of discount not found")
    all_discount_codes = db.execute("""SELECT * FROM shop_discount""").fetchall()
    return render_template("discount_management.html", form=form, title="Shop administration", all_discount_codes=all_discount_codes, message=message)

@app.route("/contact_forms_review")
@admin_required
def contact_forms_review():
    db = get_db()
    contact_forms = db.execute("""SELECT * FROM contact ORDER BY contact_id DESC;""").fetchall()
    return render_template("contact_forms_review.html", title="Contact forms", contact_forms=contact_forms)

@app.route("/remove_contact_form/<int:contact_id>")
@admin_required
def remove_contact_form(contact_id):
    db = get_db()
    db.execute("""DELETE FROM contact WHERE contact_id = ?;""", (contact_id,))
    db.commit()
    contact_forms = db.execute("""SELECT * FROM contact ORDER BY contact_id DESC;""").fetchall()
    return render_template("contact_forms_review.html", contact_forms=contact_forms)

@app.route("/admin_access_codes")
@admin_required
def admin_access_codes():
    random_access_codes()
    db = get_db()
    today_access_codes = db.execute("""SELECT scout_codes.code, scout_roles.name 
                                       FROM scout_codes, scout_roles 
                                       WHERE scout_roles.scout_role_id = scout_codes.scout_role_id;""").fetchall()
    return render_template("admin_access_codes.html", title="Access codes", today_access_codes=today_access_codes)


@app.route("/admin_activities", methods=["GET", "POST"])
@admin_required
def admin_activities():
    form = ActivitiesAdminSortForm()
    message = request.args.get("message")
    db = get_db()
    activities_dict = {}
    activities = db.execute("""SELECT * FROM activities;""").fetchall()
    for activity in activities:
        bookings = db.execute("""SELECT * FROM booked_activities WHERE activity_id = ?;""", (activity["activity_id"],)).fetchall()
        if bookings:
            activities_dict[activity["activity_id"]] = bookings
    category_choices_dict = db.execute("""SELECT DISTINCT category FROM activities;""").fetchall()
    choices = ["ALL"]
    for row in category_choices_dict:
        choices.append((row["category"]))
    form.category.choices = choices
    if form.validate_on_submit():
        from_date = form.from_date.data
        to_date = form.to_date.data
        category = form.category.data
        booking = form.booking.data
        if from_date <= date.today():
            form.from_date.errors.append("Date must be in the future")
        elif to_date <= from_date:
            form.to_date.errors.append("Date must be later than first date")
        elif to_date <= date.today():
            form.to_date.errors.append("Date must be in the future")
        elif category == "ALL":
            if form.booking.data: #select not booked activities
                activities = db.execute("""SELECT * FROM activities
                                           WHERE activity_id NOT IN (SELECT DISTINCT activity_id FROM booked_activities)
                                           AND date < ? AND date > ? 
                                           ORDER BY date;""", (to_date, from_date)).fetchall()
            else:   #all activities
                activities = db.execute("""SELECT * FROM activities
                                           WHERE date < ? AND date > ? 
                                           ORDER BY date;""", (to_date, from_date)).fetchall()
        else:
            if form.booking.data:   #select not booked activities (by selected category)
                activities = db.execute("""SELECT * FROM activities
                                           WHERE activity_id NOT IN (SELECT DISTINCT activity_id FROM booked_activities)
                                           AND date < ? AND date > ? 
                                           AND category = ?
                                           ORDER BY date;""", (to_date, from_date, category)).fetchall()
            else:   #all activities (by category)
                activities = db.execute("""SELECT * FROM activities
                                           WHERE date < ? AND date > ? 
                                           AND category = ?
                                           ORDER BY date;""", (to_date, from_date, category)).fetchall()
    return render_template("admin_activities.html", form=form, title="Activities administration", activities=activities, activities_dict=activities_dict, message=message)


@app.route("/add_activity", methods=["GET", "POST"])
@admin_required
def add_activity():
    form = AddActivityForm()
    db = get_db()
    message = request.args.get("message")
    category_choices_dict = db.execute("""SELECT DISTINCT category FROM activities;""").fetchall()
    cat_choices = [""]
    for row in category_choices_dict:
        cat_choices.append((row["category"]))
    form.category.choices = cat_choices

    if form.validate_on_submit():
        name = form.name.data
        date = form.date.data
        category = form.category.data
        other_category = form.other_category.data
        difficulty = form.difficulty.data
        capacity = form.capacity.data
        price = form.price.data

        #Error validation:
        if not (form.category.data or form.other_category.data):
            form.other_category.errors.append("*No category details, please fill one box.")
        elif form.category.data and form.other_category.data:
            form.other_category.errors.append("*Fill only ONE category box.")
        if difficulty == "":
            form.difficulty.errors.append("Select a difficulty")
        if date <= date.today():
            form.date.errors.append("Select a future date")
        if not form.errors:
            if other_category:
                category = other_category
            db.execute("""INSERT INTO activities (name, date, category, difficulty, capacity, price) 
                    VALUES (?,?,?,?,?,?);""", (name, date, category, difficulty, capacity, price))
            db.commit()
            return redirect(url_for("add_activity", message="Activity added successfully."))
    return render_template("add_activity.html", form=form, title="Activities administration", message=message)

@app.route("/product_sales", methods=["GET", "POST"])
@admin_required
def product_sales():
    db = get_db()
    form = ProductSalesSortForm()
    products = db.execute("""SELECT * FROM shop;""").fetchall()
    choices = ["ALL"]
    for product in products:
        choice = str(product["product_id"]) + " - " + product["name"]
        choices.append(choice)
    form.product_select.choices = choices

    sales_dict = {}
    product_details = ""
    product_sales = ""
    if form.validate_on_submit():
        product = form.product_select.data
        words = product.split()
        product_id = words[0]
        product_details = db.execute("""SELECT * FROM shop WHERE product_id = ?;""", (product_id,)).fetchone()
        product_sales = db.execute("""SELECT * FROM product_sales WHERE product_id = ? ORDER BY date DESC;""", (product_id,)).fetchall()

    return render_template("product_sales.html", title="Product sales", form=form, sales_dict=sales_dict, product_details=product_details, product_sales=product_sales)


@app.route("/delete_activity/<int:activity_id>", methods=["GET", "POST"])
@admin_required
def delete_activity(activity_id):
    db = get_db()
    db.execute("""DELETE FROM activities WHERE activity_id = ?;""", (activity_id,))
    db.commit()
    return redirect(url_for("admin_activities", message="Activity deleted"))



# Function to every day create random access codes to the scout group
def random_access_codes():
    db = get_db()
    saved_date = db.execute("""SELECT date FROM scout_codes LIMIT 1""").fetchone()
    today = date.today()
    if saved_date["date"] != today:
        #set starting of code to scout role initial letters
        scout_role = ['BEA-','CUB-','SCO-','VEN-','LEA-']
        # Create character pool to build random code from letters, digits and 3 special characters. Digits appear double in pool to get more chances to appear (as letters are repeated: lowercase and uppercase)
        char_pool = list(string.ascii_letters)
        char_pool.extend(string.digits)
        char_pool.extend(['?','#','_','&'])
        char_pool.extend(string.digits)
        char_pool.remove('l') #lowercase L ("l") and capital I not differentiable easily with actual font so they are both removed
        char_pool.remove('I')
        # Iterate 5 times to produce 5 codes, 1 for each scout role
        for i in range(5):
            # set in
            random_string = scout_role[i]
            for number in range(8):
                random_string = random_string + random.choice(char_pool)
            db.execute("""UPDATE scout_codes SET code = ?, date = ?
                            WHERE scout_role_id = ?;""", (random_string, today, i))
            db.commit()
    return

# Function definition that sorts the shop products
def sort_shop(order, colour, category, search):
    db = get_db()
    if colour == "ALL":     #Only "sort by" input
        if category == "ALL":
            if search:
                if order == "Most popular":
                    items = db.execute("""SELECT * FROM shop WHERE name LIKE ? ORDER BY month_sales DESC""", (search,)).fetchall()
                elif order == "Lowest price":
                    items = db.execute("""SELECT * FROM shop WHERE name LIKE ? ORDER BY price, month_sales DESC""", (search,)).fetchall()
                else:  #Highest price
                    items = db.execute("""SELECT * FROM shop WHERE name LIKE ? ORDER BY price DESC, month_sales DESC""", (search,)).fetchall()
            else:   #no search
                if order == "Most popular":
                    items = db.execute("""SELECT * FROM shop ORDER BY month_sales DESC""").fetchall()
                elif order == "Lowest price":
                    items = db.execute("""SELECT * FROM shop ORDER BY price, month_sales DESC""").fetchall()
                else:  #Highest price
                    items = db.execute("""SELECT * FROM shop ORDER BY price DESC, month_sales DESC""").fetchall()
    if colour == "ALL":     #Category and "sort by" input
        if category != "ALL":
            if search:
                if order == "Most popular":
                    items = db.execute("""SELECT * FROM shop WHERE category = ? and name LIKE ? ORDER BY month_sales DESC""", (category, search)).fetchall()
                elif order == "Lowest price":
                    items = db.execute("""SELECT * FROM shop WHERE category = ? and name LIKE ? ORDER BY price, month_sales DESC""", (category, search)).fetchall()
                else:  #Highest price
                    items = db.execute("""SELECT * FROM shop WHERE category = ? and name LIKE ? ORDER BY price DESC, month_sales DESC""", (category, search)).fetchall()
            else:   #no search
                if order == "Most popular":
                    items = db.execute("""SELECT * FROM shop WHERE category = ? ORDER BY month_sales DESC""", (category,)).fetchall()
                elif order == "Lowest price":
                    items = db.execute("""SELECT * FROM shop WHERE category = ? ORDER BY price, month_sales DESC""", (category,)).fetchall()
                else:  #Highest price
                    items = db.execute("""SELECT * FROM shop WHERE category = ? ORDER BY price DESC, month_sales DESC""", (category,)).fetchall()
    if colour != "ALL":     #Colour and "sort by" input
        if category == "ALL":
            if search:
                if order == "Most popular":
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? and name LIKE ? ORDER BY month_sales DESC""", (colour, search)).fetchall()
                elif order == "Lowest price":
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? and name LIKE ? ORDER BY price, month_sales DESC""", (colour, search)).fetchall()
                else:  #Highest price
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? and name LIKE ?  ORDER BY price DESC, month_sales DESC""", (colour, search)).fetchall()
            else:   # no search
                if order == "Most popular":
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? ORDER BY month_sales DESC""", (colour,)).fetchall()
                elif order == "Lowest price":
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? ORDER BY price, month_sales DESC""", (colour,)).fetchall()
                else:  #Highest price
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? ORDER BY price DESC, month_sales DESC""", (colour,)).fetchall()
    if colour != "ALL":     #All 3 inputs: category, colour and "sort by"
        if category != "ALL":
            if search:
                if order == "Most popular":
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? and name LIKE ? and category = ? ORDER BY month_sales DESC""", (colour, search, category)).fetchall()
                elif order == "Lowest price":
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? and name LIKE ? and category = ? ORDER BY price, month_sales DESC""", (colour, search, category)).fetchall()
                else:  #Highest price
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? and name LIKE ? and category = ? ORDER BY price DESC, month_sales DESC""", (colour, search, category)).fetchall()
            else: #no search
                if order == "Most popular":
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? and category = ? ORDER BY month_sales DESC""", (colour, category)).fetchall()
                elif order == "Lowest price":
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? and category = ? ORDER BY price, month_sales DESC""", (colour, category)).fetchall()
                else:  #Highest price
                    items = db.execute("""SELECT * FROM shop WHERE colour = ? and category = ? ORDER BY price DESC, month_sales DESC""", (colour, category)).fetchall()
    return items