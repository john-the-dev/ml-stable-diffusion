from flask import Flask, request, render_template, abort,send_file
import os
import logging
from datetime import datetime
from text2image import Text2Image
import re
import config
import json
import utils

app = Flask(__name__)
time_str = datetime.now().strftime('%Y-%m-%d-%H%M%S')
log_file = f"logs/run_{time_str}.log"
logging.basicConfig(filename=log_file, level=logging.DEBUG)
active_users,blocked_users = {},utils.load_blocked_users()

@app.route('/', methods=['GET', 'POST'])

def index():
    def auth(token):
        authenticated = None
        # add to active users if not added before
        if token not in active_users:
            for user in config.allowed_users:
                if config.allowed_users[user]["auth_token"] == token:
                    active_users[token] = user
                    app.logger.info(f"add user {user} to active user list")
        if token not in active_users:
            app.logger.info(f"invalid token ...{token[-4:]} access is blocked")
            return None

        authenticated = active_users[token]
        if authenticated in blocked_users:
            app.logger.info(f"user {authenticated} access is blocked")
            return None
        app.logger.info(f"user {authenticated} is authenticated")
        return authenticated
    
    models = ['CompVis/stable-diffusion-v1-4', 'runwayml/stable-diffusion-v1-5', 'stabilityai/stable-diffusion-2-base']
    default_model = 'runwayml/stable-diffusion-v1-5'
    token = request.args.get('token')
    user = auth(token)
    if not user:
        abort(401)
    if request.method == 'POST':
        model = request.form['models']
        if model not in models:
            app.logger.info(f"hacking attempt detected. revoking token for user {user}: token ...{token[-4:]}, model {model}, prompt {prompt}")
            blocked_users[user] = {
                "time": datetime.now()
            }
            utils.save_blocked_users(blocked_users)
            abort(401)

        prompt = request.form['prompt']
        # todo: check if there is attack attempt in prompt. if detected, block user.

        app.logger.info(f"generating image, model {model}, prompt {prompt}")

        # render image, may take some time
        # todo: provide status to client so user knows how long they need to wait
        image = Text2Image(model).imagine(prompt)

        time_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        sanitized_prompt = re.sub(r'[^\w\-_\. ]', '', prompt)
        image_file_path = f"generated/{sanitized_prompt}_{time_str}.png"
        image.save(f"serve/{image_file_path}")
        app.logger.info(f"generated, model {model}, prompt {prompt}, image {image_file_path}")

        # Render the template with the image path
        # todo: sanitize model and prompt to prevent XSS
        return render_template("index.html", user=user, img_desp=f"Generated an image with model \"{model}\", prompt \"{prompt}\"", img_path=image_file_path, models=models, default_model=default_model)
    else:
        return render_template("index.html", user=user, models=models, default_model=default_model)

@app.route('/generated/<filename>')
def get_generated(filename):
    return send_file(f"generated/{filename}", mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)