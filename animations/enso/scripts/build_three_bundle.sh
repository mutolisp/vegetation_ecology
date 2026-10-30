#!/usr/bin/env bash
# 重建 index.html <head> 內嵌的 three.js 0.160.0 + OrbitControls（MIT License）
# Rebuild the inlined three.js bundle. Output: three-bundle.js（貼回 index.html 的第一個 <script> 區塊）
set -euo pipefail
work="$(mktemp -d)"
cd "$work"
npm init -y >/dev/null
npm i --silent three@0.160.0 esbuild@0.24
cat > entry.js <<'EOF'
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
window.THREE = THREE;
window.THREE_ADDONS = { OrbitControls };
EOF
npx esbuild entry.js --bundle --minify --format=iife --legal-comments=inline --outfile=three-bundle.js
echo "$work/three-bundle.js"
