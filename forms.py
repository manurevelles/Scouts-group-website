from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, TextAreaField, IntegerField, FloatField, FileField, DateField, RadioField, TimeField, SelectMultipleField, widgets
from wtforms.validators import InputRequired, EqualTo, Length, NumberRange, Optional

class LoginForm(FlaskForm):
    user_id= StringField("User id / Email:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class RegistrationForm(FlaskForm):
    user_id= StringField("User id:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm password:", validators=[InputRequired(), EqualTo("password")])
    email = StringField("Email:", validators=[InputRequired()])
    email2 = StringField("Confirm email:", validators=[InputRequired(), EqualTo("email")])
    submit = SubmitField("Submit")

class SortForm(FlaskForm):
    search = StringField("Search: ")
    category = SelectField("Type:", choices=[], validators=[InputRequired()])
    colour = SelectField("Colour:", choices=[], validators=[InputRequired()])
    sort = SelectField("Sort by:", choices=["Most popular","Lowest price", "Highest price"], default="Most popular", validators=[InputRequired()])
    submit = SubmitField("Sort")

class ContactForm(FlaskForm):
    name = StringField("Full name:", validators=[InputRequired(), Length(min=6, max=20)])
    email = StringField("Email:", validators=[InputRequired()])
    phone = StringField("Phone:")
    subject = SelectField("Subject:", choices=["", "Joining us", "Our activities", "Shop", "Other"])
    message = TextAreaField("", validators=[InputRequired(), Length(min=80, max=500)])
    preference = BooleanField("I would prefer to be contacted by phone.")
    submit = SubmitField("Submit")

class DiscountForm(FlaskForm):
    discount = StringField("Discount code:", validators=[InputRequired()])
    submit = SubmitField("Add")

class AddProductForm(FlaskForm):
    name = StringField("Name of product:", validators=[InputRequired()])
    category = SelectField("Category:", choices=[])
    other_category = StringField("New category:")
    price = FloatField("Price:", validators=[InputRequired(), NumberRange(0.99, 500)])
    colour = SelectField("Colour:", choices=[])
    other_colour = StringField("New colour:")
    description = StringField("Description:", validators=[InputRequired()])
    stock = IntegerField("Stock:", validators=[InputRequired(), NumberRange(1, 999)])
    submit = SubmitField("Add product")

class AddImageToProductForm(FlaskForm):
    file = FileField("Image:")
    submit = SubmitField("Upload")

class RemoveProductForm(FlaskForm):
    image_removal = BooleanField("Optional: I want the image file to be deleted from the system's memory **BE AWARE OF OTHER PRODUCTS THAT MIGHT BE USING THAT SAME IMAGE. IT WILL BE DELETED FOR ALL PRODUCTS**")
    confirmation = BooleanField("I CONFIRM that I want to remove this product and all it's data from the shop's database.", validators=[InputRequired()])
    submit = SubmitField("Submit")

class UpdateProductForm(FlaskForm):
    name = StringField("Name of product:")
    category = SelectField("Category:", choices=[])
    other_category = StringField("New category:")
    price = FloatField("Price:", validators=[Optional(), NumberRange(0.99, 500)])
    colour = SelectField("Colour:", choices=[])
    other_colour = StringField("New colour:")
    description = StringField("Description:")
    stock = IntegerField("Stock:", validators=[Optional(), NumberRange(1, 999)])
    submit1 = SubmitField("Submit")

class UpdateImageForm(FlaskForm):
    file = FileField("Image:", validators=[Optional()])
    submit2 = SubmitField("Upload")

class EditDiscountForm(FlaskForm):
    discount_id = StringField("Discount code: ", validators=[InputRequired()])
    percentage_off = IntegerField("Percentage off: ", validators=[Optional(),NumberRange(10, 70)])
    add_submit = SubmitField("Add")
    delete_submit = SubmitField("Remove")
    update_submit = SubmitField("Update")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Enter current password", validators=[InputRequired()])
    new_password = PasswordField("New password:", validators=[InputRequired()])
    new_password2 = PasswordField("Confirm password:", validators=[InputRequired(), EqualTo("new_password", message="Password entered doesn't match with new password")])
    submit = SubmitField("Submit")

class WriteReviewForm(FlaskForm):
    title = StringField("Title of review:")
    product = SelectField("Product:", choices=[])
    other_category = StringField("New category:")
    price = FloatField("Price:", validators=[Optional(), NumberRange(0.99, 500)])
    colour = SelectField("Colour:", choices=[])
    other_colour = StringField("New colour:")
    description = StringField("Description:")
    stock = IntegerField("Stock:", validators=[Optional(), NumberRange(1, 999)])
    submit1 = SubmitField("Submit")

class ActivitiesSortForm(FlaskForm):
    from_date = DateField("FROM:", validators=[InputRequired()])
    to_date = DateField("TO:", validators=[InputRequired()])
    category = SelectField("Category: ", choices=[], validators=[InputRequired()])
    adults = SelectField("Places available:", validators=[InputRequired()], choices=["1","2","3","4","5","6","7","8"], default="2")
    submit = SubmitField("Search")

class AccessScoutGroupForm(FlaskForm):
    code = StringField("Access code: ", validators=[InputRequired()])
    submit = SubmitField("Submit")

class BookActivityForm(FlaskForm):
    adults = SelectField("Adults:", validators=[InputRequired()], choices=[], default="2")
    confirmation = BooleanField("I agree with the Terms and Conditions. No booking fee is returned in case of cancellation.", validators=[InputRequired()])
    submit = SubmitField("Book activity")

class WriteProductReviewForm(FlaskForm):
    bought_product = SelectField("Product to review: ", validators=[InputRequired()], choices=[])
    rating = RadioField("Rating: ", validators=[InputRequired()], choices = ["1", "2", "3", "4", "5"])
    title = StringField("Review title: ", validators=[InputRequired()])
    review = TextAreaField("Review: ", validators=[InputRequired(), Length(min=10, max=300)])
    submit = SubmitField("Submit")

class AddActivityForm(FlaskForm):
    name = StringField("Name: ", validators=[InputRequired(), Length(min=10, max=40)])
    date = DateField("Date: ", validators=[InputRequired()])
    category = SelectField("Category: ", choices=[])
    other_category = StringField("New category: ")
    difficulty = SelectField("Difficulty: ", choices=["", "Beginners", "Medium", "Advanced"])
    capacity = IntegerField("Capacity: ", validators=[InputRequired(), NumberRange(8,99)])
    price = FloatField("Price: ", validators=[InputRequired()])
    submit = SubmitField("Submit")

class CancelActivityForm(FlaskForm):
    confirmation = BooleanField("I confirm that I want to cancel my assistance to this activity.", validators=[InputRequired()])
    submit = SubmitField("Submit")

class ActivitiesAdminSortForm(FlaskForm):
    from_date = DateField("From:", validators=[InputRequired()])
    to_date = DateField("To:", validators=[InputRequired()])
    category = SelectField("Category: ", choices=[], validators=[InputRequired()])
    booking = BooleanField("Filter only activities with NO bookings yet.")
    submit = SubmitField("Search")

class ProductSalesSortForm(FlaskForm):
    product_select = SelectField("Product: ", choices=[], validators=[InputRequired()])
    submit = SubmitField("Submit")

class AddEventForm(FlaskForm):
    date = DateField("Date: ", validators=[InputRequired()])
    time = TimeField("Time: ", validators=[InputRequired()])
    name = StringField("Event name: ", validators=[InputRequired()])
    # SelectMultipleField + widget understanding: https://www.youtube.com/watch?v=d0jR-2UB9Y0
    group = SelectMultipleField("Scout group: ", validators=[InputRequired()], choices=[("Beaver", "Beaver"), ("Cub", "Cub"), ("Scout", "Scout"), ("Venture", "Venture")], option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    submit = SubmitField("Submit")