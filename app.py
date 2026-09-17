from flask import Flask, request, render_template_string, redirect
import requests

app = Flask(__name__)

PAYSTACK_SECRET = "sk_test_a60aae7d70da87c604e3b96fb783ee08b30acaf6"
DATAPLAN_API_KEY = "PUT_YOUR_DATAPLAN_KEY_HERE_LATER"
DATAPLAN_URL = "https://mydataplangh.com/api/topup"

PRICES = {
    "1": {"gb": "1GB MTN", "price": 6, "bundle_id": "1", "network": "mtn"},
    "2": {"gb": "2GB MTN", "price": 11, "bundle_id": "2", "network": "mtn"},
    "5": {"gb": "5GB MTN", "price": 26, "bundle_id": "5", "network": "mtn"},
}

HTML = """
<h2 style="text-align:center">Oheneba Data - Fast & Cheap</h2>
<form method="POST" action="/buy" style="max-width:400px;margin:auto;padding:20px;border:1px solid #ccc;border-radius:10px">
    <label>Phone Number:</label><br>
    <input type="text" name="phone" required placeholder="024xxxxxxx" style="width:100%;padding:10px"><br><br>
    <label>Select Bundle:</label><br>
    <select name="bundle" style="width:100%;padding:10px">
        <option value="1">1GB - GHS 6</option>
        <option value="2">2GB - GHS 11</option>
        <option value="5">5GB - GHS 26</option>
    </select><br><br>
    <button type="submit" style="width:100%;padding:12px;background:green;color:white;border:none;border-radius:5px">Pay with MoMo</button>
</form>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/buy", methods=["POST"])
def buy():
    phone = request.form.get("phone")
    choice = request.form.get("bundle")
    item = PRICES[choice]
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    data = {
        "email": f"{phone}@ohenebadata.com",
        "amount": item["price"] * 100,
        "metadata": {"phone": phone, "bundle": choice},
        "callback_url": "http://localhost:5000/verify"
    }
    r = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
    res = r.json()
    if res["status"]:
        return redirect(res["data"]["authorization_url"])
    else:
        return f"Paystack Error: {res}"

@app.route("/verify")
def verify():
    ref = request.args.get("reference")
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    r = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
    res = r.json()
    if res["data"]["status"] == "success":
        phone = res["data"]["metadata"]["phone"]
        bundle_choice = res["data"]["metadata"]["bundle"]
        item = PRICES[bundle_choice]
        return f"<h1 style='text-align:center;color:green'>Payment Success! {item['gb']} paid for {phone}. <br> Now you would send data via API.</h1><a href='/'>Sell again</a>"
    else:
        return "Payment failed"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
