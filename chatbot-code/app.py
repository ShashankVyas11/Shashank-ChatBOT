from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from models import db, User, Chat
from forms import RegistrationForm, LoginForm
from utils.local_llm import ask_llama, analyze_image, generate_image

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# 🔐 Load User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 🏠 Homepage - Chatbot Interface
@app.route("/", methods=["GET", "POST"])
def home():
    response_text = "👋 Welcome to Shashank_ChatBOT! Hey, this is Shashank. How can I help you today?"
    image_url = ""

    if request.method == "POST":
        user_prompt = request.form.get("prompt", "").strip()
        uploaded_file = request.files.get("image")

        if uploaded_file and uploaded_file.filename:
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            uploaded_file.save(filepath)

            caption = analyze_image(filepath)
            response_text = f"📸 Image Description: {caption}"
            image_url = generate_image(caption)
            response_text += "<br>🖼️ Generated image based on your uploaded photo."

            if current_user.is_authenticated:
                chat = Chat(prompt="Image Upload", response=caption, user_id=current_user.id)
                db.session.add(chat)
                db.session.commit()

        elif user_prompt:
            if user_prompt.lower().startswith("image:"):
                image_prompt = user_prompt[6:].strip()
                image_url = generate_image(image_prompt)
                response_text = f"🖼️ Generated Image for: {image_prompt}"
            else:
                response_text = ask_llama(user_prompt)

            if current_user.is_authenticated:
                chat = Chat(prompt=user_prompt, response=response_text, user_id=current_user.id)
                db.session.add(chat)
                db.session.commit()

    return render_template("index.html", response=response_text, image=image_url)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    form = RegistrationForm()
    if request.method == "POST":
        print("🔄 POST request received")
        print("✅ Form validation:", form.validate_on_submit())
        print("❌ Form errors:", form.errors)

    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("✅ Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("✅ Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("❌ Invalid email or password", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("🔒 You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        flash("⛔ Access Denied.", "danger")
        return redirect(url_for("home"))
    users = User.query.all()
    chats = Chat.query.order_by(Chat.timestamp.desc()).all()
    return render_template("admin.html", users=users, chats=chats)


@app.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("⛔ Unauthorized action.", "danger")
        return redirect(url_for("home"))

    user = User.query.get_or_404(user_id)
    Chat.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash("🗑️ User deleted successfully.", "success")
    return redirect(url_for("admin"))


# 👑 Create Default Admin
def create_admin():
    admin_email = "admin@bot.com"
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin_user = User(
            username="admin",
            email=admin_email,
            password_hash=generate_password_hash("admin123"),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Default admin created (admin@bot.com / admin123)")


# ✅ App Entry
if __name__ == "__main__":
    with app.app_context():
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        db.create_all()
        create_admin()
    app.run(debug=True)
