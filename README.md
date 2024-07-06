# EZWEB

This Flask application converts uploaded design files (images or PDFs) into HTML, CSS, and JavaScript code using a pre-trained text generation model.

## Features

- Upload images or PDFs of website designs
- Extract text from images or PDFs
- Detect colors and image URLs in the extracted text
- Generate HTML, CSS, and JavaScript code from the extracted description
- Edit the generated code in the browser
- Download the generated code files

## Requirements

- Python 3.6+
- pip (Python package installer)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/kisalnelaka/ezweb.git
   cd ezweb
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required libraries:**

   ```bash
   pip install Flask Pillow pytesseract PyMuPDF transformers torch
   ```

4. **Download Tesseract OCR:**

   - **Windows:** [Download Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS:** Install via Homebrew: `brew install tesseract`
   - **Linux:** Install via package manager, e.g., `sudo apt-get install tesseract-ocr`

5. **Ensure the `tesseract` command is available in your PATH.**

## Usage

1. **Run the Flask application:**

   ```bash
   python app.py
   ```

2. **Open your web browser and navigate to:**

   ```
   http://127.0.0.1:5000/
   ```

3. **Upload an image or PDF of a website design:**

   - The application will extract text from the uploaded file.
   - It will detect colors and image URLs in the extracted text.
   - It will generate HTML, CSS, and JavaScript code based on the description.

4. **Edit the generated code:**

   - You can edit the generated HTML, CSS, and JavaScript code directly in your browser.
   - Save changes to update the code files.

5. **Download the generated code files:**

   - Download the HTML, CSS, and JavaScript files using the provided download links.

## Directory Structure

```
ezweb/
|-- templates/
|   |-- index.html
|   |-- edit.html
|-- static/
|   |-- html/
|   |-- css/
|   |-- js/
|-- uploads/
|-- app.py
|-- README.md
```

## Code Overview

### app.py

The main Flask application script:

- **Dependencies:**
  - Flask
  - Pillow
  - pytesseract
  - PyMuPDF
  - transformers
  - torch

- **Functions:**
  - `extract_text_from_image(image_path)`: Extracts text from an image file.
  - `extract_text_from_pdf(pdf_path)`: Extracts text from a PDF file.
  - `detect_colors_and_images(description)`: Detects colors and image URLs in the extracted text.
  - `generate_code_from_description(description)`: Generates HTML, CSS, and JavaScript code from the description.

- **Routes:**
  - `/`: Handles file uploads and processes the uploaded files.
  - `/edit`: Allows editing of the generated code.
  - `/download/<filename>`: Allows downloading of the generated code files.

### templates/index.html

HTML template for the file upload page.

### templates/edit.html

HTML template for the code editing page.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

Feel free to customize this README file to suit your project's specific needs.