"""
Enhanced file manager supporting both TCP and HTTP operations
"""
import os
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

class EnhancedFileManager:
    """Enhanced file manager supporting both TCP and HTTP operations"""

    def __init__(self, virtual_files: List[str], thumbnail_path: str = None):
        # TCP compatibility
        self.virtual_files = virtual_files  # Shared with TCP
        self.thumbnail_path = thumbnail_path or "standard_thumbnail.png"

        # HTTP specific storage
        self.uploaded_files = {}  # filename -> file data
        self.file_metadata = {}   # filename -> metadata dict
        self.file_thumbnails = {}  # filename -> base64 thumbnail data

        # Initialize with some default metadata for virtual files
        self._initialize_default_metadata()

    def _initialize_default_metadata(self):
        """Initialize default metadata for existing virtual files"""
        default_metadata = {
            "printingTime": 3600,  # 1 hour default
            "uploadTime": datetime.now().isoformat(),
            "fileSize": 1024 * 1024,  # 1MB default
            "totalFilamentWeight": 25.5,
            "useMatlStation": False,
            "gcodeToolCnt": 1,
            "gcodeToolDatas": []
        }

        for filename in self.virtual_files:
            if filename not in self.file_metadata:
                metadata = default_metadata.copy()
                # Add some variation for AD5X files
                if filename.endswith('.3mf') and 'multi' in filename.lower():
                    metadata.update({
                        "printingTime": 7200,  # 2 hours
                        "useMatlStation": True,
                        "gcodeToolCnt": 3,  # 3 tools for more complex test
                        "totalFilamentWeight": 41.1,
                        "gcodeToolDatas": [
                            {
                                "toolId": 0,
                                "slotId": 1,
                                "materialName": "PLA",
                                "materialColor": "#FF0000",
                                "filamentWeight": 15.2
                            },
                            {
                                "toolId": 1,
                                "slotId": 2,
                                "materialName": "PLA",
                                "materialColor": "#00FF00",
                                "filamentWeight": 13.8
                            },
                            {
                                "toolId": 2,
                                "slotId": 3,
                                "materialName": "ABS",
                                "materialColor": "#0000FF",
                                "filamentWeight": 12.1
                            }
                        ]
                    })
                self.file_metadata[filename] = metadata

    def add_uploaded_file(self, filename: str, file_data: bytes, metadata: Dict = None):
        """Add file from HTTP upload"""
        self.uploaded_files[filename] = file_data

        if metadata:
            self.file_metadata[filename] = metadata
        else:
            # Create default metadata
            self.file_metadata[filename] = {
                "printingTime": 3600,
                "uploadTime": datetime.now().isoformat(),
                "fileSize": len(file_data),
                "totalFilamentWeight": 25.0,
                "useMatlStation": False,
                "gcodeToolCnt": 1,
                "gcodeToolDatas": []
            }

        # Add to virtual_files for TCP compatibility
        if filename not in self.virtual_files:
            self.virtual_files.append(filename)

    def get_file_list(self, api_type: str = "tcp") -> List[str]:
        """Get file list for specific API type"""
        if api_type == "http":
            # Return combined list for HTTP API
            all_files = set(self.virtual_files)
            all_files.update(self.uploaded_files.keys())
            return sorted(list(all_files))
        return self.virtual_files

    def get_recent_file_list(self, printer_mode: str = "5M") -> Union[List[str], List[Dict]]:
        """Get recent file list with mode-appropriate format"""
        files = self.get_file_list("http")

        if printer_mode == "AD5X":
            # Return detailed format for AD5X
            detailed_files = []
            for filename in files[:10]:  # Last 10 files
                metadata = self.file_metadata.get(filename, {})
                file_entry = {
                    "gcodeFileName": filename,
                    "printingTime": metadata.get("printingTime", 3600)
                }

                # Add AD5X specific fields if available
                if metadata.get("totalFilamentWeight"):
                    file_entry["totalFilamentWeight"] = metadata["totalFilamentWeight"]
                if metadata.get("useMatlStation") is not None:
                    file_entry["useMatlStation"] = metadata["useMatlStation"]
                if metadata.get("gcodeToolCnt"):
                    file_entry["gcodeToolCnt"] = metadata["gcodeToolCnt"]
                if metadata.get("gcodeToolDatas"):
                    file_entry["gcodeToolDatas"] = metadata["gcodeToolDatas"]

                detailed_files.append(file_entry)
            return detailed_files
        else:
            # Return simple string array for 5M/5M Pro
            return files[:10]

    def get_file_thumbnail(self, filename: str) -> Optional[str]:
        """Get base64 encoded thumbnail for file"""
        # Check if we have a stored thumbnail
        if filename in self.file_thumbnails:
            return self.file_thumbnails[filename]

        # Try to load default thumbnail
        try:
            if os.path.exists(self.thumbnail_path):
                with open(self.thumbnail_path, 'rb') as f:
                    thumbnail_data = f.read()
                return base64.b64encode(thumbnail_data).decode('utf-8')
        except Exception:
            pass

        return None

    def set_file_thumbnail(self, filename: str, thumbnail_data: str):
        """Set base64 thumbnail data for file"""
        self.file_thumbnails[filename] = thumbnail_data

    def get_file_metadata(self, filename: str) -> Dict:
        """Get metadata for a specific file"""
        return self.file_metadata.get(filename, {})

    def update_file_metadata(self, filename: str, metadata: Dict):
        """Update metadata for a file"""
        if filename in self.file_metadata:
            self.file_metadata[filename].update(metadata)
        else:
            self.file_metadata[filename] = metadata

    def file_exists(self, filename: str) -> bool:
        """Check if file exists in either virtual or uploaded files"""
        return filename in self.virtual_files or filename in self.uploaded_files

    def get_file_data(self, filename: str) -> Optional[bytes]:
        """Get raw file data (for uploaded files only)"""
        return self.uploaded_files.get(filename)

    def remove_file(self, filename: str) -> bool:
        """Remove file from all storage"""
        removed = False

        if filename in self.virtual_files:
            self.virtual_files.remove(filename)
            removed = True

        if filename in self.uploaded_files:
            del self.uploaded_files[filename]
            removed = True

        if filename in self.file_metadata:
            del self.file_metadata[filename]

        if filename in self.file_thumbnails:
            del self.file_thumbnails[filename]

        return removed

    def process_upload_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Process HTTP upload headers into metadata"""
        metadata = {
            "uploadTime": datetime.now().isoformat(),
            "printingTime": 3600,  # Default 1 hour
            "useMatlStation": headers.get('useMatlStation', 'false').lower() == 'true',
            "gcodeToolCnt": int(headers.get('gcodeToolCnt', '1')),
            "totalFilamentWeight": 25.0,  # Default
            "gcodeToolDatas": []
        }

        # Process file size
        if 'fileSize' in headers:
            try:
                metadata['fileSize'] = int(headers['fileSize'])
            except (ValueError, TypeError):
                pass

        # Process material mappings for AD5X
        if 'materialMappings' in headers and metadata['useMatlStation']:
            try:
                # Decode base64 material mappings
                mappings_json = base64.b64decode(headers['materialMappings']).decode('utf-8')
                material_mappings = json.loads(mappings_json)

                # Convert to gcodeToolDatas format
                total_weight = 0
                tool_datas = []
                for mapping in material_mappings:
                    tool_data = {
                        "toolId": mapping.get("toolId", 0),
                        "slotId": mapping.get("slotId", 1),
                        "materialName": mapping.get("materialName", "PLA"),
                        "materialColor": mapping.get("toolMaterialColor", "#FFFFFF"),
                        "filamentWeight": 22.5  # Estimated weight per tool
                    }
                    tool_datas.append(tool_data)
                    total_weight += tool_data["filamentWeight"]

                metadata['gcodeToolDatas'] = tool_datas
                metadata['totalFilamentWeight'] = total_weight

            except Exception as e:
                # If material mapping parsing fails, fall back to defaults
                pass

        return metadata

    def create_test_ad5x_file(self, filename: str = "test_multicolor.3mf"):
        """Create a test multi-color file for AD5X testing"""
        if filename not in self.virtual_files:
            self.virtual_files.append(filename)

        self.file_metadata[filename] = {
            "printingTime": 7200,  # 2 hours
            "uploadTime": datetime.now().isoformat(),
            "fileSize": 2 * 1024 * 1024,  # 2MB
            "totalFilamentWeight": 48.6,
            "useMatlStation": True,
            "gcodeToolCnt": 3,
            "gcodeToolDatas": [
                {
                    "toolId": 0,
                    "slotId": 1,
                    "materialName": "PLA",
                    "materialColor": "#FF0000",
                    "filamentWeight": 16.2
                },
                {
                    "toolId": 1,
                    "slotId": 2,
                    "materialName": "PLA",
                    "materialColor": "#00FF00",
                    "filamentWeight": 16.2
                },
                {
                    "toolId": 2,
                    "slotId": 3,
                    "materialName": "ABS",
                    "materialColor": "#0000FF",
                    "filamentWeight": 16.2
                }
            ]
        }