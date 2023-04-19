from flask_bootstrap import Bootstrap5
from flask_fontawesome import FontAwesome
from flask import Flask, render_template, jsonify, request

import base64
from datetime import datetime
from utils.ft_otp import (
    get_totp_key,
    update_master_password,
    read_master_password,
    get_random_master_key,
)

ft_otp_key = "ft_otp.key"


def create_app(test_config=None):
    app = Flask(__name__)
    FontAwesome(app)
    Bootstrap5(app)

    @app.route("/")
    def index():
        percentage = calculate_percentage_next_totp()
        key = get_totp_key("keys/" + ft_otp_key)
        master_key = read_master_password()
        return render_template(
            "index.html", key=key, percentage_to_next=percentage, master_key=master_key
        )

    @app.route("/totp", defaults={"master_password": None}, methods=["GET"])
    @app.route("/totp/<master_password>", methods=["GET"])
    def reload_totp_key(master_password):
        percentage = calculate_percentage_next_totp()
        success = False
        try:
            master_password = master_password.replace("master_password=", "")
            print(master_password)
            b64_master_password = base64.b64encode(master_password.encode("utf-8"))
            key = get_totp_key("keys/" + ft_otp_key, b64_master_password)
            success = True
        except Exception:
            key = "???"
            print("Master password: {} is not correct".format(master_password))
        return jsonify(
            {"key": key, "percentage_to_next": percentage, "success": success}
        )

    @app.route("/totp/", methods=["POST"])
    def update_master_key_controller():
        success = False
        error = None
        new_master_password = request.get_json()["new_master_password"]
        try:
            success = update_master_password(new_master_password)
        except Exception as e:
            error = str(e)
        return jsonify(
            {
                "new_master_password": new_master_password,
                "success": success,
                "error": error,
            }
        )

    def calculate_percentage_next_totp():
        now = datetime.now()
        seconds = int(now.strftime("%S"))
        thirty_mod = seconds % 30
        print("Progress bar: {}".format(thirty_mod))
        return round(thirty_mod * 100 / 30, 2)

    @app.route("/new-master-key")
    def new_master_key():
        return jsonify({"new_master_key": get_random_master_key()})

    return app
