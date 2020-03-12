from flask import Flask, render_template

app = Flask(__name__)

def start_server():
    print("Starting web server...")
    app.run(debug=True, host="0.0.0.0", port = 80)

@app.route("/")
def main():
    return render_template('index.html')
    
if __name__ == "__main__":
    start_server()