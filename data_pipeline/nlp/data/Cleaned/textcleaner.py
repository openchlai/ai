#!/usr/bin/env python3
"""
Text Data Cleaning Pipeline with PII Redaction
Author: [Your Name]
Date: [YYYY-MM-DD]
"""

import re
import pandas as pd
import logging
from pathlib import Path
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from typing import Union, List, Dict
import json
from datetime import datetime

# Configuration
CONFIG = {
    "input_formats": [".csv", ".json", ".txt"],
    "output_dir": "./data/cleaned/",
    "log_dir": "./logs/",
    "pii_types": [
        "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER",
        "LOCATION", "IP_ADDRESS", "US_SSN"
    ],
    "regex_patterns": {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'(\+\d{1,2}\s?)?(\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b'
    },
    "text_standards": {
        "lowercase": True,
        "remove_diacritics": True,
        "whitespace_normalization": True
    }
}

class TextCleaner:
    def __init__(self, config: Dict = CONFIG):
        """
        Initialize the TextCleaner with configuration settings
        Args:
            config: Dictionary containing configuration parameters
        """
        self.config = config
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self._setup_logging()
        
    def _setup_logging(self):
        """
        Initialize logging system and create necessary directories
        Sets up logging configuration and initializes PII logging list
        """
        Path(self.config["log_dir"]).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=f'{self.config["log_dir"]}preprocessing_logs.csv',
            level=logging.INFO,
            format='%(asctime)s,%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.pii_log = []

    def clean_dataset(self, input_path: Union[str, Path]):
        """
        Main cleaning pipeline that processes the input dataset
        Args:
            input_path: Path to the input file
        Returns:
            Processed DataFrame with cleaned text and redacted PII
        """
        input_path = Path(input_path)
        df = self._load_data(input_path)
        
        # Pipeline execution
        df = self._remove_duplicates(df)
        df = self._detect_and_redact_pii(df)
        df = self._clean_text_data(df)
        
        self._save_output(df, input_path)
        self._save_pii_report()
        
        return df

    def _load_data(self, input_path: Path) -> pd.DataFrame:
        """
        Load input data based on file format
        Args:
            input_path: Path to the input file
        Returns:
            DataFrame containing the loaded data
        Raises:
            ValueError: If file format is not supported
        """
        if input_path.suffix == '.csv':
            return pd.read_csv(input_path)
        elif input_path.suffix == '.json':
            return pd.read_json(input_path)
        elif input_path.suffix == '.txt':
            return pd.DataFrame({'text': input_path.read_text().splitlines()})
        else:
            raise ValueError(f"Unsupported file format: {input_path.suffix}")

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate rows from the DataFrame
        Args:
            df: Input DataFrame
        Returns:
            DataFrame with duplicates removed
        """
        initial_count = len(df)
        df.drop_duplicates(inplace=True)
        removed = initial_count - len(df)
        logging.info(f"removed_duplicates,{removed}")
        return df

    def _detect_and_redact_pii(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify and anonymize PII in text columns
        Args:
            df: Input DataFrame
        Returns:
            DataFrame with PII information redacted
        """
        pii_counts = {pii_type: 0 for pii_type in self.config["pii_types"]}
        
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(
                lambda x: self._process_text(x, pii_counts) if pd.notna(x) else x
            )
        
        # Log PII findings
        pii_summary = " | ".join(
            f"{k}: {v}" for k, v in pii_counts.items() if v > 0
        )
        if pii_summary:
            logging.info(f"redacted_pii,{pii_summary}")
            self.pii_log.append({
                "timestamp": datetime.now().isoformat(),
                "column": col,
                "counts": pii_counts
            })
            
        return df

    def _process_text(self, text: str, pii_counts: Dict) -> str:
        """
        Process individual text items for PII detection and redaction
        Args:
            text: Input text to process
            pii_counts: Dictionary to track PII occurrences
        Returns:
            Processed text with PII redacted
        """
        # Rule-based detection
        for entity_type, pattern in self.config["regex_patterns"].items():
            matches = re.findall(pattern, text)
            if matches:
                pii_counts[entity_type.upper()] += len(matches)
                
        # NLP-based detection
        results = self.analyzer.analyze(
            text=text,
            language='en',
            entities=self.config["pii_types"]
        )
        
        # Anonymize all findings
        if results:
            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results
            )
            for result in results:
                pii_counts[result.entity_type] += 1
            return anonymized.text
        
        return text

    def _clean_text_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply standard text cleaning operations to all text columns
        Args:
            df: Input DataFrame
        Returns:
            DataFrame with cleaned text
        """
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(
                lambda x: self._clean_text(x) if pd.notna(x) else x
            )
        return df

    def _clean_text(self, text: str) -> str:
        """
        Clean individual text items using standard text cleaning operations
        Args:
            text: Input text to clean
        Returns:
            Cleaned text string
        """
        # Remove HTML/XML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters (keep alphanumeric + basic punctuation)
        text = re.sub(r'[^\w\s.,!?]', '', text)
        
        # Standardize whitespace
        text = ' '.join(text.split())
        
        # Case normalization
        if self.config["text_standards"]["lowercase"]:
            text = text.lower()
            
        return text

    def _save_output(self, df: pd.DataFrame, input_path: Path):
        """
        Save processed data to output directory
        Args:
            df: Processed DataFrame to save
            input_path: Original input file path
        """
        Path(self.config["output_dir"]).mkdir(parents=True, exist_ok=True)
        output_path = Path(self.config["output_dir"]) / f"cleaned_{input_path.name}"
        
        if input_path.suffix == '.csv':
            df.to_csv(output_path, index=False)
        elif input_path.suffix == '.json':
            df.to_json(output_path, orient='records')
        else:
            output_path.write_text('\n'.join(df.iloc[:, 0].astype(str)))

    def _save_pii_report(self):
        """
        Save detailed PII findings to a JSON report file
        Only saves if PII was detected during processing
        """
        if not self.pii_log:
            return
            
        report_path = Path(self.config["log_dir"]) / \
            f"pii_redaction_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.pii_log, f, indent=2)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Text cleaning pipeline with PII redaction"
    )
    parser.add_argument(
        "input_file",
        help="Path to input file (CSV, JSON, or TXT)"
    )
    args = parser.parse_args()
    
    cleaner = TextCleaner()
    cleaner.clean_dataset(args.input_file)
    
    print(f"Processing complete. Output saved to {CONFIG['output_dir']}")