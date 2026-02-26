# Пошаговый запуск нового публичного репозитория

## 1. Подготовка локально
1. Установить pre-commit:
```powershell
.\venv\Scripts\python.exe -m pip install pre-commit detect-secrets
.\venv\Scripts\pre-commit.exe install
```
2. Сгенерировать baseline секретов:
```powershell
.\venv\Scripts\python.exe -c "import subprocess, pathlib; files=subprocess.check_output(['git','ls-files'], text=True).splitlines(); files=[f for f in files if not f.endswith('.ipynb') and not f.startswith('.idea/')]; out=subprocess.check_output(['.\\venv\\Scripts\\detect-secrets.exe','scan',*files]); pathlib.Path('.secrets.baseline').write_bytes(out)"
.\venv\Scripts\pre-commit.exe run --all-files
```

## 2. Создать чистую копию без старой истории
Вариант с новым git-репозиторием в отдельной папке:
```powershell
cd ..
New-Item -ItemType Directory TABLE_PARSE_PUBLIC
robocopy TABLE_PARSE TABLE_PARSE_PUBLIC /E /XD .git venv .idea __pycache__ .ipynb_checkpoints
cd TABLE_PARSE_PUBLIC
git init
git add .
git commit -m "Initial clean public release"
```

## 3. Подключить новый GitHub-репозиторий
```powershell
git remote add origin https://github.com/<your_user>/<new_repo>.git
git branch -M main
git push -u origin main
```

## 4. Включить protection в GitHub
- Branch protection для `main`.
- Required status checks (pre-commit/CI).
- Secret scanning и Dependabot alerts.

## 5. Публикационный чеклист
- В репозитории нет `.env`, `key/*.json`, hardcoded tokens.
- Ноутбуки очищены от output с чувствительными данными.
- Есть `README.md`, `doc/`, `.env.example`, `LICENSE`.
