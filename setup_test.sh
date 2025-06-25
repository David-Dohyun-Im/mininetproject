#!/bin/bash

# Setup script for Mininet file transfer testing
# Creates test files and provides testing utilities

set -e  # Exit on any error

echo "=== Mininet File Transfer Test Setup ==="

# Create test content
create_test_file() {
    local file_path="$1"
    echo "Creating test file: $file_path"
    
    # Create sample content for testing
    cat > "$file_path" << 'EOF'
This is a test file for Mininet file transfer testing.

Contents:
- Line 1: Hello from h1!
- Line 2: Testing TCP file transfer
- Line 3: Via dual-path network topology
- Line 4: h1 -> s1 -> (s2 or s3) -> s4 -> h2

Network topology:
h1 (10.0.0.1) -- s1 -- s2 -- s4 -- h2 (10.0.0.2)
                 |           |
                 s3 ---------

Test data: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
Binary test: $(echo -e '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F')

End of test file.
EOF
    
    echo "Test file created successfully ($(wc -c < "$file_path") bytes)"
}

# Set file permissions
set_permissions() {
    local file_path="$1"
    chmod 644 "$file_path"
    echo "File permissions set to 644 for: $file_path"
}

# Verify file transfer by comparing files
verify_transfer() {
    local original="$1"
    local received="$2"
    
    echo ""
    echo "=== File Transfer Verification ==="
    
    if [ ! -f "$original" ]; then
        echo "ERROR: Original file not found: $original"
        return 1
    fi
    
    if [ ! -f "$received" ]; then
        echo "ERROR: Received file not found: $received"
        return 1
    fi
    
    local orig_size=$(wc -c < "$original")
    local recv_size=$(wc -c < "$received")
    
    echo "Original file size: $orig_size bytes"
    echo "Received file size: $recv_size bytes"
    
    if [ "$orig_size" -eq "$recv_size" ]; then
        echo "✓ File sizes match"
    else
        echo "✗ File sizes differ!"
        return 1
    fi
    
    # Compare file contents
    if cmp -s "$original" "$received"; then
        echo "✓ File contents match perfectly"
        echo "SUCCESS: File transfer completed successfully!"
        return 0
    else
        echo "✗ File contents differ!"
        echo "Showing differences:"
        diff "$original" "$received" || true
        return 1
    fi
}

# Clean up test files
cleanup() {
    echo ""
    echo "=== Cleanup ==="
    local files_to_clean=("/tmp/send_file.txt" "/tmp/send_file.txt.1" "/tmp/send_file.txt.2" "/tmp/received_file.txt")
    
    for file in "${files_to_clean[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo "Removed: $file"
        fi
    done
    echo "Cleanup completed"
}

# Display file contents
show_file() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        echo ""
        echo "=== Contents of $file_path ==="
        cat "$file_path"
        echo ""
        echo "=== End of file ==="
    else
        echo "File not found: $file_path"
    fi
}

# Main execution
case "${1:-setup}" in
    "setup")
        echo "Setting up test environment..."
        create_test_file "/tmp/send_file.txt"
        set_permissions "/tmp/send_file.txt"
        echo ""
        echo "Setup completed!"
        echo ""
        echo "Available commands:"
        echo "  ./setup_test.sh setup     - Create test files (default)"
        echo "  ./setup_test.sh verify    - Verify file transfer"
        echo "  ./setup_test.sh show      - Show test file contents"
        echo "  ./setup_test.sh cleanup   - Clean up test files"
        echo ""
        echo "To test:"
        echo "1. Run: sudo python main.py"
        echo "2. In Mininet CLI: h2 python server.py &"
        echo "3. In Mininet CLI: h1 python client.py"
        echo "4. Exit Mininet and run: ./setup_test.sh verify"
        ;;
    "verify")
        verify_transfer "/tmp/send_file.txt" "/tmp/send_file.txt.1"
        ;;
    "show")
        show_file "/tmp/send_file.txt"
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {setup|verify|show|cleanup}"
        echo "  setup   - Create test files and setup environment"
        echo "  verify  - Verify file transfer success"
        echo "  show    - Display test file contents"
        echo "  cleanup - Remove all test files"
        exit 1
        ;;
esac