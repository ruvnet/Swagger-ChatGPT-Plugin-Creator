#  ChatGPT Plugin Creator - From Swagger
#        /\__/\   - main.py 
#       ( o.o  )  - v0.0.1
#         >^<     - by @rUv

  
import os
from flask import Flask, request, render_template, send_from_directory
import yaml

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        swagger_file = request.files['swagger_file']
        swagger_yaml = yaml.safe_load(swagger_file)
        manifest, openapi_spec = convert_swagger_to_chatgpt_manifest(swagger_yaml)
        return render_template('results.html', manifest=manifest, openapi_spec=openapi_spec)
    return render_template('index.html')

def convert_swagger_to_chatgpt_manifest(swagger_yaml):
    # Extract relevant information from the Swagger YAML
    info = swagger_yaml.get('info', {})
    title = info.get('title', 'My API Plugin')
    description = info.get('description', 'Plugin for interacting with my API.')

    # Create the ChatGPT manifest
    manifest = {
        'schema_version': 'v1',
        'name_for_human': title,
        'name_for_model': ''.join(e for e in title if e.isalnum()).lower(),
        'description_for_human': description,
        'description_for_model': description,
        'auth': {
            'type': 'none'
        },
        'api': {
            'type': 'openapi',
            'url': 'https://api.example.com/openapi.yaml',
            'is_user_authenticated': False
        },
        'logo_url': 'https://api.example.com/logo.png',
        'contact_email': 'support@example.com',
        'legal_info_url': 'https://api.example.com/legal'
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