from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
import re


class VersionInfo(BaseModel):
    major: int
    minor: int
    patch: int
    pre_release: Optional[str] = None
    build_metadata: Optional[str] = None
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version += f"-{self.pre_release}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version
    
    def __lt__(self, other: "VersionInfo") -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        return False
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VersionInfo):
            return False
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre_release == other.pre_release
        )


class VersionManager:
    """版本管理器"""
    
    SEMVER_PATTERN = re.compile(
        r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
        r"(?:-(?P<pre_release>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
        r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
        r"(?:\+(?P<build_metadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )
    
    def __init__(self):
        self._versions: Dict[str, List[VersionInfo]] = {}
    
    def parse_version(self, version_str: str) -> Optional[VersionInfo]:
        """解析版本字符串"""
        match = self.SEMVER_PATTERN.match(version_str)
        if not match:
            return None
        
        return VersionInfo(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            pre_release=match.group("pre_release"),
            build_metadata=match.group("build_metadata")
        )
    
    def register_version(self, service_name: str, version: str) -> bool:
        """注册服务版本"""
        parsed_version = self.parse_version(version)
        if not parsed_version:
            return False
        
        if service_name not in self._versions:
            self._versions[service_name] = []
        
        if parsed_version not in self._versions[service_name]:
            self._versions[service_name].append(parsed_version)
            self._versions[service_name].sort(reverse=True)
        
        return True
    
    def get_latest_version(self, service_name: str) -> Optional[str]:
        """获取最新版本"""
        if service_name not in self._versions or not self._versions[service_name]:
            return None
        return str(self._versions[service_name][0])
    
    def get_all_versions(self, service_name: str) -> List[str]:
        """获取所有版本"""
        if service_name not in self._versions:
            return []
        return [str(v) for v in self._versions[service_name]]
    
    def is_version_compatible(self, service_name: str, required_version: str, available_version: str) -> bool:
        """检查版本兼容性"""
        required = self.parse_version(required_version)
        available = self.parse_version(available_version)
        
        if not required or not available:
            return False
        
        return (
            required.major == available.major
            and available.minor >= required.minor
            and available.patch >= required.patch
        )
    
    def suggest_upgrade(self, service_name: str, current_version: str) -> Optional[str]:
        """建议升级版本"""
        latest = self.get_latest_version(service_name)
        if not latest:
            return None
        
        current = self.parse_version(current_version)
        latest_parsed = self.parse_version(latest)
        
        if current and latest_parsed and latest_parsed > current:
            return latest
        
        return None


# 全局版本管理器实例
version_manager = VersionManager()
