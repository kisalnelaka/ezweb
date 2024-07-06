import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'static'

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

def generate_code_from_description(description):
    # Simplistic parser to convert text to HTML, CSS, and JS
    lines = description.split('\n')
    html_content = ''
    for line in lines:
        line = line.strip().lower()
        if 'header' in line:
            html_content += f'<header>{line.replace("header", "").strip()}</header>\n'
        elif 'footer' in line:
            html_content += f'<footer>{line.replace("footer", "").strip()}</footer>\n'
        elif 'button' in line:
            html_content += f'<button>{line.replace("button", "").strip()}</button>\n'
        elif 'image' in line:
            html_content += f'<img src="{line.replace("image", "").strip()}" alt="image">\n'
        elif 'link' in line:
            html_content += f'<a href="{line.replace("link", "").strip()}">Link</a>\n'
        else:
            html_content += f'<p>{line}</p>\n'
    
    html_code = f"<!DOCTYPE html><html><head><title>Generated Page</title><link rel='stylesheet' href='/static/css/style.css'><script src='/static/js/script.js'></script></head><body>{html_content}</body></html>"
    css_code = "/* Add your CSS here */"
    js_code = "// Add your JavaScript here"
    
    # Save the files
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
    return send_from_directory(app.config['GENERATED_FOLDER'], filename)

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['GENERATED_FOLDER']):
        os.makedirs(app.config['GENERATED_FOLDER'])
    if not os.path.exists(os.path.join(app.config['GENERATED_FOLDER'], 'html')):
        os.makedirs(os.path.join(app.config['GENERATED_FOLDER'], 'html'))
    if not os.path.exists(os.path.join(app.config['GENERATED_FOLDER'], 'css')):
        os.makedirs(os.path.join(app.config['GENERATED_FOLDER'], 'css'))
    if not os.path.exists(os.path.join(app.config['GENERATED_FOLDER'], 'js')):
        os.makedirs(os.path.join(app.config['GENERATED_FOLDER'], 'js'))
    app.run(debug=True)
