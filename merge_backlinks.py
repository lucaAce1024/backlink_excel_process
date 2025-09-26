import pandas as pd
import os
import re
from urllib.parse import urlparse

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

def merge_backlink_files(backlinks_file, refdomains_file, output_file):
    """Merge backlinks and refdomains files"""
    try:
        # Read Excel files
        print(f"Reading {backlinks_file}...")
        df_backlinks = pd.read_excel(backlinks_file)
        
        print(f"Reading {refdomains_file}...")
        df_refdomains = pd.read_excel(refdomains_file)
        
        # Extract domain from Source url in backlinks file
        print("Extracting domains from Source urls...")
        df_backlinks['extracted_domain'] = df_backlinks['Source url'].apply(extract_domain)
        
        # Merge the dataframes on domain
        print("Merging data...")
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
        
        # Save to output file
        print(f"Saving merged data to {output_file}...")
        merged_df.to_excel(output_file, index=False)
        
        print(f"Successfully merged {len(merged_df)} records")
        return merged_df
        
    except Exception as e:
        print(f"Error merging files: {e}")
        return None

def process_all_backlinks(input_dir='backlink_resouce', output_dir='merged_backlinks'):
    """Process all backlink files in the input directory"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all backlinks files
    backlinks_files = [f for f in os.listdir(input_dir) if f.endswith('-backlinks.xlsx')]
    
    for backlinks_file in backlinks_files:
        # Extract site domain from filename
        site_domain = backlinks_file.replace('-backlinks.xlsx', '')
        refdomains_file = f"{site_domain}-backlinks_refdomains.xlsx"
        
        # Check if corresponding refdomains file exists
        if refdomains_file in os.listdir(input_dir):
            print(f"\nProcessing {site_domain}...")
            
            backlinks_path = os.path.join(input_dir, backlinks_file)
            refdomains_path = os.path.join(input_dir, refdomains_file)
            output_path = os.path.join(output_dir, f"{site_domain}-merged.xlsx")
            
            result = merge_backlink_files(backlinks_path, refdomains_path, output_path)
            
            if result is not None:
                print(f"Completed: {output_path}")
                print(f"Merged records: {len(result)}")
        else:
            print(f"Warning: Missing refdomains file for {site_domain}")

if __name__ == "__main__":
    print("Starting backlink merge process...")
    process_all_backlinks()
    print("\nMerge process completed!")