
name: submit url to pdf

on:
  # push:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  shot-scraper:
    runs-on: ubuntu-latest
    if: ${{ github.repository != 'simonw/shot-scraper-template' }}
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.10
      uses: actions/setup-python@v3
      with:
        python-version: "3.10"
    - uses: actions/cache@v3
      name: Configure pip caching
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    - name: Cache Playwright browsers
      uses: actions/cache@v3
      with:
        path: ~/.cache/ms-playwright/
        key: ${{ runner.os }}-browsers
    - name: Install extra fonts
      run: |
        sudo apt-get install rar  fonts-arphic-ukai fonts-arphic-uming fonts-ipafont-mincho fonts-ipafont-gothic fonts-unfonts-core
        sudo apt-get install zip gzip tar
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Install Playwright dependencies
      run: |
        shot-scraper install 
        playwright install
    - uses: actions/github-script@v6
      name: Create shots.yml if missing on first run
      with:
        script: |
          const fs = require('fs');
          if (!fs.existsSync('shots.yml')) {
              const desc = context.payload.repository.description;
              let line = '';
              if (desc && (desc.startsWith('http://') || desc.startsWith('https://'))) {
                  line = `- url: ${desc}` + '\n  output: shot.png\n  height: 800';
              } else {
                  line = '# - url: https://www.example.com/\n#   output: shot.png\n#   height: 800';
              }
              fs.writeFileSync('shots.yml', line + '\n');
          }
    - name: Take shots
      run: |
        python indie-2pdf.py
    - name: Commit and push
      run: |-
        git config user.name "Automated"
        git config user.email "actions@users.noreply.github.com"
        git add -A
        timestamp=$(date -u)
        git commit -m "${timestamp}" || exit 0
        git pull --rebase
        git push
    - name: Release
      uses: marvinpinto/action-automatic-releases@latest
      with:
        repo_token: "${{ secrets.GITHUB_TOKEN }}"
        automatic_release_tag: ${{ github.run_id }}
        prerelease: false
        title: ${{ github.run_id }}
        files: |
          data/*.rar
      
