#!/bin/bash

# --- Couleurs pour le terminal ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # Pas de couleur

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}   BIENVENUE DANS L'INSTALLATEUR MEDSAFE  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 1. Vérification de Python
if ! command -v python3 &> /dev/null
then
    echo "Erreur : Python3 n'est pas installé. Veuillez l'installer avant de continuer."
    exit
fi

# 2. Création de l'environnement virtuel (recommandé)
echo -e "\n${BLUE}[1/4] Création de l'environnement virtuel...${NC}"
python3 -m venv venv
source venv/bin/activate

# 3. Installation des dépendances
echo -e "${BLUE}[2/4] Installation des bibliothèques (CustomTkinter, Pillow)...${NC}"
pip install --upgrade pip
pip install customtkinter Pillow 

# 4. Vérification du logo
if [ ! -f "mokkt.jpg" ]; then
    echo -e "${BLUE}[Avertissement] Le fichier mokkt.jpg est absent du dossier.${NC}"
fi 

# 5. Initialisation de la base de données (si setup_db.py existe)
if [ -f "setup_db.py" ]; then
    echo -e "${BLUE}[3/4] Initialisation de la base de données SQLite...${NC}"
    python3 setup_db.py
fi

# 6. Lancement de l'application
echo -e "${GREEN}[4/4] Lancement de MedSafe en cours...${NC}"
echo -e "${BLUE}=========================================${NC}"
python3 main.py [cite: 1762]
