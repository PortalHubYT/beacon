#!/bin/bash

# Check if the files exist
if [ ! -f "new_pip_freeze.txt" ] || [ ! -f "old_pip_freeze.txt" ]; then
    echo "Both new_pip_freeze.txt and old_pip_freeze.txt must exist."
    exit 1
fi

# Declare associative arrays for new and old pip components
declare -A new_components
declare -A old_components

# Read new_pip_freeze.txt and populate new_components associative array
while IFS="==" read -r package version; do
    new_components["$package"]=$version
done < <(awk -F '==' '{print $1"=="$2}' new_pip_freeze.txt)

# Read old_pip_freeze.txt and populate old_components associative array
while IFS="==" read -r package version; do
    old_components["$package"]=$version
done < <(awk -F '==' '{print $1"=="$2}' old_pip_freeze.txt)

# Find updated components
echo "Updated Components:"
for package in "${!new_components[@]}"; do
    if [ -n "${old_components[$package]}" ]; then
        if [ "${new_components[$package]}" != "${old_components[$package]}" ]; then
            echo "$package: ${new_components[$package]} | ${old_components[$package]}"
        fi
    fi
done
echo "---------------------------"

# Find missing components in the new file
echo "Missing Components:"
for package in "${!old_components[@]}"; do
    if [ -z "${new_components[$package]}" ]; then
        echo "$package:  ${old_components[$package]}"
    fi
done
echo "---------------------------"

# Find new components only in the new file
echo "New Components:"
for package in "${!new_components[@]}"; do
    if [ -z "${old_components[$package]}" ]; then
        echo "$package: ${new_components[$package]}"
    fi
done
