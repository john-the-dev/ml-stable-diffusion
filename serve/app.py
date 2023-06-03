from flask import Flask, request, render_template
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        # Run your function here
        # ...
        # Save the image to disk
        img_path = 'static/img/result.png'
        # Render the template with the image path
        return render_template("index.html", img_path=img_path)
    else:
        return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)