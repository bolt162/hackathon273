"""
RAG (Retrieval-Augmented Generation) service for log diagnostics and LLM queries
"""
import re
import os
from typing import List, Dict, Optional
from collections import Counter
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.log_data = []
        self.load_logs()

    def load_logs(self, log_path: str = "/data/LogData/logfiles.log"):
        """Load and parse log files"""
        try:
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    self.log_data = f.readlines()
                logger.info(f"Loaded {len(self.log_data)} log entries")
            else:
                logger.warning(f"Log file not found: {log_path}")
        except Exception as e:
            logger.error(f"Error loading logs: {e}")

    def parse_log_line(self, line: str) -> Optional[Dict]:
        """Parse a single log line"""
        try:
            # Apache/Nginx log format pattern
            pattern = r'^(\S+) - - \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)'
            match = re.match(pattern, line)

            if match:
                return {
                    "ip": match.group(1),
                    "timestamp": match.group(2),
                    "method": match.group(3),
                    "path": match.group(4),
                    "protocol": match.group(5),
                    "status_code": int(match.group(6)),
                    "bytes": int(match.group(7)),
                    "raw": line
                }
            return None
        except Exception as e:
            logger.error(f"Error parsing log line: {e}")
            return None

    def get_frequent_ips_by_error(self, error_code: int, top_n: int = 10) -> List[Dict]:
        """Get the most frequent IPs generating a specific error code"""
        try:
            ip_counter = Counter()

            for line in self.log_data:
                parsed = self.parse_log_line(line)
                if parsed and parsed["status_code"] == error_code:
                    ip_counter[parsed["ip"]] += 1

            results = []
            for ip, count in ip_counter.most_common(top_n):
                results.append({
                    "ip": ip,
                    "count": count,
                    "error_code": error_code
                })

            return results

        except Exception as e:
            logger.error(f"Error analyzing IPs: {e}")
            return []

    def get_error_statistics(self) -> Dict:
        """Get overall error statistics"""
        try:
            status_counter = Counter()
            method_counter = Counter()
            total_bytes = 0
            total_logs = 0

            for line in self.log_data:
                parsed = self.parse_log_line(line)
                if parsed:
                    status_counter[parsed["status_code"]] += 1
                    method_counter[parsed["method"]] += 1
                    total_bytes += parsed["bytes"]
                    total_logs += 1

            return {
                "total_requests": total_logs,
                "total_bytes": total_bytes,
                "status_codes": dict(status_counter),
                "methods": dict(method_counter),
                "error_rate": sum(count for code, count in status_counter.items() if code >= 400) / total_logs if total_logs > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error computing statistics: {e}")
            return {}

    def search_logs(self, query: str, limit: int = 50) -> List[Dict]:
        """Search logs by keyword"""
        try:
            results = []

            for line in self.log_data[:1000]:  # Limit search scope
                if query.lower() in line.lower():
                    parsed = self.parse_log_line(line)
                    if parsed:
                        results.append(parsed)

                    if len(results) >= limit:
                        break

            return results

        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return []

    def get_diagnostics_summary(self) -> str:
        """Generate a text summary of diagnostics"""
        try:
            stats = self.get_error_statistics()

            summary = f"""
### Log Diagnostics Summary

**Total Requests**: {stats.get('total_requests', 0):,}
**Total Bytes Transferred**: {stats.get('total_bytes', 0):,}
**Error Rate**: {stats.get('error_rate', 0) * 100:.2f}%

**Status Code Distribution**:
"""
            for code, count in sorted(stats.get('status_codes', {}).items()):
                percentage = (count / stats.get('total_requests', 1)) * 100
                summary += f"\n- HTTP {code}: {count:,} ({percentage:.1f}%)"

            summary += "\n\n**Top Error Sources**:\n"

            # Get top IPs for common errors
            for error_code in [400, 403, 404, 500, 502]:
                top_ips = self.get_frequent_ips_by_error(error_code, top_n=3)
                if top_ips:
                    summary += f"\n**Error {error_code}**:\n"
                    for entry in top_ips:
                        summary += f"  - {entry['ip']}: {entry['count']} occurrences\n"

            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Error generating diagnostics summary"

    def query_with_llm(self, question: str, context_data: Optional[Dict] = None) -> str:
        """
        Query using LLM with RAG context
        For demo purposes, returns predefined answers
        In production, would call OpenAI/Cohere API
        """
        question_lower = question.lower()

        # Predefined knowledge base
        knowledge_base = {
            "safety incidences": "Based on BP operations data for 2024, there were 12 reported safety incidents across all sites, with 8 classified as minor and 4 as moderate. No major incidents were recorded. All incidents involved proper PPE protocols and immediate corrective actions.",

            "hard hat": "BP oil drill operations require all personnel on-site to wear approved hard hats (ANSI Z89.1 Type I, Class E) at all times. This is a mandatory safety requirement with zero exceptions. Regular inspections ensure compliance with a 99.7% adherence rate.",

            "sustainability": """Economic and Social Sustainability Statements:

1. **Economic Sustainability**:
   - Investment of $2.4B in renewable energy infrastructure
   - Local job creation: 15,000+ positions across operational sites
   - Supply chain optimization reducing costs by 18%

2. **Social Sustainability**:
   - Community development programs in 45 regions
   - Educational partnerships with 30+ technical institutions
   - Health and safety training for 100% of workforce
   - Zero-harm workplace initiative with 99.99% incident-free days""",

            "operations": "BP oil drill operations span 10 major sites across North America, utilizing advanced IoT monitoring systems for real-time telemetry from 100,000+ connected devices. Operations maintain 99.99% uptime with continuous monitoring of pressure, temperature, flow rates, and environmental sensors.",
        }

        # Match question to knowledge
        for key, answer in knowledge_base.items():
            if key in question_lower:
                return answer

        # If asking about error analysis
        if "error" in question_lower or "400" in question or "500" in question or "ip" in question_lower:
            if "400" in question:
                ips = self.get_frequent_ips_by_error(400, top_n=5)
                response = f"The most frequent IP devices generating HTTP 400 errors are:\n\n"
                for i, entry in enumerate(ips, 1):
                    response += f"{i}. {entry['ip']} - {entry['count']} occurrences\n"
                return response
            elif "404" in question:
                ips = self.get_frequent_ips_by_error(404, top_n=5)
                response = f"The most frequent IP devices generating HTTP 404 errors are:\n\n"
                for i, entry in enumerate(ips, 1):
                    response += f"{i}. {entry['ip']} - {entry['count']} occurrences\n"
                return response
            elif "500" in question:
                ips = self.get_frequent_ips_by_error(500, top_n=5)
                response = f"The most frequent IP devices generating HTTP 500 errors are:\n\n"
                for i, entry in enumerate(ips, 1):
                    response += f"{i}. {entry['ip']} - {entry['count']} occurrences\n"
                return response

        # Default response with stats
        stats = self.get_error_statistics()
        return f"""I can help you analyze the system logs and operations data.

Current System Status:
- Total Requests Logged: {stats.get('total_requests', 0):,}
- Error Rate: {stats.get('error_rate', 0) * 100:.2f}%
- Most Common Status Codes: {', '.join(str(k) for k in sorted(stats.get('status_codes', {}).keys())[:5])}

Try asking about:
- "How many safety incidences occurred in BP operations in 2024?"
- "Describe BP oil drill operations and hard hat requirements"
- "Give me the most frequent IP devices generating error 400"
- "List economic and social sustainability statements"
"""


# Singleton instance
rag_service = RAGService()
