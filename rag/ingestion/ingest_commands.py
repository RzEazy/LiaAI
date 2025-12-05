"""
Ingest command documentation into the vector database.
"""
import json
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vectordb import VectorDB

def create_sample_command_docs() -> List[Dict[str, Any]]:
    """
    Create enhanced command documentation with detailed man page information.
    
    Returns:
        List of document dictionaries
    """
    documents = [
        {
            "text": "Command: ls (Linux/macOS)\nCategory: File Operations\nDescription: List directory contents\nSyntax: ls [OPTION]... [FILE]...\nDetailed Description: List information about the FILEs (the current directory by default). Sort entries alphabetically if none of -cftuvSUX nor --sort is specified.\nCommon Options:\n  -a, --all: Do not ignore entries starting with .\n  -l: Use a long listing format\n  -h, --human-readable: Print human readable sizes\n  -R, --recursive: List subdirectories recursively\n  -t: Sort by modification time\n  -S: Sort by file size\nExamples:\n  ls -la: List all files in long format\n  ls -lh: Show files with human-readable sizes\n  ls -R: List directory tree recursively",
            "metadata": {"command": "ls", "category": "file_operations", "os": "linux_macos", "source": "man_page"}
        },
        {
            "text": "Command: ps (Linux/macOS)\nCategory: Process Management\nDescription: Report a snapshot of the current processes\nSyntax: ps [options]\nDetailed Description: Displays information about a selection of the active processes. Outputs different information based on the options provided.\nCommon Options:\n  aux: List all processes (BSD syntax)\n  -ef: Full format listing (POSIX syntax)\n  -u username: Processes for specific user\n  -p PID: Process by specific ID\nExamples:\n  ps aux: Show all running processes with detailed info\n  ps -ef: Show full process list\n  ps -p 1234: Show specific process",
            "metadata": {"command": "ps", "category": "process_management", "os": "linux_macos", "source": "man_page"}
        },
        {
            "text": "Command: grep (Linux/macOS)\nCategory: Text Processing\nDescription: Search for patterns in files\nSyntax: grep [OPTIONS] PATTERN [FILE...]\nDetailed Description: Grep searches the named input files for lines containing a match to the given PATTERN. By default, grep prints the matching lines.\nCommon Options:\n  -r, -R, --recursive: Read all files under each directory recursively\n  -i, --ignore-case: Ignore case distinctions\n  -n, --line-number: Prefix each line of output with the 1-based line number\n  -v, --invert-match: Invert the sense of matching\n  -E, --extended-regexp: Interpret PATTERN as an extended regular expression\nExamples:\n  grep 'error' logfile.txt: Search for 'error' in logfile\n  grep -r 'function' ./src: Recursively search for 'function' in src directory\n  grep -i 'Error' file.txt: Case-insensitive search",
            "metadata": {"command": "grep", "category": "text_processing", "os": "linux_macos", "source": "man_page"}
        },
        {
            "text": "Command: find (Linux/macOS)\nCategory: File Search\nDescription: Search for files in a directory hierarchy\nSyntax: find [PATH] [EXPRESSION]\nDetailed Description: Find walks a directory tree and evaluates expressions for each file. It supports complex expressions for filtering.\nCommon Expressions:\n  -name pattern: Base of file name matches shell pattern\n  -type f/d/l: File is of type regular file/directory/symbolic link\n  -mtime days: File's data was last modified n days ago\n  -size [+/-]n[bcwkMG]: File uses n units of space\nExamples:\n  find . -name '*.txt': Find all .txt files in current directory\n  find /tmp -type f -mtime +7: Find files older than 7 days\n  find . -size +100M: Find files larger than 100MB",
            "metadata": {"command": "find", "category": "file_search", "os": "linux_macos", "source": "man_page"}
        },
        {
            "text": "Command: mkdir (Cross-platform)\nCategory: File Operations\nDescription: Make directories\nSyntax (Linux/macOS): mkdir [OPTION] DIRECTORY...\nSyntax (Windows): mkdir [drive:]path\nDetailed Description: Create the DIRECTORY(ies), if they do not already exist.\nOptions (Linux/macOS):\n  -p, --parents: Make parent directories as needed\n  -v, --verbose: Print a message for each created directory\n  -m, --mode=MODE: Set file mode\nExamples:\n  mkdir new_folder: Create a new directory\n  mkdir -p path/to/new/folder: Create nested directories\n  mkdir -m 755 mydir: Create directory with specific permissions",
            "metadata": {"command": "mkdir", "category": "file_operations", "os": "cross_platform", "source": "man_page"}
        },
        {
            "text": "Command: ping (Cross-platform)\nCategory: Network\nDescription: Send ICMP ECHO_REQUEST to network hosts\nSyntax (Linux/macOS): ping [OPTION] HOST\nSyntax (Windows): ping [-t] [-a] [-n count] [-l size] [-f] [-i TTL] [-v TOS] [-r count] [-s count] [[-j host-list] | [-k host-list]] [-w timeout] [-R] [-S srcaddr] [-4] [-6] target_host\nDetailed Description: Ping uses the ICMP protocol's mandatory ECHO_REQUEST datagram to elicit an ICMP ECHO_RESPONSE from a host or gateway.\nCommon Options (Linux/macOS):\n  -c count: Stop after sending count ECHO_REQUEST packets\n  -i interval: Wait interval seconds between sending each packet\n  -W timeout: Time to wait for a response\nExamples:\n  ping google.com: Ping Google continuously\n  ping -c 4 google.com: Ping Google 4 times",
            "metadata": {"command": "ping", "category": "network", "os": "cross_platform", "source": "man_page"}
        },
        {
            "text": "Command: df (Linux/macOS)\nCategory: System Information\nDescription: Report file system disk space usage\nSyntax: df [OPTION]... [FILE]...\nDetailed Description: Displays the amount of disk space available on the file system containing each file name argument.\nCommon Options:\n  -h, --human-readable: Print sizes in human readable format (e.g., 1K 234M 2G)\n  -i, --inodes: List inode information instead of block usage\n  -T, --print-type: Print file system type\nExamples:\n  df: Show disk usage in blocks\n  df -h: Show disk usage in human readable format\n  df -i: Show inode usage",
            "metadata": {"command": "df", "category": "system_info", "os": "linux_macos", "source": "man_page"}
        },
        {
            "text": "Command: cat (Linux/macOS)\nCategory: Text Processing\nDescription: Concatenate files and print on standard output\nSyntax: cat [OPTION]... [FILE]...\nDetailed Description: Concatenate FILE(s) to standard output. With no FILE, or when FILE is -, read standard input.\nCommon Options:\n  -n, --number: Number all output lines\n  -b, --number-nonblank: Number nonempty output lines\n  -s, --squeeze-blank: Suppress repeated empty output lines\n  -E, --show-ends: Display $ at end of each line\nExamples:\n  cat file.txt: Display file contents\n  cat file1.txt file2.txt > combined.txt: Concatenate files\n  cat -n file.txt: Display file with line numbers",
            "metadata": {"command": "cat", "category": "text_processing", "os": "linux_macos", "source": "man_page"}
        }
    ]
    
    return documents

def ingest_command_docs(vectordb: VectorDB):
    """
    Ingest command documentation into vector database.
    
    Args:
        vectordb: VectorDB instance
    """
    print("Creating sample command documents...")
    documents = create_sample_command_docs()
    
    # Prepare for insertion
    doc_texts = [doc['text'] for doc in documents]
    doc_metadatas = [doc['metadata'] for doc in documents]
    doc_ids = [f"command_{i}" for i in range(len(documents))]
    
    print(f"Ingesting {len(documents)} command documents...")
    try:
        vectordb.add_documents(
            collection_name="os_commands",
            documents=doc_texts,
            metadatas=doc_metadatas,
            ids=doc_ids
        )
        print("Command ingestion complete!")
    except Exception as e:
        print(f"Error during command ingestion: {e}")

if __name__ == "__main__":
    # Initialize vector database
    db = VectorDB()
    
    # Create collection if it doesn't exist
    try:
        db.create_collection("os_commands")
    except Exception:
        print("Collection already exists or error creating collection")
    
    # Ingest commands
    ingest_command_docs(db)