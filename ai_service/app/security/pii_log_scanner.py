#!/usr/bin/env python3
"""
PII Detection and Redaction for OpenCHS Logs

This script implements automated PII detection using Microsoft Presidio
to scan and redact sensitive information from application logs.

Features:
- Scans Celery worker logs and main application logs
- Detects names, phone numbers, emails, locations, dates
- Automatically redacts PII with [REDACTED-TYPE] placeholders
- Generates alerts when PII is found
- Creates audit reports

Usage:
    python pii_log_scanner.py --scan /path/to/logs
    python pii_log_scanner.py --monitor /path/to/logs --alert-email admin@openchs.org
    python pii_log_scanner.py --redact input.log output.log

Requirements:
    pip install presidio-analyzer presidio-anonymizer spacy
    python -m spacy download en_core_web_lg

"""

import re
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field
import argparse

# Check for spaCy (lightweight NER)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# Check for Presidio dependencies (full-featured)
try:
    from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
    from presidio_anonymizer import AnonymizerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

if not SPACY_AVAILABLE and not PRESIDIO_AVAILABLE:
    print("Warning: Neither spaCy nor Presidio installed.")
    print("For best PII detection, install spaCy:")
    print("  pip install spacy")
    print("  python -m spacy download en_core_web_sm")
    print("Or for full features:")
    print("  pip install presidio-analyzer presidio-anonymizer spacy")
    print("  python -m spacy download en_core_web_lg")


@dataclass
class PIIDetection:
    """Record of detected PII in logs"""
    timestamp: str
    log_file: str
    line_number: int
    entity_type: str
    entity_text: str
    confidence: float
    context: str  # Surrounding text for context
    redacted_text: str = ""


@dataclass
class ScanResult:
    """Results from scanning a file or directory"""
    scan_timestamp: str
    files_scanned: int
    total_lines: int
    lines_with_pii: int
    pii_percentage: float
    total_detections: int
    detections_by_type: Dict[str, int]
    high_risk_files: List[str] = field(default_factory=list)


class KenyanPhoneRecognizer(PatternRecognizer):
    """Custom recognizer for Kenyan phone numbers"""

    def __init__(self):
        patterns = [
            Pattern(
                name="kenyan_phone_254",
                regex=r"\+254\s?[17]\d{8}",  # +254 7XXXXXXXX or +254 1XXXXXXXX
                score=0.95
            ),
            Pattern(
                name="kenyan_phone_0",
                regex=r"\b0[17]\d{8}\b",  # 07XXXXXXXX or 01XXXXXXXX
                score=0.9
            ),
            Pattern(
                name="kenyan_phone_spaces",
                regex=r"\+254\s?\d{3}\s?\d{3}\s?\d{3}",  # +254 712 345 678
                score=0.95
            ),
            Pattern(
                name="kenyan_phone_no_plus",
                regex=r"\b254[17]\d{8}\b",  # 2547XXXXXXXX
                score=0.85
            ),
        ]
        super().__init__(
            supported_entity="KENYAN_PHONE",
            patterns=patterns,
            context=["phone", "call", "caller", "contact", "mobile", "tel", "simu"]
        )


class SwahiliNameRecognizer(PatternRecognizer):
    """Custom recognizer for common Swahili/East African names"""

    def __init__(self):
        # Comprehensive list of common East African names
        common_names = [
            # Kikuyu names
            "Wanjiru", "Kamau", "Njeri", "Mwangi", "Wanjiku", "Karanja", "Njoroge",
            "Wairimu", "Nyambura", "Muthoni", "Wambui", "Mumbi", "Wangari", "Njoki",
            "Gathoni", "Nyokabi", "Gitau", "Kiarie", "Kimani", "Kariuki", "Macharia",
            # Luo names
            "Otieno", "Akinyi", "Omondi", "Adhiambo", "Ochieng", "Awino", "Oduor",
            "Onyango", "Akoth", "Owino", "Auma", "Odhiambo", "Anyango", "Atieno",
            # Kalenjin names
            "Chebet", "Kiplagat", "Rotich", "Kibet", "Jepkorir", "Kosgei", "Kipruto",
            "Chepkoech", "Kipchoge", "Kiptoo", "Cherono", "Tanui", "Kimutai",
            # Luhya names
            "Wekesa", "Nafula", "Simiyu", "Nekesa", "Wasike", "Wanyama", "Barasa",
            "Makokha", "Wafula", "Nasimiyu", "Khisa", "Masinde",
            # Kamba names
            "Mutua", "Mwende", "Musyoka", "Ndinda", "Kioko", "Muthama", "Kilonzo",
            "Musau", "Nthenya", "Wambua", "Mutinda", "Kavata",
            # Coastal/Swahili names (Tanzania & Kenya coast)
            "Mwanaisha", "Bakari", "Hamisi", "Fatuma", "Salim", "Amina", "Hassan",
            "Zainab", "Omar", "Khadija", "Mohamed", "Aisha", "Yusuf", "Halima",
            "Juma", "Rehema", "Saidi", "Rashid", "Mwajuma", "Zawadi", "Mwamini",
            # Tanzanian names
            "Neema", "Baraka", "Mbarako", "Nyanguzi", "Tumaini", "Furaha", "Upendo",
            "Bahati", "Riziki", "Imani", "Asha", "Mwalimu", "Mtumwa", "Mwamvita",
            "Barakako", "Nyawi", "Tumain", "Ester", "Grace", "Happines", "Gift",
        ]

        # Build regex pattern
        name_pattern = "|".join(re.escape(name) for name in common_names)

        patterns = [
            Pattern(
                name="east_african_names",
                regex=rf"\b({name_pattern})\b",
                score=0.75
            ),
        ]
        super().__init__(
            supported_entity="KENYAN_NAME",
            patterns=patterns,
            context=["caller", "victim", "child", "mother", "father", "name",
                     "mtoto", "mama", "baba", "mzazi", "reported", "girl", "boy"]
        )


class KenyanLocationRecognizer(PatternRecognizer):
    """Custom recognizer for Kenyan and Tanzanian locations"""

    def __init__(self):
        locations = [
            # Kenya - Major cities
            "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Thika", "Malindi",
            "Kitale", "Garissa", "Kakamega", "Nyeri", "Meru", "Embu", "Machakos",
            # Kenya - Counties
            "Kiambu", "Kajiado", "Narok", "Turkana", "Samburu", "Kilifi", "Kwale",
            # Kenya - Neighborhoods
            "Kibera", "Mathare", "Eastleigh", "Westlands", "Karen", "Langata",
            "Kasarani", "Embakasi", "Dagoretti", "Ruaraka", "Starehe", "Makadara",
            # Tanzania - Regions/Districts
            "Kagera", "Kilwa", "Arusha", "Tabora", "Dodoma", "Mwanza", "Tanga",
            "Morogoro", "Iringa", "Mbeya", "Kigoma", "Shinyanga", "Singida",
            "Rukwa", "Ruvuma", "Lindi", "Mtwara", "Pwani", "Dar es Salaam",
            "Zanzibar", "Pemba", "Mara", "Geita", "Simiyu", "Njombe", "Katavi",
            # Common area descriptors
            "district", "county", "region", "ward", "village", "town",
        ]

        location_pattern = "|".join(re.escape(loc) for loc in locations)

        patterns = [
            Pattern(
                name="kenyan_locations",
                regex=rf"\b({location_pattern})\b",
                score=0.7
            ),
        ]
        super().__init__(
            supported_entity="KENYAN_LOCATION",
            patterns=patterns,
            context=["location", "address", "from", "area", "county", "mahali", "eneo", "district", "region"]
        )


class PIILogScanner:
    """Main PII scanner for log files"""

    def __init__(self, alert_email: str = None, use_presidio: bool = True, use_spacy: bool = True):
        """
        Initialize PII scanner

        Args:
            alert_email: Email address to send alerts when PII is detected
            use_presidio: Use Presidio for advanced detection (requires installation)
            use_spacy: Use spaCy NER for entity detection (lightweight alternative)
        """
        self.alert_email = alert_email
        self.detections: List[PIIDetection] = []
        self.use_presidio = use_presidio and PRESIDIO_AVAILABLE
        self.use_spacy = use_spacy and SPACY_AVAILABLE and not self.use_presidio
        self.nlp = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        if self.use_presidio:
            self._setup_presidio_analyzer()
        elif self.use_spacy:
            self._setup_spacy_analyzer()
        else:
            self._setup_regex_analyzer()

    def _setup_presidio_analyzer(self):
        """Setup Presidio analyzer with custom recognizers"""
        try:
            # Create NLP engine
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
            }
            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()

            # Create analyzer
            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

            # Add custom recognizers
            self.analyzer.registry.add_recognizer(KenyanPhoneRecognizer())
            self.analyzer.registry.add_recognizer(SwahiliNameRecognizer())
            self.analyzer.registry.add_recognizer(KenyanLocationRecognizer())

            # Create anonymizer
            self.anonymizer = AnonymizerEngine()

            self.logger.info("Initialized Presidio analyzer with custom recognizers")

        except Exception as e:
            self.logger.error(f"Failed to initialize Presidio: {e}")
            self.logger.info("Falling back to spaCy or regex-based detection")
            self.use_presidio = False
            if SPACY_AVAILABLE:
                self._setup_spacy_analyzer()
            else:
                self._setup_regex_analyzer()

    def _setup_spacy_analyzer(self):
        """Setup spaCy NER analyzer for entity detection"""
        try:
            # Try to load models in order of preference
            model_names = ["en_core_web_lg", "en_core_web_md", "en_core_web_sm"]
            for model_name in model_names:
                try:
                    self.nlp = spacy.load(model_name)
                    self.logger.info(f"Loaded spaCy model: {model_name}")
                    break
                except OSError:
                    continue

            if self.nlp is None:
                raise RuntimeError("No spaCy model available")

            # Entity types we care about for PII
            self.spacy_entity_types = {
                "PERSON": "PERSON",
                "GPE": "LOCATION",  # Geopolitical entity (countries, cities)
                "LOC": "LOCATION",  # Non-GPE locations
                "ORG": "ORGANIZATION",
                "DATE": "DATE",
                "TIME": "TIME",
                "MONEY": "FINANCIAL",
                "CARDINAL": "NUMBER",  # Numerals
                "FAC": "LOCATION",  # Facilities
            }

            # Also setup regex patterns for things spaCy might miss
            self._setup_supplementary_regex()

            self.logger.info("Initialized spaCy NER analyzer")

        except Exception as e:
            self.logger.error(f"Failed to initialize spaCy: {e}")
            self.logger.info("Falling back to regex-based detection")
            self.use_spacy = False
            self._setup_regex_analyzer()

    def _setup_supplementary_regex(self):
        """Setup supplementary regex patterns for phone numbers, emails, etc."""
        self.supplementary_patterns = [
            # Phone numbers - Kenya
            (re.compile(r'\+254\s?[17]\d{8}'), 'PHONE_NUMBER'),
            (re.compile(r'\b0[17]\d{8}\b'), 'PHONE_NUMBER'),
            # Phone numbers - Tanzania
            (re.compile(r'\+255\s?[67]\d{8}'), 'PHONE_NUMBER'),
            (re.compile(r'\b0[67]\d{8}\b'), 'PHONE_NUMBER'),
            # Generic international phone
            (re.compile(r'\+\d{1,3}\s?\d{9,12}'), 'PHONE_NUMBER'),
            # Email
            (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), 'EMAIL'),
            # Age patterns
            (re.compile(r'\b(\d{1,2})[\s-]?(?:year|yr)[\s-]?old\b', re.I), 'AGE'),
            # ID numbers (generic pattern for national IDs)
            (re.compile(r'\b\d{6,10}\b'), 'ID_NUMBER'),
        ]

    def _analyze_line_spacy(self, line: str) -> List[Dict]:
        """Analyze a line using spaCy NER, focusing on model predictions and user data."""
        results = []

        # Extract text from model predictions and user data fields
        text_to_analyze = self._extract_text_content(line)

        # Skip if no relevant content found
        if not text_to_analyze or len(text_to_analyze.strip()) < 3:
            return results

        # Run spaCy NER
        doc = self.nlp(text_to_analyze)

        for ent in doc.ents:
            if ent.label_ in self.spacy_entity_types:
                # Map spaCy entity type to our standardized types
                entity_type = self.spacy_entity_types[ent.label_]

                # Find position in original line
                start = line.find(ent.text)
                if start == -1:
                    start = 0
                end = start + len(ent.text)

                results.append({
                    'entity_type': entity_type,
                    'start': start,
                    'end': end,
                    'score': 0.85,  # spaCy confidence
                    'text': ent.text  # Store the actual entity text
                })

        # Also check supplementary regex patterns
        for pattern, entity_type in self.supplementary_patterns:
            for match in pattern.finditer(line):
                # Avoid duplicates
                is_duplicate = any(
                    r['start'] <= match.start() < r['end'] or
                    r['start'] < match.end() <= r['end']
                    for r in results
                )
                if not is_duplicate:
                    results.append({
                        'entity_type': entity_type,
                        'start': match.start(),
                        'end': match.end(),
                        'score': 0.8
                    })

        return results

    def _extract_text_content(self, line: str) -> str:
        """Extract readable text from model predictions and user data fields only.

        Focuses on actual content where PII might exist:
        - prediction: model output text
        - transcript/transcription: speech-to-text output
        - translation: translated content
        - summary: summarized content

        Ignores technical fields like call_id, task_id, timestamps, etc.
        """
        extracted_parts = []

        # Pattern 1: 'prediction': '"actual content here"' (SQL INSERT format)
        # Captures the quoted text content, handling escaped quotes
        prediction_patterns = [
            # 'prediction': '"content with spaces and punctuation"'
            r"'prediction':\s*'\"(.+?)\"'",
            # 'transcript': 'content here'
            r"'transcript':\s*'([^']{10,})'",
            # 'transcription': 'content here'
            r"'transcription':\s*'([^']{10,})'",
            # 'translation': 'content here'
            r"'translation':\s*'([^']{10,})'",
            # 'summary': 'content here'
            r"'summary':\s*'([^']{10,})'",
        ]

        for pattern in prediction_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                # Clean the match - remove any remaining SQL artifacts
                clean_text = match.strip()
                # Skip if it looks like a technical value (ID, timestamp, etc.)
                if not re.match(r'^[\d\-\.]+$', clean_text) and len(clean_text) > 5:
                    extracted_parts.append(clean_text)

        # Only return content from target fields - no fallback to full line
        if extracted_parts:
            return " ".join(extracted_parts)

        # No relevant content fields found - skip this line
        return ""

    def _is_technical_line(self, line: str) -> bool:
        """Check if a line contains only technical/system data (no user content)."""
        # Patterns for lines we should skip
        technical_patterns = [
            r'^[\s\d\-T:\.Z]+$',  # Timestamp only
            r'^\s*\[?[A-F0-9\-]{36}\]?\s*$',  # UUID only
            r'^\s*call_id[=:]\s*\d+\s*$',  # call_id assignment
            r'^\s*task_id[=:]\s*[\w\-]+\s*$',  # task_id assignment
            r'INFO:.*:Starting|INFO:.*:Completed|INFO:.*:Processing',  # Status logs
            r'celery.*received|celery.*succeeded',  # Celery task status
            r'^\s*\d+\s*$',  # Just numbers (IDs)
        ]

        for pattern in technical_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True

        return False

    def _setup_regex_analyzer(self):
        """Setup regex-based analyzer (fallback when Presidio not available)"""
        # East African names - expanded list including Swahili and regional names
        east_african_names = [
            # Kenyan names
            "Wanjiru", "Kamau", "Njeri", "Mwangi", "Otieno", "Akinyi", "Omondi",
            "Wanjiku", "Karanja", "Njoroge", "Wairimu", "Nyambura", "Muthoni",
            "Chebet", "Kiplagat", "Rotich", "Kibet", "Wekesa", "Nafula",
            "Mutua", "Mwende", "Musyoka", "Bakari", "Hamisi", "Fatuma",
            # Tanzanian/Swahili names
            "Neema", "Baraka", "Mbarako", "Nyanguzi", "Salim", "Amina", "Hassan",
            "Zainab", "Omar", "Khadija", "Mohamed", "Aisha", "Yusuf", "Halima",
            "Juma", "Rehema", "Saidi", "Mwanaisha", "Rashid", "Mwajuma",
            "Zawadi", "Tumaini", "Furaha", "Upendo", "Bahati", "Riziki",
        ]
        names_pattern = "|".join(re.escape(name) for name in east_african_names)

        # East African locations
        locations = [
            # Kenya
            "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Kibera",
            # Tanzania
            "Kagera", "Kilwa", "Arusha", "Tabora", "Dodoma", "Mwanza", "Tanga",
            "Morogoro", "Iringa", "Mbeya", "Dar es Salaam", "Zanzibar",
            # Uganda
            "Kampala", "Entebbe", "Jinja",
        ]
        locations_pattern = "|".join(re.escape(loc) for loc in locations)

        self.regex_patterns = [
            # Phone numbers - Kenya
            (re.compile(r'\+254\s?[17]\d{8}'), 'PHONE_NUMBER'),
            (re.compile(r'\b0[17]\d{8}\b'), 'PHONE_NUMBER'),
            # Phone numbers - Tanzania
            (re.compile(r'\+255\s?[67]\d{8}'), 'PHONE_NUMBER'),
            (re.compile(r'\b0[67]\d{8}\b'), 'PHONE_NUMBER'),

            # Email
            (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), 'EMAIL'),

            # Known East African names
            (re.compile(rf'\b({names_pattern})\b', re.I), 'PERSON'),

            # East African locations
            (re.compile(rf'\b({locations_pattern})\b', re.I), 'LOCATION'),

            # Names in context patterns - detects names mentioned with context words
            # Pattern: "named X" or "name is X" or "caller X"
            (re.compile(r'\b(?:named?|caller|victim|child|mother|father|parent)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'), 'PERSON'),

            # Pattern: "X from [location]" - person mentioned with location
            (re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+from\s+[A-Z][a-z]+\b'), 'PERSON'),

            # Pattern: Multi-word proper names (2-3 capitalized words together)
            (re.compile(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'), 'PERSON'),

            # Age patterns that might indicate a person being discussed
            (re.compile(r'\b(\d{1,2})[\s-]?(?:year|yr)[\s-]?old\b', re.I), 'AGE'),
        ]
        self.logger.info("Initialized regex-based analyzer with expanded patterns")

    def _analyze_line_presidio(self, line: str) -> List[Dict]:
        """Analyze a line using Presidio, focusing on model predictions and user data."""
        # Extract only relevant content (predictions, transcripts, etc.)
        text_to_analyze = self._extract_text_content(line)

        # Skip if no relevant content found
        if not text_to_analyze or len(text_to_analyze.strip()) < 3:
            return []

        results = self.analyzer.analyze(
            text=text_to_analyze,
            entities=[
                "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS",
                "LOCATION", "DATE_TIME", "KENYAN_PHONE",
                "KENYAN_NAME", "KENYAN_LOCATION"
            ],
            language='en'
        )

        # Extract entity text from the analyzed content and find position in original line
        parsed_results = []
        for r in results:
            entity_text = text_to_analyze[r.start:r.end]

            # Find where this entity appears in the original line
            start_in_line = line.find(entity_text)
            if start_in_line == -1:
                start_in_line = 0
            end_in_line = start_in_line + len(entity_text)

            parsed_results.append({
                'entity_type': r.entity_type,
                'start': start_in_line,
                'end': end_in_line,
                'score': r.score,
                'text': entity_text  # Store extracted text
            })

        return parsed_results

    def _analyze_line_regex(self, line: str) -> List[Dict]:
        """Analyze a line using regex patterns"""
        results = []
        for pattern, entity_type in self.regex_patterns:
            for match in pattern.finditer(line):
                results.append({
                    'entity_type': entity_type,
                    'start': match.start(),
                    'end': match.end(),
                    'score': 0.8  # Fixed confidence for regex
                })
        return results

    def scan_log_file(self, log_file: Path) -> Tuple[int, int]:
        """
        Scan a single log file for PII

        Args:
            log_file: Path to log file

        Returns:
            Tuple of (total_lines, lines_with_pii)
        """
        self.logger.info(f"Scanning: {log_file}")

        total_lines = 0
        lines_with_pii = 0

        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    total_lines += 1

                    # Analyze line for PII
                    if self.use_presidio:
                        results = self._analyze_line_presidio(line)
                    elif self.use_spacy:
                        results = self._analyze_line_spacy(line)
                    else:
                        results = self._analyze_line_regex(line)

                    if results:
                        lines_with_pii += 1

                        # Record each detection
                        for result in results:
                            # Use pre-extracted text if available, otherwise extract from line
                            entity_text = result.get('text', line[result['start']:result['end']])

                            # Get context (50 chars before and after)
                            context_start = max(0, result['start'] - 50)
                            context_end = min(len(line), result['end'] + 50)
                            context = line[context_start:context_end].strip()

                            detection = PIIDetection(
                                timestamp=datetime.now().isoformat(),
                                log_file=str(log_file),
                                line_number=line_num,
                                entity_type=result['entity_type'],
                                entity_text=entity_text,
                                confidence=result['score'],
                                context=context
                            )
                            self.detections.append(detection)

                            self.logger.warning(
                                f"PII detected in {log_file.name}:{line_num} - "
                                f"{result['entity_type']}: {entity_text[:20]}... "
                                f"(confidence: {result['score']:.2f})"
                            )

        except Exception as e:
            self.logger.error(f"Error scanning {log_file}: {e}")

        return total_lines, lines_with_pii

    def scan_directory(self, log_dir: Path, pattern: str = "*.log") -> ScanResult:
        """
        Scan all log files in a directory

        Args:
            log_dir: Path to log directory
            pattern: Glob pattern for log files (default: *.log)

        Returns:
            ScanResult with scan statistics
        """
        self.logger.info(f"Scanning directory: {log_dir}")

        log_files = list(log_dir.glob(pattern))
        # Also check for common log patterns
        log_files.extend(log_dir.glob("*.txt"))

        # Remove duplicates
        log_files = list(set(log_files))

        self.logger.info(f"Found {len(log_files)} log files")

        total_lines = 0
        total_lines_with_pii = 0
        high_risk_files = []

        for log_file in log_files:
            lines, lines_with_pii = self.scan_log_file(log_file)
            total_lines += lines
            total_lines_with_pii += lines_with_pii

            # Mark high-risk files (>5% PII)
            if lines > 0 and (lines_with_pii / lines) > 0.05:
                high_risk_files.append(str(log_file))

        result = ScanResult(
            scan_timestamp=datetime.now().isoformat(),
            files_scanned=len(log_files),
            total_lines=total_lines,
            lines_with_pii=total_lines_with_pii,
            pii_percentage=(total_lines_with_pii / total_lines * 100) if total_lines > 0 else 0,
            total_detections=len(self.detections),
            detections_by_type=self._count_by_type(),
            high_risk_files=high_risk_files
        )

        return result

    def _count_by_type(self) -> Dict[str, int]:
        """Count detections by entity type"""
        counts: Dict[str, int] = {}
        for detection in self.detections:
            counts[detection.entity_type] = counts.get(detection.entity_type, 0) + 1
        return counts

    def _redact_by_positions(self, text: str, detections: List[Dict]) -> str:
        """Redact text based on detection positions"""
        # Sort by start position in reverse to avoid offset issues
        sorted_detections = sorted(detections, key=lambda x: x['start'], reverse=True)

        result = text
        for detection in sorted_detections:
            start = detection['start']
            end = detection['end']
            entity_type = detection['entity_type']
            result = result[:start] + f'[REDACTED-{entity_type}]' + result[end:]

        return result

    def redact_log_file(self, input_file: Path, output_file: Path) -> int:
        """
        Create a redacted version of a log file

        Args:
            input_file: Original log file
            output_file: Redacted log file

        Returns:
            Number of lines redacted
        """
        self.logger.info(f"Redacting: {input_file} -> {output_file}")

        lines_redacted = 0

        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:

            for line in infile:
                if self.use_presidio:
                    # Analyze line
                    results = self.analyzer.analyze(
                        text=line,
                        entities=[
                            "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS",
                            "LOCATION", "DATE_TIME", "KENYAN_PHONE",
                            "KENYAN_NAME", "KENYAN_LOCATION"
                        ],
                        language='en'
                    )

                    if results:
                        # Anonymize the line
                        anonymized = self.anonymizer.anonymize(
                            text=line,
                            analyzer_results=results
                        )
                        outfile.write(anonymized.text)
                        lines_redacted += 1
                    else:
                        outfile.write(line)
                elif self.use_spacy:
                    # spaCy-based redaction
                    results = self._analyze_line_spacy(line)
                    if results:
                        redacted_line = self._redact_by_positions(line, results)
                        outfile.write(redacted_line)
                        lines_redacted += 1
                    else:
                        outfile.write(line)
                else:
                    # Regex-based redaction
                    redacted_line = line
                    for pattern, entity_type in self.regex_patterns:
                        redacted_line = pattern.sub(f'[REDACTED-{entity_type}]', redacted_line)

                    if redacted_line != line:
                        lines_redacted += 1

                    outfile.write(redacted_line)

        self.logger.info(f"Redacted {lines_redacted} lines")
        return lines_redacted

    def generate_audit_report(self, output_file: Path):
        """
        Generate detailed audit report of PII detections

        Args:
            output_file: Path to save report (JSON format)
        """
        scanner_type = "presidio" if self.use_presidio else ("spacy" if self.use_spacy else "regex")
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "scanner_type": scanner_type,
            "summary": {
                "total_detections": len(self.detections),
                "detections_by_type": self._count_by_type(),
                "files_with_pii": len(set(d.log_file for d in self.detections))
            },
            "detections": [asdict(d) for d in self.detections]
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Audit report saved to: {output_file}")

        # Also create human-readable summary
        summary_file = output_file.with_suffix('.txt')
        with open(summary_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("PII Detection Audit Report - OpenCHS AI Service\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Scanner Type: {report['scanner_type']}\n")
            f.write(f"Total Detections: {len(self.detections)}\n")
            f.write(f"Files with PII: {report['summary']['files_with_pii']}\n\n")

            f.write("Detections by Type:\n")
            f.write("-" * 40 + "\n")
            for entity_type, count in sorted(report['summary']['detections_by_type'].items()):
                f.write(f"  {entity_type}: {count}\n")

            if self.detections:
                f.write("\n" + "=" * 60 + "\n")
                f.write("Sample Detections (first 20):\n")
                f.write("=" * 60 + "\n\n")

                for detection in self.detections[:20]:
                    f.write(f"File: {detection.log_file}:{detection.line_number}\n")
                    f.write(f"Type: {detection.entity_type}\n")
                    f.write(f"Text: {detection.entity_text}\n")
                    f.write(f"Confidence: {detection.confidence:.2f}\n")
                    f.write(f"Context: ...{detection.context}...\n")
                    f.write("-" * 40 + "\n\n")

        self.logger.info(f"Human-readable summary saved to: {summary_file}")

    def send_alert(self, results: ScanResult):
        """
        Send email alert about PII detections

        Args:
            results: Scan results
        """
        if not self.alert_email:
            return

        alert_message = f"""
PII DETECTION ALERT - OpenCHS AI Service
=========================================

Scan completed at: {results.scan_timestamp}

Summary:
- Files scanned: {results.files_scanned}
- Total lines: {results.total_lines}
- Lines with PII: {results.lines_with_pii}
- PII percentage: {results.pii_percentage:.2f}%
- Total detections: {results.total_detections}

High-risk files (>5% PII):
{chr(10).join('- ' + f for f in results.high_risk_files) if results.high_risk_files else '- None'}

Detections by type:
{chr(10).join(f'- {k}: {v}' for k, v in results.detections_by_type.items())}

ACTION REQUIRED:
1. Review the audit report for details
2. Investigate why PII is being logged
3. Ensure PIISanitizingFilter is enabled in application
4. Consider redacting existing logs

This is an automated alert from the PII scanning system.
        """

        self.logger.warning(f"ALERT: PII detected!\n{alert_message}")

        # TODO: Implement actual email sending
        # For now, just log the alert
        if self.alert_email:
            self.logger.info(f"Alert would be sent to: {self.alert_email}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PII Detection Scanner for OpenCHS Logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a directory
  python pii_log_scanner.py --scan /var/log/openchs/

  # Scan with specific pattern
  python pii_log_scanner.py --scan /var/log/openchs/ --pattern "celery*.log"

  # Redact a log file
  python pii_log_scanner.py --redact app.log app_sanitized.log

  # Scan with email alerts
  python pii_log_scanner.py --scan /var/log/ --alert-email admin@openchs.org
        """
    )
    parser.add_argument(
        '--scan',
        type=Path,
        help='Directory or file to scan for PII'
    )
    parser.add_argument(
        '--redact',
        nargs=2,
        metavar=('INPUT', 'OUTPUT'),
        help='Redact PII from INPUT log file, save to OUTPUT'
    )
    parser.add_argument(
        '--alert-email',
        help='Email address to send alerts when PII is detected'
    )
    parser.add_argument(
        '--report',
        type=Path,
        default=Path('pii_audit_report.json'),
        help='Path to save audit report (default: pii_audit_report.json)'
    )
    parser.add_argument(
        '--pattern',
        default='*.log',
        help='Glob pattern for log files (default: *.log)'
    )
    parser.add_argument(
        '--no-presidio',
        action='store_true',
        help='Use regex-only detection (faster, less accurate)'
    )

    args = parser.parse_args()

    # Check for at least one action
    if not args.scan and not args.redact:
        parser.print_help()
        return 1

    # Initialize scanner
    scanner = PIILogScanner(
        alert_email=args.alert_email,
        use_presidio=not args.no_presidio
    )

    if args.scan:
        # Scan mode
        scan_path = Path(args.scan)

        if scan_path.is_file():
            # Scan single file
            total_lines, lines_with_pii = scanner.scan_log_file(scan_path)
            results = ScanResult(
                scan_timestamp=datetime.now().isoformat(),
                files_scanned=1,
                total_lines=total_lines,
                lines_with_pii=lines_with_pii,
                pii_percentage=(lines_with_pii / total_lines * 100) if total_lines > 0 else 0,
                total_detections=len(scanner.detections),
                detections_by_type=scanner._count_by_type()
            )
        elif scan_path.is_dir():
            # Scan directory
            results = scanner.scan_directory(scan_path, pattern=args.pattern)
        else:
            print(f"Error: {scan_path} is not a valid file or directory")
            return 1

        # Print results
        print("\n" + "=" * 60)
        print("PII Detection Results - OpenCHS AI Service")
        print("=" * 60)
        print(f"Files scanned: {results.files_scanned}")
        print(f"Total lines: {results.total_lines}")
        print(f"Lines with PII: {results.lines_with_pii}")
        print(f"PII percentage: {results.pii_percentage:.2f}%")
        print(f"Total detections: {results.total_detections}")

        if results.detections_by_type:
            print("\nDetections by type:")
            for entity_type, count in sorted(results.detections_by_type.items()):
                print(f"  {entity_type}: {count}")

        if results.high_risk_files:
            print("\nHigh-risk files (>5% PII):")
            for f in results.high_risk_files:
                print(f"  - {f}")

        # Generate audit report
        scanner.generate_audit_report(args.report)
        print(f"\nAudit report saved to: {args.report}")

        # Send alert if configured and PII found
        if args.alert_email and results.total_detections > 0:
            scanner.send_alert(results)

        # Return exit code based on findings
        if results.pii_percentage > 5.0:
            print("\n[WARNING] High PII percentage detected!")
            return 2  # Warning exit code

    elif args.redact:
        # Redact mode
        input_file, output_file = args.redact
        lines_redacted = scanner.redact_log_file(Path(input_file), Path(output_file))
        print(f"Redacted {lines_redacted} lines")
        print(f"Output saved to: {output_file}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
