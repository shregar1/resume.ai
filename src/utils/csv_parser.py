"""
Utility to convert CSV resume dataset to individual text files.
This processes the dataset.csv format and creates CV files for testing.
"""

import pandas as pd
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_resume_csv(csv_path: str, output_dir: str = "data/cvs/processed", max_cvs: int = None):
    """Parse the resume CSV and create individual CV files.
    
    Args:
        csv_path: Path to the CSV file
        output_dir: Directory to save individual CV files
        max_cvs: Maximum number of CVs to process (None for all)
    """
    try:
        # Read CSV
        logger.info(f"Reading CSV from {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Get column names
        if len(df.columns) >= 2:
            category_col = df.columns[0]
            resume_col = df.columns[1]
        else:
            logger.error("CSV must have at least 2 columns")
            return
        
        logger.info(f"Found {len(df)} resumes in dataset")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process CVs
        processed = 0
        for idx, row in df.iterrows():
            if max_cvs and processed >= max_cvs:
                break
            
            category = row[category_col]
            resume_text = row[resume_col]
            
            # Skip empty or invalid entries
            if pd.isna(resume_text) or not isinstance(resume_text, str):
                continue
            
            # Clean the text
            resume_text = str(resume_text).strip()
            if len(resume_text) < 100:  # Skip very short entries
                continue
            
            # Create filename
            filename = f"cv_{processed + 1}_{category.replace(' ', '_').lower()}.txt"
            filepath = os.path.join(output_dir, filename)
            
            # Write CV to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Category: {category}\n")
                f.write("="*80 + "\n\n")
                f.write(resume_text)
            
            processed += 1
            
            if processed % 10 == 0:
                logger.info(f"Processed {processed} CVs...")
        
        logger.info(f"✓ Successfully created {processed} CV files in {output_dir}")
        return processed
    
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise


def get_sample_cvs(csv_path: str, num_samples: int = 10, category: str = "Data Science"):
    """Get sample CVs from the dataset.
    
    Args:
        csv_path: Path to CSV file
        num_samples: Number of samples to get
        category: Category to filter by
        
    Returns:
        List of CV texts
    """
    try:
        df = pd.read_csv(csv_path)
        
        if len(df.columns) >= 2:
            category_col = df.columns[0]
            resume_col = df.columns[1]
        else:
            return []
        
        # Filter by category if specified
        if category:
            df_filtered = df[df[category_col].str.contains(category, case=False, na=False)]
        else:
            df_filtered = df
        
        # Get samples
        samples = df_filtered.head(num_samples)
        
        cvs = []
        for _, row in samples.iterrows():
            resume_text = row[resume_col]
            if pd.notna(resume_text) and isinstance(resume_text, str):
                cvs.append(str(resume_text).strip())
        
        return cvs
    
    except Exception as e:
        logger.error(f"Error getting samples: {e}")
        return []


def get_dataset_stats(csv_path: str):
    """Get statistics about the dataset.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Dictionary with statistics
    """
    try:
        df = pd.read_csv(csv_path)
        
        if len(df.columns) >= 2:
            category_col = df.columns[0]
            resume_col = df.columns[1]
        else:
            return {}
        
        # Calculate stats
        stats = {
            "total_resumes": len(df),
            "valid_resumes": df[resume_col].notna().sum(),
            "categories": df[category_col].value_counts().to_dict(),
            "avg_resume_length": df[resume_col].str.len().mean()
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {}


if __name__ == "__main__":
    # Process the dataset
    csv_path = "data/cvs/dataset.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Dataset not found at {csv_path}")
        print("Please ensure dataset.csv is in the data/cvs/ directory")
    else:
        print("📊 Dataset Statistics:")
        print("="*80)
        stats = get_dataset_stats(csv_path)
        print(f"Total Resumes: {stats.get('total_resumes', 0)}")
        print(f"Valid Resumes: {stats.get('valid_resumes', 0)}")
        print(f"\nCategories:")
        for category, count in stats.get('categories', {}).items():
            print(f"  - {category}: {count}")
        print(f"\nAverage Resume Length: {stats.get('avg_resume_length', 0):.0f} characters")
        print("="*80)
        print()
        
        # Ask user how many to process
        print("Convert CVs to individual files?")
        choice = input("Enter number of CVs to process (or 'all' for all, 'skip' to skip): ").strip()
        
        if choice.lower() != 'skip':
            max_cvs = None if choice.lower() == 'all' else int(choice) if choice.isdigit() else 50
            
            print(f"\n🔄 Processing {max_cvs or 'all'} CVs...")
            count = parse_resume_csv(csv_path, max_cvs=max_cvs)
            print(f"\n✅ Created {count} CV files in data/cvs/processed/")

