# 🧠 CTeSP Cyber — Sistema POS (Projeto Final)

Projeto desenvolvido em **Python (com JSON e interface PyQt5)** no âmbito do **CTeSP em Cibersegurança — ISTEC Lisboa**.

Este repositório contém todo o código-fonte e recursos necessários para o sistema POS.  
> ⚠️ **IMPORTANTE:** Antes de enviar alterações para o repositório, **faça sempre um backup completo** da pasta do projeto local.

---

## 🚀 Como enviar uma nova versão do projeto (Windows e macOS)

Estas instruções destinam-se a todos os colaboradores que pretendem **atualizar o código existente** neste repositório.

---

### 🧩 0) Fazer Backup (Obrigatório)

Antes de substituir ou atualizar ficheiros:
1. Copie a pasta atual do projeto para outro local seguro.  
2. Só depois continue com os passos seguintes.

> ❗ Isto evita perda de dados caso algo corra mal durante o processo de atualização.

---

### 💻 1) Abrir o Terminal / Git Bash

#### 🪟 No Windows:
Abra o **Git Bash** e navegue até à pasta do projeto:
```bash
cd "C:/Users/SEU_UTILIZADOR/Caminho/para/o/projeto"
```

#### 🍎 No macOS:
Abra o **Terminal** e escreva:
```bash
cd ~/Caminho/para/o/projeto
```

---

### 🧱 2) Verificar se o repositório está inicializado

```bash
git status
```

Se aparecer algo como *“not a git repository”*, inicialize-o:
```bash
git init
```

---

### 🌐 3) Ligar o repositório local ao remoto no GitHub

```bash
git remote add origin https://github.com/lourencoprudencio/CTesPCyber_SistemaPOS_Projeto.git
```

> Se já existir um “origin”, atualize-o com:
> ```bash
> git remote set-url origin https://github.com/lourencoprudencio/CTesPCyber_SistemaPOS_Projeto.git
> ```

---

### 🌳 4) Confirmar a branch correta

Verifica a branch atual:
```bash
git branch
```

Se quiseres usar a branch padrão `main`:
```bash
git branch -M main
```

Se preferires manter `master`:
```bash
git branch -M master
```

---

### 🔄 5) Fazer Pull antes de enviar (para evitar conflitos)

#### Caso o projeto use **main**:
```bash
git pull origin main --allow-unrelated-histories
```

#### Caso o projeto use **master**:
```bash
git pull origin master --allow-unrelated-histories
```

> Isto é necessário se o repositório GitHub já tiver algum ficheiro (ex.: README.md).

---

### 📂 6) Adicionar as alterações locais

```bash
git add .
```

---

### 📝 7) Criar o commit

```bash
git commit -m "Descrição clara da atualização (ex.: adiciona gestão de vendas)"
```

---

### ☁️ 8) Enviar para o GitHub

#### Se estiveres a usar `main`:
```bash
git push -u origin main
```

#### Se estiveres a usar `master`:
```bash
git push -u origin master
```

---

## 🧯 Em caso de conflitos

Se o Git indicar que existem conflitos (ficheiros marcados com `<<<<<<<`, `=======`, `>>>>>>>`):

1. Abre os ficheiros indicados.
2. Resolve manualmente o conflito (escolhe a versão correta).
3. Depois executa:
```bash
git add .
git commit -m "Resolve conflitos de merge"
git push
```

---

## ⚙️ Recomendações Técnicas

### 🔸 Ficheiro `.gitattributes`
Para evitar problemas de formatação entre Windows e macOS, cria um ficheiro chamado `.gitattributes` na raiz do projeto com o seguinte conteúdo:
```
* text=auto
*.py text eol=lf
*.json text eol=lf
*.sh text eol=lf
```

---

### 🔸 Ficheiro `.gitignore`
Cria também um ficheiro `.gitignore` com o seguinte conteúdo:
```
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so
*.egg-info/
.dist/
build/
dist/

# Virtual envs
.venv/
venv/
env/

# IDEs e configurações locais
.vscode/
.idea/

# Sistema Operativo
.DS_Store
Thumbs.db
```

---

## 🧪 Testar o projeto localmente

Antes de enviar qualquer atualização, certifica-te de que o projeto funciona corretamente:
```bash
python --version
python pv_trabalhofinal/main.py
```
---

## Instalação

```bash
pip install -r requirements.txt
```
---

## Execução

```bash
python main.py
```

---

## Testes

```bash
python -m unittest
```

---

## Documentação (pdoc)

```bash
pdoc --html . -o docs
```

---

## 📌 Notas Finais

- **Nunca** faças alterações diretas na branch principal (`main` ou `master`) sem testar primeiro.
- Faz sempre **backup local** antes de substituir ficheiros.
- Evita commits genéricos como “update”; descreve o que realmente mudou.

---

## 👤 Autor / Mantenedor

**Lourenço Prudêncio**  
CTeSP em Cibersegurança — ISTEC Lisboa  
📍 Portugal  
🗓️ Ano Letivo 2025 / 2026  
🔗 [GitHub: lourencoprudencio](https://github.com/lourencoprudencio)
