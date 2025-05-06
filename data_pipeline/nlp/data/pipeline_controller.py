#!/usr/bin/env python3
"""
NLP Pipeline Controller
Integrates with existing:
- data/textcleaner.py
- data/text_normalizer.py
"""

import os
import sys
from pathlib import Path
from importlib import import_module
import logging
from datetime import datetime

# Configure project paths
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR / "data"))

class PipelineController:
    def __init__(self):
        self._setup_logging()
        self._verify_structure()
        
        # Dynamic imports of existing modules
        try:
            self.text_cleaner = import_module("textcleaner").TextCleaner()
            self.text_normalizer = import_module("text_normalizer").TextNormalizer()
        except ImportError as e:
            logging.error(f"Failed to import modules: {e}")
            raise

    def _setup_logging(self):
        """Configure logging system"""
        log_dir = BASE_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Pipeline initialized")

    def _verify_structure(self):
        """Verify project directory structure"""
        required_dirs = [
            BASE_DIR / "Case_Category_Classification/original_case_catagories_data",
            BASE_DIR / "data/Cleaned",
            BASE_DIR / "data/normalized",
            BASE_DIR / "benchmarks"
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                logging.warning(f"Created missing directory: {directory}")

    def run_pipeline(self, input_file: str = None):
        """Execute complete processing pipeline"""
        try:
            # Get input files
            input_files = self._get_input_files(input_file)
            
            for file_path in input_files:
                logging.info(f"Processing file: {file_path.name}")
                
                # Clean data
                cleaned_data = self.text_cleaner.process(file_path)
                clean_path = self._save_output(
                    cleaned_data, 
                    file_path, 
                    "Cleaned", 
                    prefix="cleaned_"
                )
                
                # Normalize data
                normalized_data = self.text_normalizer.process(clean_path)
                self._save_output(
                    normalized_data,
                    file_path,
                    "normalized",
                    prefix="normalized_"
                )
                
            logging.info("Pipeline completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Pipeline failed: {e}")
            return False

    def _get_input_files(self, input_file: str = None):
        """Resolve input file(s) to process"""
        input_dir = BASE_DIR / "Case_Category_Classification/original_case_catagories_data"
        
        if input_file:
            file_path = Path(input_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            return [file_path]
        
        # Get all supported files from input directory
        supported_formats = ('.csv', '.json', '.txt')
        input_files = [
            f for f in input_dir.iterdir() 
            if f.suffix.lower() in supported_formats
        ]
        
        if not input_files:
            raise FileNotFoundError(f"No supported files found in {input_dir}")
            
        return input_files

    def _save_output(self, data, original_path, output_dir, prefix=""):
        """Save processed data with consistent naming"""
        output_path = (
            BASE_DIR / "data" / output_dir / 
            f"{prefix}{original_path.name}"
        )
        
        if isinstance(data, pd.DataFrame):
            if original_path.suffix == '.csv':
                data.to_csv(output_path, index=False)
            elif original_path.suffix == '.json':
                data.to_json(output_path, orient='records')
            else:  # .txt
                output_path.write_text('\n'.join(data.iloc[:, 0].astype(str)))
        else:
            output_path.write_text(str(data))
            
        logging.info(f"Saved output to: {output_path}")
        return output_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NLP Pipeline Controller",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--input",
        help="Specific file to process (optional)",
        default=None
    )
    
    args = parser.parse_args()
    
    pipeline = PipelineController()
    success = pipeline.run_pipeline(args.input)
    
    if not success:
        print("Pipeline failed - check logs for details")
        sys.exit(1)
        
    print("Pipeline completed successfully")