# ChatGPT Plugin Creator - From Swagger
#        /\__/\   - main.py
#       ( o.o  )  - v0.0.1
#         >^<     - by @rUv

import os
import uuid
import time
from flask import Flask, request, render_template, send_from_directory, flash, jsonify
import yaml
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your_secret_key'
plugins_folder = 'plugins'
base_url = "https://chatgpt-swagger-plug-in-creator.ruvnet.repl.co"  # Replace with your actual base URL

# Ensure the plugins folder exists
if not os.path.exists(plugins_folder):
    os.makedirs(plugins_folder)
  
@app.route('/api/v1/create-plugin', methods=['POST'])
def create_plugin():
    # Process the JSON data
    data = request.get_json()
  
    # Get the form data
    swagger_yaml = yaml.safe_load(data['swaggerFile'])
    name = data.get('name')
    description = data.get('description')
    url = data.get('url')
    user_authenticated = data.get('user_authenticated') == 'true'
    logo_url = data.get('logo_url')
    contact_email = data.get('contact_email')
    legal_info_url = data.get('legal_info_url')

        # Generate a unique file name with a timestamp
    spec_file_name = f"spec_{int(time.time())}.yaml"

    # Convert the Swagger file to ChatGPT manifest and API specification
    manifest, openapi_spec = convert_swagger_to_chatgpt_manifest(swagger_yaml, name, description, base_url, spec_file_name, user_authenticated, logo_url, contact_email, legal_info_url)

    # Generate unique file names for the manifest and specification files
    manifest_filename = os.path.join(plugins_folder, f'manifest-{uuid.uuid4()}.yaml')
    openapi_spec_filename = os.path.join(plugins_folder, f'spec-{uuid.uuid4()}.yaml')

    # Save the manifest and specification files
    with open(manifest_filename, 'w') as manifest_file:
        manifest_file.write(manifest)
    with open(openapi_spec_filename, 'w') as spec_file:
        spec_file.write(openapi_spec)
    
    return jsonify({
        'manifest_file': f"/plugins/{os.path.basename(manifest_filename)}",
        'openapi_spec_file': f"/plugins/{os.path.basename(openapi_spec_filename)}",
        'manifest': manifest,
        'openapi_spec': openapi_spec
    })

from pathlib import Path
import uuid

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

        # Save the manifest and specification files to the /plugins folder
        Path("plugins").mkdir(parents=True, exist_ok=True)

        manifest_filename = f"manifest-{uuid.uuid4()}.yaml"
        with open(f"plugins/{manifest_filename}", "w") as manifest_file:
            manifest_file.write(manifest)

        openapi_spec_filename = f"openapi_spec-{uuid.uuid4()}.yaml"
        with open(f"plugins/{openapi_spec_filename}", "w") as openapi_spec_file:
            openapi_spec_file.write(openapi_spec)

        return jsonify({
            'manifest_file': f"/download/{manifest_filename}",
            'openapi_spec_file': f"/download/{openapi_spec_filename}",
            'manifest': manifest,
            'openapi_spec': openapi_spec
        })

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

def convert_swagger_to_chatgpt_manifest(swagger_yaml, name, description, base_url, spec_file_name, user_authenticated, logo_url, contact_email, legal_info_url):
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
            'url': f"{base_url}/plugins/{spec_file_name}",
            'is_user_authenticated': user_authenticated
        },
        'logo_url': logo_url,
        'contact_email': contact_email,
        'legal_info_url': legal_info_url
    }

    # Update the endpoints with authentication and POST type
    paths = swagger_yaml.get('paths', {})
    for path_key, path_item in paths.items():
        for method_key, method_item in path_item.items():
            if method_key.lower() == 'post':
                method_item['x-auth-type'] = 'none' if not user_authenticated else 'apiKey'
                method_item['x-auth-location'] = 'query'

    # Convert the manifest dictionary to a YAML string
    manifest_yaml = yaml.dump(manifest, default_flow_style=False)

    # Prepare the OpenAPI specification for ChatGPT
    # This example assumes that the original Swagger YAML is suitable for use as the ChatGPT OpenAPI specification.
    # You may need to modify or filter the original YAML to suit your needs.
    openapi_spec_yaml = yaml.dump(swagger_yaml, default_flow_style=False)

    return manifest_yaml, openapi_spec_yaml

@app.route('/.well-known/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory('plugins', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
