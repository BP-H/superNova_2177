# superNova_2177/ ⚡️🌌🎶🚀🌸🔬
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/BP-H/community_guidelines/blob/main/LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red.svg)](https://opensource.org/)
[![Contributors Welcome](https://img.shields.io/badge/Contributors-Welcome-brightgreen.svg)](https://github.com/BP-H/community_guidelines/issues)
[![Stars](https://img.shields.io/github/stars/BP-H/community_guidelines?style=social)](https://github.com/BP-H/superNova_2177)

**A scientifically grounded social metaverse engine for collaborative creativity**

This repository hosts `superNova_2177.py` — an experimental protocol merging computational sociology, quantum-aware simulation logic, and creative systems engineering. It models symbolic influence, interaction entropy, and network resonance across users and content, with classical compatibility and quantum-readiness.

⚠️ This is *not* a financial product, cryptocurrency, or tradable asset. All metrics (e.g., Harmony Score, Resonance, Entropy) are symbolic — for modeling, visualization, and creative gameplay only. See legal/disclaimer sections in `superNova_2177.py`, lines 60–88.

````markdown
# superNova_2177 🧠

**AI-Powered Scientific Validation with Built-In Integrity Scoring**

A modular intelligence pipeline that evaluates hypotheses through evidence-based validation, peer review scoring, and manipulation resistance.

## 🚀 Quick Start

```bash
# create the virtual environment and install dependencies
python setup_env.py

# optional: launch the API immediately
# python setup_env.py --run-app

# optional: build the NiceGUI frontend
# python setup_env.py --build-ui

# Try demo mode
supernova-validate --demo

# Run your own validation set
supernova-validate --validations sample_validations.json
````
## 📦 Installation

### Step-by-Step

1. **Install Python 3.12** from [python.org](https://www.python.org/) if it isn't
   already on your machine. You can check by running `python --version` in your
   terminal.
2. **Run the setup script** to create the virtual environment and install all
   dependencies locally. You can also pass `--run-app` or `--build-ui` to
   automatically start the API or compile the frontend:
   ```bash
   python setup_env.py
   # python setup_env.py --run-app    # launch API after install
   # python setup_env.py --build-ui   # build NiceGUI frontend assets
   ```
  Or install the published wheel directly from PyPI:
  ```bash
  # Linux/macOS
  ./online_install.sh
  # Windows
  ./online_install.ps1
  ```
3. **Activate the environment**:
   ```bash
   # Linux/macOS
   source venv/bin/activate
   # Windows
   .\venv\Scripts\activate
   ```
4. You're ready to run the demo commands shown in [Quick Start](#-quick-start).

This project relies on features introduced in **SQLAlchemy 2.x** such as
`DeclarativeBase`. Ensure you have `sqlalchemy>=2.0` installed. The code also
requires `python-dateutil` for timestamp parsing.

## 🏁 Getting Started

Set up a Python environment and install the package and its dependencies:

```bash
pip install .
# install optional libraries used by the tests
pip install -r requirements.txt
```

Run the full test suite to verify your setup:

```bash
pytest
```

## 🔧 Configuration

`SECRET_KEY` can be supplied via environment variables for JWT signing. If it is
not set, a secure random value will be generated automatically:

```bash
# optional
export SECRET_KEY="your-random-secret"
```

Copy `.env.example` to `.env` and set values for `SECRET_KEY`, `DATABASE_URL`,
and `BACKEND_URL` before running the app. Set `DB_MODE=central` if you want to
use a shared PostgreSQL instance instead of the default local SQLite file.

## 🐳 Docker

You can build a standalone Docker image or run the API with Postgres and Redis
via `docker-compose`.

Build the image:
```bash
docker build -t supernova-2177 .
```

Or bring up the full stack:
```bash
cp .env.example .env  # set your own secrets
docker-compose up
```

The application will be available at [http://localhost:8000](http://localhost:8000).

## 🌩️ Streamlit Cloud

Deploy the demo UI online with Streamlit Cloud:

1. Fork this repository on GitHub.
2. Sign in to [Streamlit Cloud](https://streamlit.io/cloud) and select **New app**.
3. Choose the repo and set `app.py` as the entry point.
4. Add your `SECRET_KEY` and `DATABASE_URL` under **Secrets** in the app settings.
5. Streamlit will install dependencies from `requirements.txt` and launch the app.

After the build completes, you'll get a shareable URL to interact with the validation demo in your browser.

## 🧪 Running Tests

Install all dependencies first:

```bash
pip install -r requirements.txt
pytest
```

The test suite requires packages like `SQLAlchemy`, `networkx`, and `numpy`.
If `pytest` fails with missing module errors, run `pip install -r requirements.txt` again.

### Makefile Commands

For a quicker workflow you can use the provided `Makefile`:

```bash
# install project dependencies
make install

# run the full test suite
make test

# run static type checks
make lint
```

## 📦 Building an Executable

You can package the command line interface into a standalone binary using
PyInstaller. Run the helper script:

```bash
scripts/build_executable.sh
```

On Windows, use the PowerShell version:

```powershell
scripts/build_executable.ps1
```

The generated executable will be placed under `dist/` as `supernova-cli` on
Unix systems or `supernova-cli.exe` on Windows.

### Running the Installer

If you're on Windows, download `supernova-cli.exe` from the [GitHub Releases page](https://github.com/BP-H/superNova_2177/releases/latest)
or build it yourself with the script above. Before launching, set the required
environment variables so the application can connect to its services. `SECRET_KEY`
is optional because a secure one will be generated if omitted:

```bash
# optional
export SECRET_KEY="your-secret"
export DATABASE_URL="postgresql+asyncpg://user:password@localhost/transcendental_resonance"
export BACKEND_URL="http://localhost:8000"
```

To connect to a central database instead of the local file, pass
`--db-mode central` when launching the application or set `DB_MODE=central`.

After setting the variables, execute the binary directly:

```bash
./supernova-cli --demo   # on Windows use supernova-cli.exe
```

### One-Click Installers

Prebuilt installers for each platform are published under the [Releases page](https://github.com/BP-H/superNova_2177/releases).
Each installer bundles Python 3.12 and all dependencies so it works offline:

* **Windows** – run `SuperNova_2177.msi` to install the CLI.
* **macOS** – open `supernova-cli.dmg` and drag the app to `Applications`.
* **Linux** – make the AppImage executable with `chmod +x` and run it directly.

If you prefer to build everything locally, execute `python one_click_install.py`.
It detects your OS, downloads Python 3.12 if necessary, bundles the
dependencies into `offline_deps/`, creates a virtual environment, and installs
the package.

## ✨ Features

* **🧠 Smart Scoring** — Combines confidence, signal strength, and NLP sentiment
* **🛡️ Manipulation Detection** — Flags collusion, bias, and temporal anomalies
* **📊 Multi-Factor Analysis** — Diversity, reputation, coordination, timing
* **📋 Actionable Reports** — Output includes flags, scores, certification level
* **🧵 Fully Modular** — Each analysis step is plug-and-play

## 📈 Example Output

```
🔬 VALIDATION REPORT — superNova_2177
=============================================

✅ CERTIFICATION: PROVISIONAL
📊 Consensus Score: 0.782
👥 Validators: 5

🛡️ INTEGRITY
Risk Level: MEDIUM
Integrity Score: 0.683
Flags: ['limited_consensus', 'low_diversity']

💡 Recommendation:
- Add more validators from diverse affiliations
- Check timestamp clustering for coordination risks
```

## 📓 Jupyter Examples

Two notebooks in `docs/` showcase how to run the validation pipeline and plot
coordination graphs using the sample data in `sample_validations.json`.

Launch them from the repository root:

```bash
jupyter notebook docs/Validation_Pipeline.ipynb
jupyter notebook docs/Network_Graph_Visualization.ipynb
```

## 🏗️ Architecture (v4.6)

* `validation_integrity_pipeline.py` — Orchestrator for full validation logic
* `reputation_influence_tracker.py` — Tracks and scores validators over time
* `diversity_analyzer.py` — Detects echo chambers and affiliation bias
* `temporal_consistency_checker.py` — Tracks time-based volatility
* `network_coordination_detector.py` — Spots suspicious group behavior using
  sentence‑embedding similarity

## 🧪 Status

**v4.6 — Stable & Ready**

* Robust CLI
* Structured error handling
* Transparent results
* Designed for peer-reviewable output

---

*Built for scientific integrity in a world of noise.*


## 📝 Contributing RFCs

We welcome design proposals through our RFC process. Create a numbered folder under `rfcs/` with a `README.md` describing your idea and update `rfcs/README.md` to add its title. Open a pull request so the community can review.

