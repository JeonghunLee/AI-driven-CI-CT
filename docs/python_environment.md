# Python Environment

## Components

<br/>

| Item | Value |
|---|---|
| System Python | OS installation |
| Project Python | `.venv` |
| Dependencies | `requirements.txt` |
| Environment setup | `test_envs.tools.environment_setup python` |
| OS config | `test_envs/configs/config.json → os` |
| Environment check | `test_envs/configs/check.json → python` |

<br/>

## Setup order

<br/>

| Order | Action | Python |
|---:|---|---|
| 1 | Select Operating System | System Python |
| 2 | Create `.venv` | System Python |
| 3 | Install dependencies | `.venv` Python |

<br/>

```text
System Python
      ↓
Select OS
      ↓
python -m venv .venv
      ↓
.venv Python
      ↓
pip install -r requirements.txt
```

<br/>

## OS

<br/>

| Config value | Runtime |
|---|---|
| `auto` | Host OS detection |
| `windows` | Windows |
| `linux` | Linux |
| `macos` | macOS |

<br/>

| OS | Virtual environment Python |
|---|---|
| Windows | `.venv/Scripts/python.exe` |
| Linux | `.venv/bin/python` |
| macOS | `.venv/bin/python` |

<br/>

## VS Code

<br/>

| Item | Value |
|---|---|
| Launch | `SETUP 1: Select Operating System` |
| Launch | `SETUP 2: Install Python Virtual Environment` |
| Task | `SETUP 1: Select Operating System` |
| Task | `SETUP 2: Install Python Virtual Environment` |
| Setup 1 interpreter | `python` |
| Setup 2 interpreter | `python` |


<br/>

## Commands

<br/>

```powershell
python -m test_envs.tools.configuration select-os
python -m test_envs.tools.environment_setup python
```

<br/>

## Check file

<br/>

```text
python
├── installed
├── executable
└── version
```

<br/>

## Constraints

<br/>

| Rule | Value |
|---|---|
| OS selection inside `.venv` | Prohibited |
| Setup 1 `.venv` dependency | Prohibited |
| Setup 2 `.venv` dependency | Prohibited |
| Runtime dependency | Project `.venv` |

<br/>