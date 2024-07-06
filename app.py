import os
import re
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'static'

# Load a smaller pre-trained model
tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
model = AutoModelForCausalLM.from_pretrained("distilgpt2")
text_generation = pipeline("text-generation", model=model, tokenizer=tokenizer)

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def detect_colors_and_images(description):
    colors = set(re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', description))
    image_urls = re.findall(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.(?:png|jpg|jpeg|gif))', description)
    return colors, image_urls

def generate_code_from_description(description):
    colors, image_urls = detect_colors_and_images(description)
    
    # Use the model to generate code
    result = text_generation(description, max_length=512, num_return_sequences=1)
    generated_code = result[0]['generated_text']
    
    html_content = generated_code
    
    # Embed detected images in HTML
    for image_url in image_urls:
        html_content += f'<img src="{image_url}" alt="Image">\n'
    
    css_code = "/* Add your CSS here */\n"
    for color in colors:
        css_code += f".color-{color.lstrip('#')} {{ color: {color}; }}\n"

    js_code = "// Add your JavaScript here"
    
    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <title>Generated Page</title>
    <link rel='stylesheet' href='/static/css/style.css'>
    <script src='/static/js/script.js'></script>
</head>
<body>
{html_content}
</body>
</html>"""

    # Save the files
    os.makedirs(os.path.join(app.config['GENERATED_FOLDER'], 'html'), exist_ok=True)
    os.makedirs(os.path.join(app.config['GENERATED_FOLDER'], 'css'), exist_ok=True)
    os.makedirs(os.path.join(app.config['GENERATED_FOLDER'], 'js'), exist_ok=True)

    with open(os.path.join(app.config['GENERATED_FOLDER'], 'html', 'generated.html'), 'w') as html_file:
        html_file.write(html_code)
    with open(os.path.join(app.config['GENERATED_FOLDER'], 'css', 'style.css'), 'w') as css_file:
        css_file.write(css_code)
    with open(os.path.join(app.config['GENERATED_FOLDER'], 'js', 'script.js'), 'w') as js_file:
        js_file.write(js_code)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            if file.filename.lower().endswith(('png', 'jpg', 'jpeg')):
                description = extract_text_from_image(file_path)
            elif file.filename.lower().endswith('pdf'):
                description = extract_text_from_pdf(file_path)
            else:
                return 'Unsupported file type'
            
            generate_code_from_description(description)
            return redirect(url_for('edit_code'))
    
    return render_template('index.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit_code():
    html_path = os.path.join(app.config['GENERATED_FOLDER'], 'html', 'generated.html')
    css_path = os.path.join(app.config['GENERATED_FOLDER'], 'css', 'style.css')
    js_path = os.path.join(app.config['GENERATED_FOLDER'], 'js', 'script.js')
    
    if request.method == 'POST':
        html_code = request.form['html']
        css_code = request.form['css']
        js_code = request.form['js']
        
        with open(html_path, 'w') as html_file:
            html_file.write(html_code)
        with open(css_path, 'w') as css_file:
            css_file.write(css_code)
        with open(js_path, 'w') as js_file:
            js_file.write(js_code)
        
        return redirect(url_for('edit_code'))
    
    with open(html_path, 'r') as html_file:
        html_code = html_file.read()
    with open(css_path, 'r') as css_file:
        css_code = css_file.read()
    with open(js_path, 'r') as js_file:
        js_code = js_file.read()
    
    return render_template('edit.html', html_code=html_code, css_code=css_code, js_code=js_code)

@app.route('/download/<filename>')
def download_file(filename):
    directory, filename = os.path.split(filename)
    return send_from_directory(os.path.join(app.config['GENERATED_FOLDER'], directory), filename)

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['GENERATED_FOLDER'], 'html'), exist_ok=True)
    os.makedirs(os.path.join(app.config['GENERATED_FOLDER'], 'css'), exist_ok=True)
    os.makedirs(os.path.join(app.config['GENERATED_FOLDER'], 'js'), exist_ok=True)
    app.run(debug=True)
