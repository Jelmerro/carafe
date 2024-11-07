#!/usr/bin/env bash
cd "$(dirname "$(realpath "$0")")" || exit
shopt -s expand_aliases
alias fpm="../jfpm/fpm.sh"
source ./release_fpm.sh
