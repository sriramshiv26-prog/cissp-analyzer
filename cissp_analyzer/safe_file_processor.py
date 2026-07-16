#!/usr/bin/env python3
"""
Safe File Processor - Phase 3C Enhancement
Handles concurrent file access with locking and atomic writes.
Prevents race conditions when multiple processes access exam data.
"""

import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import fcntl
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileLock:
    """Context manager for file-based locking."""

    def __init__(self, lock_path: Path, timeout: int = 30):
        """
        Initialize file lock.

        Args:
            lock_path: Path to lock file
            timeout: Maximum seconds to wait for lock
        """
        self.lock_path = Path(lock_path)
        self.timeout = timeout
        self.lock_file = None
        self.acquired = False

    def __enter__(self):
        """Acquire lock."""
        start_time = time.time()

        while True:
            try:
                # Create lock file with exclusive access
                self.lock_file = open(self.lock_path, "w")

                # Try to acquire exclusive lock (non-blocking on some systems)
                try:
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.acquired = True
                    logger.debug(f"✓ Acquired lock: {self.lock_path}")
                    return self

                except (IOError, OSError):
                    # Lock is held by another process
                    self.lock_file.close()
                    self.lock_file = None

                    # Check timeout
                    elapsed = time.time() - start_time
                    if elapsed > self.timeout:
                        raise TimeoutError(f"Could not acquire lock after {self.timeout}s")

                    # Wait before retrying
                    time.sleep(0.1)

            except Exception as e:
                if self.lock_file:
                    self.lock_file.close()
                raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock."""
        if self.lock_file and self.acquired:
            try:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                self.lock_file.close()
                self.acquired = False
                logger.debug(f"✓ Released lock: {self.lock_path}")
            except Exception as e:
                logger.error(f"Error releasing lock: {str(e)}")


class SafeFileProcessor:
    """Safe file processing with locking and atomic writes."""

    def __init__(self, exam_folder: Path):
        """
        Initialize safe file processor.

        Args:
            exam_folder: Path to exam folder
        """
        self.exam_folder = Path(exam_folder)
        self.lock_dir = self.exam_folder / ".locks"
        self.lock_dir.mkdir(exist_ok=True)
        self.state_file = self.exam_folder / ".exam_state.json"

    def read_with_lock(self, file_path: Path, timeout: int = 30) -> Optional[Dict]:
        """
        Read file safely with locking.

        Args:
            file_path: Path to file to read
            timeout: Lock timeout in seconds

        Returns:
            File contents as dictionary or None if failed
        """
        lock_path = self.lock_dir / f"{file_path.name}.lock"

        try:
            with FileLock(lock_path, timeout):
                if not file_path.exists():
                    logger.warning(f"File not found: {file_path}")
                    return None

                with open(file_path, "r") as f:
                    data = json.load(f)
                    logger.debug(f"✓ Read with lock: {file_path.name}")
                    return data

        except TimeoutError as e:
            logger.error(f"Lock timeout reading {file_path.name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error reading {file_path.name}: {str(e)}")
            return None

    def write_atomic(self, file_path: Path, data: Dict, timeout: int = 30) -> bool:
        """
        Write file atomically with locking.

        Strategy:
        1. Acquire lock
        2. Write to temporary file
        3. Verify data integrity (checksum)
        4. Atomic rename to target
        5. Release lock

        Args:
            file_path: Path to file to write
            data: Dictionary to write
            timeout: Lock timeout in seconds

        Returns:
            True if successful, False otherwise
        """
        lock_path = self.lock_dir / f"{file_path.name}.lock"
        temp_path = file_path.with_suffix(".tmp")

        try:
            with FileLock(lock_path, timeout):
                # Step 1: Write to temporary file
                with open(temp_path, "w") as f:
                    json.dump(data, f, indent=2)

                # Step 2: Verify by reading back
                with open(temp_path, "r") as f:
                    verify_data = json.load(f)

                if verify_data != data:
                    raise ValueError("Data verification failed")

                # Step 3: Atomic rename
                try:
                    # On POSIX systems, rename is atomic
                    os.replace(str(temp_path), str(file_path))
                except Exception as e:
                    # Fallback for Windows
                    if file_path.exists():
                        file_path.unlink()
                    temp_path.rename(file_path)

                logger.info(f"✓ Atomic write: {file_path.name}")
                return True

        except TimeoutError as e:
            logger.error(f"Lock timeout writing {file_path.name}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error writing {file_path.name}: {str(e)}")
            if temp_path.exists():
                temp_path.unlink()
            return False

    def safe_update(self, file_path: Path, update_fn, timeout: int = 30) -> bool:
        """
        Read, update, write safely (read-modify-write).

        Args:
            file_path: Path to file
            update_fn: Function that takes old data and returns new data
            timeout: Lock timeout

        Returns:
            True if successful
        """
        lock_path = self.lock_dir / f"{file_path.name}.lock"

        try:
            with FileLock(lock_path, timeout):
                # Read current data
                if file_path.exists():
                    with open(file_path, "r") as f:
                        data = json.load(f)
                else:
                    data = {}

                # Update
                new_data = update_fn(data)

                # Write
                with open(file_path, "w") as f:
                    json.dump(new_data, f, indent=2)

                logger.debug(f"✓ Safe update: {file_path.name}")
                return True

        except Exception as e:
            logger.error(f"Error in safe_update: {str(e)}")
            return False

    def detect_conflicts(self, file_path: Path) -> Optional[Dict]:
        """
        Detect concurrent modification conflicts.

        Checks:
        - File modification time
        - File size changes
        - Data hash changes

        Returns:
            Conflict info if detected, None if no conflict
        """
        metadata_file = self.lock_dir / f"{file_path.name}.metadata"

        try:
            if not file_path.exists():
                return None

            # Get current file info
            stat = file_path.stat()
            with open(file_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            current_metadata = {
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "hash": file_hash,
                "timestamp": datetime.now().isoformat(),
            }

            # Compare with previous metadata
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    previous = json.load(f)

                conflicts = []
                if current_metadata["size"] != previous.get("size"):
                    conflicts.append("file_size_changed")
                if current_metadata["hash"] != previous.get("hash"):
                    conflicts.append("content_changed")

                if conflicts:
                    logger.warning(
                        f"⚠️  Conflict detected in {file_path.name}: {conflicts}"
                    )
                    return {
                        "file": str(file_path),
                        "conflicts": conflicts,
                        "previous": previous,
                        "current": current_metadata,
                    }

            # Save current metadata
            with open(metadata_file, "w") as f:
                json.dump(current_metadata, f, indent=2)

            return None

        except Exception as e:
            logger.error(f"Error detecting conflicts: {str(e)}")
            return None

    def cleanup_locks(self, max_age_seconds: int = 3600) -> int:
        """
        Clean up stale lock files.

        Removes lock files older than max_age_seconds (default: 1 hour).

        Args:
            max_age_seconds: Maximum lock file age

        Returns:
            Number of locks cleaned
        """
        count = 0
        current_time = time.time()

        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                age = current_time - lock_file.stat().st_mtime

                if age > max_age_seconds:
                    lock_file.unlink()
                    count += 1
                    logger.info(f"Cleaned stale lock: {lock_file.name}")

            except Exception as e:
                logger.warning(f"Error cleaning lock {lock_file.name}: {str(e)}")

        if count > 0:
            logger.info(f"✓ Cleaned {count} stale locks")

        return count

    def get_lock_status(self) -> Dict:
        """
        Get status of all locks.

        Returns:
            Dictionary with lock information
        """
        locks = {}

        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                stat = lock_file.stat()
                locks[lock_file.name] = {
                    "age_seconds": time.time() - stat.st_mtime,
                    "size_bytes": stat.st_size,
                }
            except Exception as e:
                logger.warning(f"Error reading lock {lock_file.name}: {str(e)}")

        return {
            "total_locks": len(locks),
            "locks": locks,
        }
