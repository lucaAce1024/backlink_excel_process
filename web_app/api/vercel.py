from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import pandas as pd
import os
import tempfile
from werkzeug.utils import secure_filename
import re
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Set max content length from environment variable or default to 50MB
max_content_length = int(os.environ.get('MAX_CONTENT_LENGTH', 52428800))
app.config['MAX_CONTENT_LENGTH'] = max_content_length

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_file_type(filename):
    """Detect file type based on filename"""
    if 'backlinks_refdomains' in filename.lower():
        return 'refdomains'
    elif 'backlinks' in filename.lower():
        return 'backlinks'
    else:
        return None

def extract_domain(url):
    """Extract domain from URL"""
    if pd.isna(url) or not isinstance(url, str):
        return None
    url = url.strip()
    if not url:
        return None
    
    # Handle URLs without protocol
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # Remove 'www.' prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    
    return domain

def extract_domain_from_filename(filename):
    """Extract domain name from filename"""
    # Remove file extension and backlinks suffix
    name = os.path.splitext(filename)[0]
    if '-backlinks' in name:
        domain = name.replace('-backlinks', '')
    elif '-backlinks_refdomains' in name:
        domain = name.replace('-backlinks_refdomains', '')
    else:
        domain = 'unknown'
    return domain

def validate_domain_consistency(backlinks_filename, refdomains_filename):
    """Validate that both files belong to the same domain"""
    domain1 = extract_domain_from_filename(backlinks_filename)
    domain2 = extract_domain_from_filename(refdomains_filename)
    
    if domain1 != domain2:
        raise ValueError(f"域名不匹配：'{domain1}' 和 '{domain2}'。请确保两个文件属于同一个域名。")
    
    return domain1

def merge_backlink_files(backlinks_file, refdomains_file):
    """Merge backlinks and refdomains files"""
    try:
        # Validate domain consistency first
        domain = validate_domain_consistency(backlinks_file.filename, refdomains_file.filename)
        
        # Read Excel files
        df_backlinks = pd.read_excel(backlinks_file)
        df_refdomains = pd.read_excel(refdomains_file)
        
        # Check required columns
        required_backlinks_cols = ['Source url', 'Source title']
        required_refdomains_cols = ['Domain', 'Domain ascore']
        
        for col in required_backlinks_cols:
            if col not in df_backlinks.columns:
                raise ValueError(f"Missing required column in backlinks file: {col}")
        
        for col in required_refdomains_cols:
            if col not in df_refdomains.columns:
                raise ValueError(f"Missing required column in refdomains file: {col}")
        
        # Extract domain from Source url in backlinks file
        df_backlinks['extracted_domain'] = df_backlinks['Source url'].apply(extract_domain)
        
        # Merge the dataframes on domain
        merged_df = pd.merge(
            df_refdomains[['Domain ascore', 'Domain']],
            df_backlinks[['extracted_domain', 'Source title', 'Source url']],
            left_on='Domain',
            right_on='extracted_domain',
            how='inner'
        )
        
        # Remove the extracted_domain column
        merged_df = merged_df.drop('extracted_domain', axis=1)
        
        # Sort by Domain ascore (descending) and Domain (ascending)
        merged_df = merged_df.sort_values(
            by=['Domain ascore', 'Domain'],
            ascending=[False, True]
        )
        
        return merged_df, domain
        
    except Exception as e:
        raise Exception(f"Error merging files: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    # Handle multiple files upload
    if 'files' not in request.files:
        flash('Please upload files')
        return redirect(request.url)
    
    files = request.files.getlist('files')
    
    if len(files) != 2:
        flash('Please upload exactly 2 files')
        return redirect(request.url)
    
    # Detect file types automatically
    backlinks_file = None
    refdomains_file = None
    
    for file in files:
        if file.filename == '':
            flash('One of the files has no name')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash(f'File {file.filename} is not a valid Excel file')
            return redirect(request.url)
        
        file_type = detect_file_type(file.filename)
        if file_type == 'backlinks':
            backlinks_file = file
        elif file_type == 'refdomains':
            refdomains_file = file
    
    if not backlinks_file:
        flash('Could not find backlinks file (should contain "backlinks" in filename)')
        return redirect(request.url)
    
    if not refdomains_file:
        flash('Could not find refdomains file (should contain "backlinks_refdomains" in filename)')
        return redirect(request.url)
    
    try:
        # Pre-validate domain consistency
        try:
            validate_domain_consistency(backlinks_file.filename, refdomains_file.filename)
        except ValueError as e:
            flash(str(e))
            return redirect(request.url)
        
        # Save uploaded files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as backlinks_temp:
            backlinks_file.save(backlinks_temp.name)
            backlinks_path = backlinks_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as refdomains_temp:
            refdomains_file.save(refdomains_temp.name)
            refdomains_path = refdomains_temp.name
        
        # Merge files
        merged_df, domain = merge_backlink_files(backlinks_path, refdomains_path)
        
        # Create output filename with domain and date
        current_date = datetime.now().strftime('%Y%m%d')
        output_filename = f"{domain}-merged-{current_date}.xlsx"
        
        # Create temporary output file
        output_path = tempfile.mktemp(suffix='.xlsx')
        merged_df.to_excel(output_path, index=False)
        
        # Clean up temporary files
        os.unlink(backlinks_path)
        os.unlink(refdomains_path)
        
        # Send the merged file
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error processing files: {str(e)}')
        return redirect(request.url)
    finally:
        # Clean up output file if it exists
        if 'output_path' in locals():
            try:
                os.unlink(output_path)
            except:
                pass

@app.route('/api/merge', methods=['POST'])
def api_merge():
    """API endpoint for programmatic access"""
    # Handle multiple files upload
    if 'files' not in request.files:
        return {'error': 'Please upload files'}, 400
    
    files = request.files.getlist('files')
    
    if len(files) != 2:
        return {'error': 'Please upload exactly 2 files'}, 400
    
    # Detect file types automatically
    backlinks_file = None
    refdomains_file = None
    
    for file in files:
        if file.filename == '':
            return {'error': 'One of the files has no name'}, 400
        
        if not allowed_file(file.filename):
            return {'error': f'File {file.filename} is not a valid Excel file'}, 400
        
        file_type = detect_file_type(file.filename)
        if file_type == 'backlinks':
            backlinks_file = file
        elif file_type == 'refdomains':
            refdomains_file = file
    
    if not backlinks_file:
        return {'error': 'Could not find backlinks file (should contain "backlinks" in filename)'}, 400
    
    if not refdomains_file:
        return {'error': 'Could not find refdomains file (should contain "backlinks_refdomains" in filename)'}, 400
    
    try:
        # Save uploaded files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as backlinks_temp:
            backlinks_file.save(backlinks_temp.name)
            backlinks_path = backlinks_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as refdomains_temp:
            refdomains_file.save(refdomains_temp.name)
            refdomains_path = refdomains_temp.name
        
        # Merge files
        merged_df, domain = merge_backlink_files(backlinks_path, refdomains_path)
        
        # Clean up temporary files
        os.unlink(backlinks_path)
        os.unlink(refdomains_path)
        
        # Return statistics
        return {
            'success': True,
            'records_count': len(merged_df),
            'domain': domain,
            'columns': merged_df.columns.tolist(),
            'sample_data': merged_df.head(5).to_dict('records')
        }
        
    except Exception as e:
        return {'error': str(e)}, 500

# Vercel serverless function handler
def handler(event, context):
    return app