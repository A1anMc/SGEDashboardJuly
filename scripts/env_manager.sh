#!/bin/zsh

# Function to read all environment variables
read_env() {
    echo "Current Environment Variables:"
    echo "-----------------------------"
    while IFS= read -r line; do
        # Skip empty lines and comments
        if [[ ! -z "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
            echo "$line"
        fi
    done < .env
}

# Function to update an environment variable
update_env() {
    if [ "$#" -ne 2 ]; then
        echo "Usage: update_env KEY VALUE"
        return 1
    fi
    
    local key=$1
    local value=$2
    local updated=0
    
    # Create temporary file
    temp_file=$(mktemp)
    
    while IFS= read -r line || [ -n "$line" ]; do
        if [[ "$line" =~ ^[[:space:]]*"$key"= ]]; then
            echo "$key=$value" >> "$temp_file"
            updated=1
        else
            echo "$line" >> "$temp_file"
        fi
    done < .env
    
    # If key wasn't found, append it
    if [ $updated -eq 0 ]; then
        echo "$key=$value" >> "$temp_file"
    fi
    
    # Replace original file
    mv "$temp_file" .env
    echo "Updated $key successfully"
}

# Function to delete an environment variable
delete_env() {
    if [ "$#" -ne 1 ]; then
        echo "Usage: delete_env KEY"
        return 1
    fi
    
    local key=$1
    temp_file=$(mktemp)
    
    while IFS= read -r line || [ -n "$line" ]; do
        if [[ ! "$line" =~ ^[[:space:]]*"$key"= ]]; then
            echo "$line" >> "$temp_file"
        fi
    done < .env
    
    mv "$temp_file" .env
    echo "Deleted $key successfully"
}

# Function to add a new environment variable
add_env() {
    if [ "$#" -ne 2 ]; then
        echo "Usage: add_env KEY VALUE"
        return 1
    fi
    
    local key=$1
    local value=$2
    
    # Check if key already exists
    if grep -q "^$key=" .env; then
        echo "Key already exists. Use update_env to modify it."
        return 1
    fi
    
    echo "$key=$value" >> .env
    echo "Added $key successfully"
}

# Function to get a specific environment variable
get_env() {
    if [ "$#" -ne 1 ]; then
        echo "Usage: get_env KEY"
        return 1
    fi
    
    local key=$1
    local value=$(grep "^$key=" .env | cut -d'=' -f2-)
    
    if [ -z "$value" ]; then
        echo "Key not found: $key"
        return 1
    fi
    
    echo "$value"
}

echo "Environment management functions loaded!"
echo "Available commands:"
echo "  read_env              - Display all environment variables"
echo "  get_env KEY          - Get value of specific environment variable"
echo "  add_env KEY VALUE    - Add new environment variable"
echo "  update_env KEY VALUE - Update existing environment variable"
echo "  delete_env KEY       - Delete environment variable" 