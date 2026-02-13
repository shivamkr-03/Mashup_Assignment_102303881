from flask import Flask, render_template, request
import re
import os
from mashup_logic import build_mashup, send_mashup_email, cleanup_workspace

app = Flask(__name__)


# ------------------------------
# EMAIL VALIDATION FUNCTION
# ------------------------------

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)


# ------------------------------
# HOME ROUTE
# ------------------------------

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    error = ""

    if request.method == "POST":

        singer = request.form.get("singer")
        num_videos = request.form.get("videos")
        duration = request.form.get("duration")
        email = request.form.get("email")

        # Validation
        if not singer or singer.strip() == "":
            error = "Singer name cannot be empty."

        elif not num_videos or int(num_videos) <= 10:
            error = "Number of videos must be greater than 10."

        elif not duration or int(duration) <= 20:
            error = "Duration must be greater than 20 seconds."

        elif not is_valid_email(email):
            error = "Please enter a valid email address."

        else:
            try:
                zip_path = build_mashup(
                    singer,
                    int(num_videos),
                    int(duration)
                )

                send_mashup_email(email, zip_path)

                cleanup_workspace()

                message = "Mashup generated and sent successfully!"

            except Exception as e:
                error = str(e)

    return render_template("index.html", message=message, error=error)


# ------------------------------
# RUN APP
# ------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)