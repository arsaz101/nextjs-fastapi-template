import os
import shutil
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
from datetime import datetime


class FileService:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

    def get_documentation_files(self) -> List[Dict[str, Any]]:
        """
        Get all documentation files in the docs directory.
        """
        files = []
        if not self.docs_root.exists():
            return files

        for file_path in self.docs_root.rglob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                files.append(
                    {
                        "path": str(file_path.relative_to(self.docs_root)),
                        "name": file_path.name,
                        "content": content,
                        "sections": self._extract_sections(content),
                        "size": len(content),
                    }
                )
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

        return files

    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract sections from markdown content.
        """
        sections = []
        lines = content.split("\n")
        current_section = None
        current_content = []

        for i, line in enumerate(lines, 1):
            # Check for headers (h1-h6)
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)

            if header_match:
                # Save previous section
                if current_section:
                    current_section["content"] = "\n".join(current_content).strip()
                    current_section["end_line"] = i - 1
                    sections.append(current_section)

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = {
                    "title": title,
                    "level": level,
                    "start_line": i,
                    "content": "",
                    "end_line": None,
                }
                current_content = []
            else:
                current_content.append(line)

        # Add the last section
        if current_section:
            current_section["content"] = "\n".join(current_content).strip()
            current_section["end_line"] = len(lines)
            sections.append(current_section)

        return sections

    def find_relevant_sections(self, query: str) -> List[Dict[str, Any]]:
        """
        Find sections that might be relevant to the user's query.
        """
        relevant_sections = []
        files = self.get_documentation_files()

        # Simple keyword matching (could be enhanced with embeddings)
        query_lower = query.lower()
        keywords = query_lower.split()

        for file_info in files:
            for section in file_info["sections"]:
                section_text = f"{section['title']} {section['content']}".lower()
                relevance_score = sum(
                    1 for keyword in keywords if keyword in section_text
                )

                if relevance_score > 0:
                    relevant_sections.append(
                        {
                            "file_path": file_info["path"],
                            "section": section,
                            "relevance_score": relevance_score,
                            "content": file_info["content"],
                        }
                    )

        # Sort by relevance score
        relevant_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant_sections[:10]  # Return top 10 most relevant

    def apply_suggestions(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply approved suggestions to documentation files.
        """
        results = {"success": [], "errors": [], "backups": []}

        for suggestion in suggestions:
            try:
                file_path = suggestion.get("file_path")
                if not file_path:
                    results["errors"].append(
                        {
                            "suggestion_id": suggestion.get("id"),
                            "error": "No file path specified",
                        }
                    )
                    continue

                full_path = self.docs_root / file_path
                if not full_path.exists():
                    results["errors"].append(
                        {
                            "suggestion_id": suggestion.get("id"),
                            "error": f"File not found: {file_path}",
                        }
                    )
                    continue

                # Create backup
                backup_path = self._create_backup(full_path)
                results["backups"].append(str(backup_path))

                # Apply the change
                success = self._apply_single_suggestion(full_path, suggestion)

                if success:
                    results["success"].append(
                        {
                            "suggestion_id": suggestion.get("id"),
                            "file_path": file_path,
                            "message": "Successfully applied",
                        }
                    )
                else:
                    results["errors"].append(
                        {
                            "suggestion_id": suggestion.get("id"),
                            "error": "Failed to apply suggestion",
                        }
                    )

            except Exception as e:
                results["errors"].append(
                    {"suggestion_id": suggestion.get("id"), "error": str(e)}
                )

        return results

    def _create_backup(self, file_path: Path) -> Path:
        """
        Create a backup of the file before making changes.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(file_path, backup_path)
        return backup_path

    def _apply_single_suggestion(
        self, file_path: Path, suggestion: Dict[str, Any]
    ) -> bool:
        """
        Apply a single suggestion to a file.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # For now, we'll append the suggestion as a comment
            # This is a simple approach - could be enhanced with more sophisticated diffing
            new_content = self._apply_suggestion_to_content(content, suggestion)

            # Write the updated content
            file_path.write_text(new_content, encoding="utf-8")
            return True

        except Exception as e:
            print(f"Error applying suggestion to {file_path}: {e}")
            return False

    def _apply_suggestion_to_content(
        self, content: str, suggestion: Dict[str, Any]
    ) -> str:
        """
        Apply a suggestion to the content.
        This is a simplified version - could be enhanced with proper diffing.
        """
        suggestion_text = suggestion.get("suggestion", "")
        section = suggestion.get("section", "General")

        # Add a comment with the suggestion
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comment = f"\n\n<!-- TODO: {timestamp} - {section} -->\n<!-- Suggestion: {suggestion_text} -->\n"

        return content + comment

    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get the content of a specific file.
        """
        try:
            full_path = self.docs_root / file_path
            if full_path.exists():
                return full_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

        return None

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all backup files.
        """
        backups = []
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file():
                stat = backup_file.stat()
                backups.append(
                    {
                        "name": backup_file.name,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "path": str(backup_file),
                    }
                )

        return sorted(backups, key=lambda x: x["created"], reverse=True)


# Global file service instance
file_service = FileService()
