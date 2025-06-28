# MedOCR [Minor Project I]

## Usage:

### 1. Clone the repo:

```sh
git clone https://github.com/XIAOR1Ck/MedOCR.git
```

### 2. Create a python Virtual Enviornment:

After cloning the repo go to the repo folder and make a python virtual envoirnment to containerize the project dependencies.
**Linux/Mac:**

```sh
cd MedOCR
python -m venv .venv
```

**Windows:**

```sh
# in cmd
chdir MedOCR
python -m venv .venv
```

Note: powershell users can follow any of the above.

### 3. Activating the Virtual Enviornment

**Linux/Mac:**

```sh
source .venv/bin/activate
```

You can also find shell specific activation scripts for zsh, fish etc

**Windows**

```sh
# in cmd
.venv\Scriprts\activate.bat
# in powershell
.venv\Scripts\activate.ps1
```

### 4. Installing Requirements

After activating the virtual enviornment, you can install the dependencies by the following command:

```sh
pip install requirements.txt
```

### 5. Running The Project

```sh
flask --app app --debug run
```
