#!/usr/bin/env bash

# Default values
PROFILE="cloud-services-prod"
DOMAIN="artifacts"
REPOSITORY="manifests"
FORMAT="pypi"
PACKAGES=()
VERSIONS=()
VERBOSE=0

__version__="0.26.74"

# Help message
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Delete package versions from AWS CodeArtifact repository.

Options:
    --profile PROFILE      AWS profile (default: cloud-services-prod)
    --domain DOMAIN        CodeArtifact domain (default: artifacts)
    --repository REPO      CodeArtifact repository (default: manifests)
    --format FORMAT        Package format (default: pypi)
    --package PKG         Package name (can be specified multiple times)
    --version VER         Version to delete (can be specified multiple times)
    -v, --verbose         Increase verbosity
    -h, --help            Show this help message and exit

Examples:
    # Delete specific version from all packages
    $(basename "$0") --version 0.7.5

    # Delete multiple versions from specific packages
    $(basename "$0") --package lobby --package assets --version 0.7.5 --version 0.7.6

    # Use different AWS profile
    $(basename "$0") --profile my-profile --package lobby --version 0.7.5
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --repository)
            REPOSITORY="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --package)
            PACKAGES+=("$2")
            shift 2
            ;;
        --version)
            VERSIONS+=("$2")
            shift 2
            ;;
        -v|--verbose)
            ((VERBOSE++))
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

# Validate inputs
if [ ${#PACKAGES[@]} -eq 0 ]; then
    # If no packages specified, get all packages from repository
    if [ $VERBOSE -gt 0 ]; then
        echo "No packages specified, listing all packages in repository..."
    fi

    PACKAGES_JSON=$(aws codeartifact list-packages \
        --profile "$PROFILE" \
        --domain "$DOMAIN" \
        --repository "$REPOSITORY" \
        --query 'packages[].package' \
        --output json)

    # Convert JSON array to bash array using a more compatible approach
    PACKAGES=()
    while IFS= read -r pkg; do
        PACKAGES+=("$pkg")
    done < <(echo "$PACKAGES_JSON" | jq -r '.[]')

    if [ $VERBOSE -gt 0 ]; then
        echo "Found packages: ${PACKAGES[*]}"
    fi
fi

if [ ${#VERSIONS[@]} -eq 0 ]; then
    echo "No versions specified to delete" >&2
    usage
    exit 1
fi

# Process each package
for pkg in "${PACKAGES[@]}"; do
    if [ $VERBOSE -gt 0 ]; then
        echo "Processing package: $pkg"
        echo "Listing current versions..."
    fi

    # List current versions
    aws codeartifact list-package-versions \
        --profile "$PROFILE" \
        --domain "$DOMAIN" \
        --repository "$REPOSITORY" \
        --package "$pkg" \
        --format "$FORMAT"

    # Delete specified versions
    for ver in "${VERSIONS[@]}"; do
        if [ $VERBOSE -gt 0 ]; then
            echo "Deleting version $ver of package $pkg..."
        fi

        aws codeartifact delete-package-versions \
            --profile "$PROFILE" \
            --domain "$DOMAIN" \
            --repository "$REPOSITORY" \
            --package "$pkg" \
            --format "$FORMAT" \
            --versions "$ver"
    done
done
