#!/bin/bash

function delete_artifact() {
  local artifact_name=$1
  # Get the artifact ID
  artifact_id=$(gh api repos/${GITHUB_REPOSITORY}/actions/artifacts --paginate \
  | jq -r --arg name "$artifact_name" '.artifacts[] | select(.name == $name) | .id')

  # Check if artifact_id is not empty
  if [[ -n "$artifact_id" ]]; then
    echo "Found artifact IDs: ($artifact_id)"
    # Delete the artifact using the ID
    #echo gh api --method DELETE repos/${GITHUB_REPOSITORY}/actions/artifacts/$artifact_id
    for id in $artifact_id; do
      echo "Deleting artifact: $artifact_name (ID: $id)"
      gh api --method DELETE repos/${GITHUB_REPOSITORY}/actions/artifacts/$id
      echo "Deleted artifact: $artifact_name (ID: $id)"
    done
  else
    echo "Artifact not found: $artifact_name"
  fi
}

function find_old_artifacts() {
  # Query all artifacts and filter those older than 1 hour
  gh api repos/${GITHUB_REPOSITORY}/actions/artifacts --paginate \
  | jq --arg current_time "$current_time" -r '.artifacts[] | select((now - (.created_at | fromdateiso8601)) > 3600) | .name' \
  >old_artifacts.txt

  echo "Artifacts older than 1 hour:"
  cat old_artifacts.txt
}

# Create directories to store downloaded artifacts and final configs
mkdir -p ~/.aws
mkdir -p artifacts

export GITHUB_TOKEN_SAVED=$GITHUB_TOKEN
export GITHUB_TOKEN=${CI_GITHUB_TOKEN:-$(echo $CI_ACCESS_TOKEN | cut -d : -f 2 2>/dev/null)}

# Get the current time in ISO 8601 format
current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

find_old_artifacts

echo "Deleting old artifacts..."
while read -r artifact_name; do
  # Artifacts exempt from deletion: github-pages - use a egrep regex pattern
  if echo "$artifact_name" | egrep -e '(github-pages)'; then
    echo "Skipping deletion of artifact: $artifact_name"
  else
    echo "Processing artifact: $artifact_name"

    delete_artifact "$artifact_name"
  fi
done < old_artifacts.txt

#set | egrep -e '^(GITHUB)'
#set -x
# Retrieve all artifacts that match the pattern "aws-config-*"
gh api repos/${GITHUB_REPOSITORY}/actions/artifacts --paginate \
  | jq -r ".artifacts[] | select(.name | startswith(\"aws-config-\")) | select(.name | endswith(\"-${GITHUB_RUN_ID}\")) | .name" \
  >artifacts.txt
echo "Artifacts to be processed:"
cat artifacts.txt
if [ -z "$(cat artifacts.txt | sed 's/ //g')" ] ; then
  echo "No artifacts found."
  exit 5
else
  echo "Processing the artifacts:"
  matrix_profile_count=$(echo $MATRIX_PROFILES | wc -w)
  matrix_profile_count=$((0 + matrix_profile_count))
  cat artifacts.txt | while read -r artifact_name; do
      echo "  artifact: $artifact_name"

      # Download the artifact
      [ -d "artifacts/$artifact_name" ] || {
        echo "Creating directory: artifacts/$artifact_name";
        mkdir -p "artifacts/$artifact_name";
        gh run download --name "$artifact_name" --dir "artifacts/$artifact_name";
      }
      ls -alR artifacts/
      profile_count=$(cat ~/.aws/config | egrep -e '\[profile .*\]' | wc -l)
      profile_count=$((0 + profile_count))

      echo "Profile count ($profile_count). Matrix profile count ($matrix_profile_count). Using artifact: $artifact_name"

      # Append credentials and config to ~/.aws IF NOT already present
      aws configure list-profiles
      matches=""
      for profile in $(aws configure list-profiles); do
        if echo "$artifact_name" | grep -q "$profile"; then
          if [ -z "$matches" ]; then
            matches="$profile"
          else
            matches="$profile|$matches"
          fi
        fi
      done
      if [ -z "$matches" ]; then
        cat "artifacts/$artifact_name/credentials" >> ~/.aws/credentials || echo "No credentials in $artifact_name"
        cat "artifacts/$artifact_name/config" >> ~/.aws/config || echo "No config in $artifact_name"
      else
        echo "Matches: $matches"
        aws configure list-profiles | egrep -v -e "($matches)" 2>/dev/null
        if [ -z "$(aws configure list-profiles | egrep -v -e "($matches)" 2>/dev/null)" ] ; then
          cat "artifacts/$artifact_name/credentials" > ~/.aws/credentials || echo "No credentials in $artifact_name"
          cat "artifacts/$artifact_name/config" > ~/.aws/config || echo "No config in $artifact_name"
        else
          echo "Skipping credentials and config from $artifact_name"
        fi
      fi

      rm -fr "artifacts/$artifact_name"
      delete_artifact "$artifact_name"
    done
fi
export GITHUB_TOKEN=$GITHUB_TOKEN_SAVED
# Display the final credentials and config for debugging
[ -f ~/.aws/config ] && {
  echo "Final ~/.aws/config:";
  cat ~/.aws/config;
} || echo "No config found"
[ -f ~/.aws/credentials ] && {
  echo "Final ~/.aws/credentials:";
  cat ~/.aws/credentials;
} || echo "No credentials found"
