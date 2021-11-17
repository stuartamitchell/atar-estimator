import os
import secrets
from flask.helpers import flash, send_from_directory
from flask import Flask, request, redirect 
from flask.templating import render_template
from src.atar_est import produce_atar_estimates
from src.read_data import load_data

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'downloads')
app.secret_key = secrets.token_bytes(16)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        acs_export = request.files['acs_export']
        scaling_groups = request.files['scaling_groups']
        past_params_file = request.files['past_params']
        atar_bounds_file = request.files['atar_bounds']

        students, past_params, scaling_groups, atar_bounds = load_data(acs_export, 
                                                                        past_params_file, 
                                                                        scaling_groups,
                                                                        atar_bounds_file)
        
        predict_atar_df = produce_atar_estimates(students, past_params, scaling_groups, atar_bounds)
        predict_atar_df.to_excel(os.path.join(app.root_path, 'downloads/atar_estimates.xlsx'))

        return render_template('index.html', download_file=True)
    else:
        return render_template('index.html', download_file=False)

@app.route('/downloads/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()