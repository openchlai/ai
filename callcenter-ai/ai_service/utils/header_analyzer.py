#!/usr/bin/env python3
"""
Header Analysis Utility for Asterisk Audio Streams
Helps identify call ID patterns in TCP audio data
"""

import struct
import re
from typing import Dict, List, Optional, Tuple

class AsteriskHeaderAnalyzer:
    """Analyze Asterisk audio stream headers to extract call information"""
    
    def __init__(self):
        self.common_patterns = {
            'uuid': re.compile(rb'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE),
            'call_id': re.compile(rb'call[_-]?id[:\s=]([a-zA-Z0-9\-_]+)', re.IGNORECASE),
            'channel': re.compile(rb'channel[:\s=]([a-zA-Z0-9\-_/]+)', re.IGNORECASE),
            'digits': re.compile(rb'\b\d{8,}\b'),  # 8+ digit sequences
            'hex_id': re.compile(rb'\b[0-9a-f]{16,}\b', re.IGNORECASE),  # Long hex sequences
        }
    
    def analyze_packet(self, data: bytes, packet_num: int = 0) -> Dict:
        """Analyze a single packet for header information"""
        analysis = {
            'packet_number': packet_num,
            'size': len(data),
            'hex_dump': data.hex(),
            'ascii_view': data.decode('ascii', errors='replace'),
            'patterns_found': {},
            'potential_call_ids': [],
            'structure_analysis': {}
        }
        
        # Pattern matching
        for pattern_name, pattern in self.common_patterns.items():
            matches = pattern.findall(data)
            if matches:
                analysis['patterns_found'][pattern_name] = [m.decode('ascii', errors='ignore') for m in matches]
        
        # Structure analysis for common header formats
        analysis['structure_analysis'] = self._analyze_structure(data)
        
        # Extract potential call IDs
        analysis['potential_call_ids'] = self._extract_call_ids(data)
        
        return analysis
    
    def _analyze_structure(self, data: bytes) -> Dict:
        """Analyze potential header structures"""
        structure = {
            'starts_with_text': data[:10].decode('ascii', errors='ignore').isprintable(),
            'has_null_bytes': b'\x00' in data,
            'null_positions': [i for i, b in enumerate(data) if b == 0] if b'\x00' in data else [],
            'length_fields': [],
            'potential_separators': []
        }
        
        # Look for length fields (common in binary protocols)
        if len(data) >= 4:
            potential_lengths = []
            for i in range(0, min(16, len(data) - 4)):
                # Try different endianness
                big_endian = struct.unpack('>I', data[i:i+4])[0]
                little_endian = struct.unpack('<I', data[i:i+4])[0]
                
                if 0 < big_endian < len(data) * 2:  # Reasonable length
                    potential_lengths.append({'offset': i, 'value': big_endian, 'endian': 'big'})
                if 0 < little_endian < len(data) * 2:
                    potential_lengths.append({'offset': i, 'value': little_endian, 'endian': 'little'})
            
            structure['length_fields'] = potential_lengths
        
        # Look for common separators
        separators = [b'\r\n', b'\n', b'\r', b'|', b';', b':', b' ']
        for sep in separators:
            if sep in data:
                positions = [i for i in range(len(data)) if data[i:i+len(sep)] == sep]
                if positions:
                    structure['potential_separators'].append({
                        'separator': sep.decode('ascii', errors='replace'),
                        'positions': positions
                    })
        
        return structure
    
    def _extract_call_ids(self, data: bytes) -> List[Dict]:
        """Extract potential call IDs using various heuristics"""
        call_ids = []
        
        # Method 1: Look for UUID patterns
        uuid_matches = self.common_patterns['uuid'].findall(data)
        for match in uuid_matches:
            call_ids.append({
                'type': 'uuid',
                'value': match.decode('ascii'),
                'confidence': 0.9
            })
        
        # Method 2: Look for long numeric sequences (might be timestamps + call ID)
        digit_matches = self.common_patterns['digits'].findall(data)
        for match in digit_matches:
            call_ids.append({
                'type': 'numeric',
                'value': match.decode('ascii'),
                'confidence': 0.6
            })
        
        # Method 3: Look for structured data after known prefixes
        prefixes = [b'CALL:', b'ID:', b'UID:', b'CHANNEL:']
        for prefix in prefixes:
            if prefix in data:
                start_pos = data.find(prefix) + len(prefix)
                # Extract next 32 chars or until separator
                end_pos = start_pos + 32
                for sep in [b'\r', b'\n', b' ', b'\x00']:
                    sep_pos = data.find(sep, start_pos)
                    if sep_pos != -1 and sep_pos < end_pos:
                        end_pos = sep_pos
                
                if start_pos < len(data):
                    potential_id = data[start_pos:end_pos].decode('ascii', errors='ignore').strip()
                    if potential_id:
                        call_ids.append({
                            'type': 'prefixed',
                            'prefix': prefix.decode('ascii'),
                            'value': potential_id,
                            'confidence': 0.8
                        })
        
        return call_ids
    
    def analyze_stream_start(self, initial_packets: List[bytes]) -> Dict:
        """Analyze the beginning of a stream to understand header format"""
        stream_analysis = {
            'total_packets': len(initial_packets),
            'packet_analyses': [],
            'consistent_patterns': {},
            'likely_header_format': None,
            'call_id_candidates': []
        }
        
        # Analyze each packet
        for i, packet in enumerate(initial_packets):
            analysis = self.analyze_packet(packet, i + 1)
            stream_analysis['packet_analyses'].append(analysis)
        
        # Find consistent patterns across packets
        if len(initial_packets) > 1:
            stream_analysis['consistent_patterns'] = self._find_consistent_patterns(
                stream_analysis['packet_analyses']
            )
        
        # Determine likely header format
        stream_analysis['likely_header_format'] = self._determine_header_format(
            stream_analysis['packet_analyses']
        )
        
        # Collect all call ID candidates
        all_candidates = []
        for analysis in stream_analysis['packet_analyses']:
            all_candidates.extend(analysis['potential_call_ids'])
        
        # Deduplicate and rank by confidence
        unique_candidates = {}
        for candidate in all_candidates:
            key = f"{candidate['type']}:{candidate['value']}"
            if key not in unique_candidates or candidate['confidence'] > unique_candidates[key]['confidence']:
                unique_candidates[key] = candidate
        
        stream_analysis['call_id_candidates'] = sorted(
            unique_candidates.values(),
            key=lambda x: x['confidence'],
            reverse=True
        )
        
        return stream_analysis
    
    def _find_consistent_patterns(self, analyses: List[Dict]) -> Dict:
        """Find patterns that appear consistently across multiple packets"""
        consistent = {}
        
        # Check which patterns appear in multiple packets
        pattern_counts = {}
        for analysis in analyses:
            for pattern_name in analysis['patterns_found']:
                pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1
        
        # Patterns that appear in >50% of packets are considered consistent
        threshold = len(analyses) * 0.5
        for pattern_name, count in pattern_counts.items():
            if count >= threshold:
                consistent[pattern_name] = {
                    'appearances': count,
                    'total_packets': len(analyses),
                    'consistency': count / len(analyses)
                }
        
        return consistent
    
    def _determine_header_format(self, analyses: List[Dict]) -> Optional[str]:
        """Determine the most likely header format based on analysis"""
        
        if not analyses:
            return None
        
        first_packet = analyses[0]
        
        # Check for text-based protocol
        if first_packet['structure_analysis']['starts_with_text']:
            return "text_based"
        
        # Check for binary protocol with length fields
        if first_packet['structure_analysis']['length_fields']:
            return "binary_with_length"
        
        # Check for fixed-size headers
        sizes = [a['size'] for a in analyses]
        if len(set(sizes)) == 1 and sizes[0] < 100:  # All same size and small
            return "fixed_size_header"
        
        # Check for mixed content (header + audio)
        if any(a['structure_analysis']['has_null_bytes'] for a in analyses):
            return "mixed_header_audio"
        
        return "unknown"

def format_analysis_report(analysis: Dict) -> str:
    """Format analysis results into a readable report"""
    report = []
    report.append("=" * 60)
    report.append("ASTERISK HEADER ANALYSIS REPORT")
    report.append("=" * 60)
    
    if 'total_packets' in analysis:  # Stream analysis
        report.append(f"Stream Analysis ({analysis['total_packets']} packets)")
        report.append(f"Likely Header Format: {analysis['likely_header_format']}")
        report.append("")
        
        report.append("CALL ID CANDIDATES:")
        for i, candidate in enumerate(analysis['call_id_candidates'][:5], 1):
            report.append(f"  {i}. {candidate['type'].upper()}: {candidate['value']} (confidence: {candidate['confidence']:.1f})")
        
        report.append("")
        report.append("CONSISTENT PATTERNS:")
        for pattern, info in analysis['consistent_patterns'].items():
            report.append(f"  {pattern}: {info['appearances']}/{info['total_packets']} packets ({info['consistency']:.1%})")
            
    else:  # Single packet analysis
        report.append(f"Packet {analysis['packet_number']} Analysis ({analysis['size']} bytes)")
        report.append("")
        report.append(f"Hex: {analysis['hex_dump'][:100]}{'...' if len(analysis['hex_dump']) > 100 else ''}")
        report.append(f"ASCII: {repr(analysis['ascii_view'][:50])}")
        report.append("")
        
        if analysis['potential_call_ids']:
            report.append("POTENTIAL CALL IDs:")
            for cid in analysis['potential_call_ids']:
                report.append(f"  {cid['type']}: {cid['value']} (confidence: {cid['confidence']:.1f})")
    
    report.append("=" * 60)
    return "\n".join(report)

if __name__ == "__main__":
    print("Asterisk Header Analyzer")
    print("This utility analyzes TCP packets to identify call ID patterns")
    print("Use it by importing and calling analyze_packet() or analyze_stream_start()")