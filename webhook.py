import subprocess
from flask import Flask, request
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route("/run", methods=["GET"])
def run_bot():
    if request.args.get("key") != os.getenv("TRIGGER_KEY"):
        return " Yetkisiz istek", 403

    try:
        subprocess.run(["python", "main.py"], check=True)
        return " Bot çalıştırıldı", 200
    except Exception as e:
        return f" Hata: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
