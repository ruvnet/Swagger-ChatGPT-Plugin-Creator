# ChatGPT Plugin Creator - From Swagger
#        /\__/\   - main.py
#       ( o.o  )  - v0.0.1
#         >^<     - by @rUv

import os
from flask import Flask, request, render_template, send_from_directory, flash
import yaml
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Process the form data
        swagger_file = request.files['swaggerFile']
        swagger_yaml = yaml.safe_load(swagger_file.read())

        # Get additional form data
        name = request.form.get('name')
        description = request.form.get('description')
        url = request.form.get('url')
        user_authenticated = request.form.get('user_authenticated') == 'true'
        logo_url = request.form.get('logo_url')
        contact_email = request.form.get('contact_email')
        legal_info_url = request.form.get('legal_info_url')

        # Convert the Swagger file to ChatGPT manifest and API specification
        manifest, openapi_spec = convert_swagger_to_chatgpt_manifest(swagger_yaml, name, description, url, user_authenticated, logo_url, contact_email, legal_info_url)

        return jsonify({'manifest': manifest, 'openapi_spec': openapi_spec})

    return render_template('index.html')

def index():
    if request.method == 'POST':
        swagger_file = request.files['swaggerFile']
        name = request.form['name']
        description = request.form['description']
        url = request.form['url']
        user_authenticated = request.form['user_authenticated'] == 'true'
        logo_url = request.form['logo_url']
        contact_email = request.form['contact_email']
        legal_info_url = request.form['legal_info_url']

        if swagger_file:
            swagger_yaml = yaml.safe_load(swagger_file.read())
            manifest, openapi_spec = convert_swagger_to_chatgpt_manifest(swagger_yaml, name, description, url, user_authenticated, logo_url, contact_email, legal_info_url)
            return render_template('index.html', manifest=manifest, openapi_spec=openapi_spec)
        else:
            flash('Please upload a valid Swagger (OpenAPI) file.', 'danger')
            return render_template('index.html')

    return render_template('index.html')

def convert_swagger_to_chatgpt_manifest(swagger_yaml, name, description, url, user_authenticated, logo_url, contact_email, legal_info_url):
    # Extract relevant information from the Swagger YAML
    info = swagger_yaml.get('info', {})
    title = info.get('title', 'My API Plugin')
    description = info.get('description', 'Plugin for interacting with my API.')

    # Create the ChatGPT manifest
    manifest = {
    'schema_version': 'v1',
    'name_for_human': name or title,
    'description_for_human': description or 'Plugin for interacting with my API.',
    'description_for_model': description or 'Plugin for interacting with my API.',
    'auth': {
        'type': 'none'
    },
    'api': {
        'type': 'openapi',
        'url': url,
        'is_user_authenticated': user_authenticated
    },
    'logo_url': logo_url,
    'contact_email': contact_email,
    'legal_info_url': legal_info_url
}

    # Convert the manifest dictionary to a YAML string
    manifest_yaml = yaml.dump(manifest, default_flow_style=False)

    # Prepare the OpenAPI specification for ChatGPT
    # This example assumes that the original Swagger YAML is suitable for use as the ChatGPT OpenAPI specification.
    # You may need to modify or filter the original YAML to suit your needs.
    openapi_spec_yaml = yaml.dump(swagger_yaml, default_flow_style=False)

    return manifest_yaml, openapi_spec_yaml

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory('.', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
