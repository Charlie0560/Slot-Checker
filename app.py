from datetime import datetime
import requests
from flask import Flask, render_template, request

app = Flask(__name__)
OUTPUTS = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/index.html')
def home():
    return render_template('index.html')


@app.route("/about.html")
def about():
    return render_template("about.html")


@app.route("/products.html")
def products():
    return render_template("products.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    if not name:
        return render_template("error.html", message="Please Enter District Name")

    else:
        def get_sessions(data):
            for center in data["centers"]:
                for session in center["sessions"]:
                    yield {"name": center["name"],
                           "type": center["fee_type"],
                           "date": session["date"],
                           "capacity": session["available_capacity"],
                           "age_limit": session["min_age_limit"],
                           "vaccine": session["vaccine"],
                           "pincode": center["pincode"]
                           }

        def get_for_seven_days(start_date):
            resp = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict",
                                params={"district_id": name, "date": start_date.strftime("%d-%m-%Y")}, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"})
            data = resp.json()
            return [session for session in get_sessions(data) if session["capacity"] > 0 and session["age_limit"] == 18]

        def create_output(session_info):
            return [session_info['date'], session_info['name'], session_info['pincode'], session_info['capacity'],
                    session_info['vaccine'] + " " + session_info['type']]

        content = [create_output(session_info) for session_info in get_for_seven_days(datetime.now())]
        if not content:
            return render_template("noavailable.html", message="No slots available for your region")
        else:
            heading = ("DATE", "HOSP NAME", "PINCODE", "CAPACITY", "VACCINE,FEE")
            return render_template("output.html", heading=heading, message=content)
