#!/usr/bin/env bash
cd "$(dirname "$(realpath "$0")")" || exit
rm -rf dist/
mkdir -p dist/
name=$(grep "^name=" pyproject.toml | sed 's/.*=//g' | tr -d '"')
version=$(grep "^version=" pyproject.toml | sed 's/.*=//g' | tr -d '"')
description=$(grep "^description=" pyproject.toml | sed 's/.*=//g' | tr -d '"')
url=$(grep "^Repository=" pyproject.toml | sed 's/.*=//g' | tr -d '"')
author=$(grep "^authors=" pyproject.toml | sed 's/.*=//g' | sed 's/}]$//g' | tr -d '"')
license=$(grep "^license=" pyproject.toml | sed 's/.*=//g' | sed 's/}$//g' | tr -d '"')
for rel in "rpm" "deb" "pacman";do
    fpm -s dir -t $rel \
        --package "dist/$name-$version.any.$rel" \
        --name "$name" --license "$license" --version "$version" --url "$url" \
        --architecture all --depends python3 --description "$description" \
        --maintainer "$author" "$name.py=/usr/bin/$name"
done
