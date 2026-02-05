"""
History Storage Module
Saves analysis results to JSON files for tracking over time
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class HistoryStorage:
    """Manages persistent storage of analysis results"""
    
    def __init__(self, data_dir: str = "data/history"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.data_dir / "index.json"
        self._ensure_index()
    
    def _ensure_index(self):
        """Create index file if it doesn't exist"""
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps([], indent=2))
    
    def save_analysis(self, url: str, result: Dict) -> str:
        """Save analysis result and return ID"""
        # Generate ID based on URL and timestamp
        timestamp = datetime.now().isoformat()
        analysis_id = f"hist_{datetime.now().timestamp()}"
        
        # Prepare data
        history_entry = {
            "id": analysis_id,
            "url": url,
            "timestamp": timestamp,
            "seo_score": result['seo']['score'],
            "aeo_score": result['aeo']['score'],
            "title": result.get('metadata', {}).get('title', 'Untitled')
        }
        
        # Save full result to file
        result_file = self.data_dir / f"{analysis_id}.json"
        result_file.write_text(json.dumps(result, indent=2))
        
        # Update index
        index = self._read_index()
        
        # Check if URL already exists in history
        existing_entries = [e for e in index if e['url'] == url]
        
        # Add new entry
        index.append(history_entry)
        
        # Keep only last 100 entries per URL
        if len(existing_entries) >= 100:
            # Remove oldest entry for this URL
            oldest = min(existing_entries, key=lambda x: x['timestamp'])
            index = [e for e in index if e['id'] != oldest['id']]
            # Delete old file
            old_file = self.data_dir / f"{oldest['id']}.json"
            if old_file.exists():
                old_file.unlink()
        
        self._write_index(index)
        
        return analysis_id
    
    def get_history_for_url(self, url: str, limit: int = 20) -> List[Dict]:
        """Get analysis history for a specific URL"""
        index = self._read_index()
        entries = [e for e in index if e['url'] == url]
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return entries[:limit]
    
    def get_all_urls(self) -> List[Dict]:
        """Get list of all analyzed URLs with their latest results"""
        index = self._read_index()
        
        # Group by URL and get latest for each
        url_map = {}
        for entry in index:
            url = entry['url']
            if url not in url_map or entry['timestamp'] > url_map[url]['timestamp']:
                url_map[url] = entry
        
        # Return as list, sorted by timestamp
        results = list(url_map.values())
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return results
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict]:
        """Retrieve full analysis by ID"""
        result_file = self.data_dir / f"{analysis_id}.json"
        
        if not result_file.exists():
            return None
        
        return json.loads(result_file.read_text())
    
    def compare_history(self, url: str, limit: int = 10) -> Dict:
        """Compare recent analyses for a URL to show trends"""
        history = self.get_history_for_url(url, limit)
        
        if len(history) < 2:
            return {
                "trend": "insufficient_data",
                "message": "Need at least 2 analyses to show trends"
            }
        
        # Calculate trends
        seo_scores = [h['seo_score'] for h in reversed(history)]  # Oldest to newest
        aeo_scores = [h['aeo_score'] for h in reversed(history)]
        
        seo_trend = seo_scores[-1] - seo_scores[0]
        aeo_trend = aeo_scores[-1] - aeo_scores[0]
        
        return {
            "trend": "improving" if (seo_trend + aeo_trend) > 0 else "declining",
            "history_count": len(history),
            "seo": {
                "current": seo_scores[-1],
                "previous": seo_scores[-2] if len(seo_scores) > 1 else None,
                "change": seo_trend,
                "scores": seo_scores
            },
            "aeo": {
                "current": aeo_scores[-1],
                "previous": aeo_scores[-2] if len(aeo_scores) > 1 else None,
                "change": aeo_trend,
                "scores": aeo_scores
            },
            "timestamps": [h['timestamp'] for h in reversed(history)]
        }
    
    def delete_history(self, analysis_id: str) -> bool:
        """Delete a specific analysis from history"""
        # Remove from index
        index = self._read_index()
        index = [e for e in index if e['id'] != analysis_id]
        self._write_index(index)
        
        # Delete file
        result_file = self.data_dir / f"{analysis_id}.json"
        if result_file.exists():
            result_file.unlink()
            return True
        
        return False
    
    def _read_index(self) -> List[Dict]:
        """Read index file"""
        try:
            return json.loads(self.index_file.read_text())
        except Exception:
            return []
    
    def _write_index(self, index: List[Dict]):
        """Write index file"""
        self.index_file.write_text(json.dumps(index, indent=2))
