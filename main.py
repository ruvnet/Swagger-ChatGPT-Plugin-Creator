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
from flask import jsonify
import json
from werkzeug.routing import BaseConverter
from urllib.parse import unquote
import re
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'
plugins_folder = 'plugins'
base_url = "https://chatgpt-dev-1.ruvnet.repl.co"  # Replace with your actual base URL

current_topic = None

# Ensure the plugins folder exists
if not os.path.exists(plugins_folder):
  os.makedirs(plugins_folder)

class RandomPathConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RandomPathConverter, self).__init__(url_map)
        self.regex = '(?i).*random.*'

app.url_map.converters['random_path'] = RandomPathConverter


def load_json_data():
  data_file_path = os.path.join('data', 'introduction.json')
  with open(data_file_path, 'r') as file:
    data = json.load(file, strict=False)
  return data

# Define a function to read the contents of the data/instructions.txt file
def read_instructions_file(filename):
  file_path = os.path.join('data', filename)
  try:
    with open(file_path, 'r') as file:
      contents = file.read()
    return contents
  except FileNotFoundError:
    return "File not found."

@app.before_request
def log_request_info():
    logging.info('Headers: %s', request.headers)
    logging.info('Body: %s', request.get_data())

# Add the requested endpoints
@app.route('/introduction', methods=['GET', 'POST'])
def introduction():
  if request.method == 'POST':
    # code to be executed
    pass
  else:
    # Handle the GET request (default behavior)
    instructions_text = read_instructions_file('introduction.txt')
    return instructions_text  # Return the contents of the file as plain text

@app.route('/purpose', methods=['GET'])
def purpose():
    purpose_text = read_instructions_file('purpose.txt')
    return purpose_text


@app.route('/context', methods=['GET'])
def context():
    context_text = read_instructions_file('context.txt')
    return context_text


@app.route('/examples', methods=['GET'])
def examples():
    examples_text = read_instructions_file('examples.txt')
    return examples_text


@app.route('/errors', methods=['GET'])
def errors():
    errors_text = read_instructions_file('errors.txt')
    return errors_text


@app.route('/commands', methods=['GET'])
def commands():
    commands_text = read_instructions_file('commands.txt')
    return commands_text


@app.route('/action', methods=['GET'])
def action():
    action_text = read_instructions_file('action.txt')
    return action_text


@app.route('/initialize', methods=['GET'])
def initialize():
    initialize_text = read_instructions_file('initialize.txt')
    return initialize_text

@app.route('/random', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/random/<path:path>', methods=['GET', 'POST'])
def random(path):
    if request.method == 'GET':
        # Extract JSON payload from the path
        payload = re.search(r'\{.*\}', unquote(path))
        if payload:
            payload_str = payload.group()
            try:
                input_data = json.loads(payload_str)
                topic = input_data.get('topic', 'No topic provided')
                data = {
                    'message':
                    f'You have provided the following topic: {topic}. Here is the output of a manifest.json and specification.yaml in mark down code block.'
                }
                return jsonify(data)
            except json.JSONDecodeError:
                pass
        random_text = read_instructions_file('random.txt')
        return random_text
    elif request.method == 'POST':
        input_data = request.get_json()
        topic = input_data.get('topic', 'No topic provided')
        random_text = read_instructions_file('random.txt')
        data = {
            'message':
            f'You have provided the following topic: {topic}. Here is the output of a manifest.json and specification.yaml in mark down code block.\n\n{random_text}'
        }
        return jsonify(data)

@app.route('/convert_curl', methods=['POST'])
def convert_curl():
    input_data = request.get_json()
    topic = input_data.get('curl_command', '{topic}')
    random_text = read_instructions_file('random.txt')
    data = {
        'message': f'You have provided the following CURL: {topic}. Here is the output of a manifest.json and specification.yaml in mark down code block.\n\n{random_text}'
    }
    return jsonify(data)


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
  manifest, openapi_spec = convert_swagger_to_chatgpt_manifest(
    swagger_yaml, name, description, base_url, spec_file_name,
    user_authenticated, logo_url, contact_email, legal_info_url)

  # Generate unique file names for the manifest and specification files
  manifest_filename = os.path.join(plugins_folder,
                                   f'manifest-{uuid.uuid4()}.yaml')
  openapi_spec_filename = os.path.join(plugins_folder,
                                       f'spec-{uuid.uuid4()}.yaml')

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
    manifest, openapi_spec = convert_swagger_to_chatgpt_manifest(
      swagger_yaml, name, description, url, user_authenticated, logo_url,
      contact_email, legal_info_url)

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
      manifest, openapi_spec = convert_swagger_to_chatgpt_manifest(
        swagger_yaml, name, description, url, user_authenticated, logo_url,
        contact_email, legal_info_url)
      return render_template('index.html',
                             manifest=manifest,
                             openapi_spec=openapi_spec)
    else:
      flash('Please upload a valid Swagger (OpenAPI) file.', 'danger')
      return render_template('index.html')

  return render_template('index.html')


def convert_swagger_to_chatgpt_manifest(swagger_yaml, name, description,
                                        base_url, spec_file_name,
                                        user_authenticated, logo_url,
                                        contact_email, legal_info_url):
  # Extract relevant information from the Swagger YAML
  info = swagger_yaml.get('info', {})
  title = info.get('title', 'My API Plugin')
  description = info.get('description', 'Plugin for interacting with my API.')

  # Create the ChatGPT manifest
  manifest = {
    'schema_version': 'v1',
    'name_for_human': name or title,
    'description_for_human': description
    or 'Plugin for interacting with my API.',
    'description_for_model': description
    or 'Plugin for interacting with my API.',
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
        method_item[
          'x-auth-type'] = 'none' if not user_authenticated else 'apiKey'
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
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8080)