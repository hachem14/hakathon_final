import customtkinter as ctk
from PIL import Image
import sqlite3
from tkinter import messagebox, filedialog
import os
import sys
import threading
import zipfile
from itertools import combinations

# =========================================================
# MEDSAFE AI — Configuration du modèle DistilBERT
# =========================================================
AI_ZIP_PATH  = "medsafe_model.zip"
AI_MODEL_DIR = "medsafe_model"

LABEL_MAP = {0: "MILD",    1: "CAUTION", 2: "DANGER"}
EMOJI_MAP = {0: "🟢",      1: "🟡",      2: "🔴"}
COLOR_MAP = {0: "#2C9970", 1: "#E67E22", 2: "#C0392B"}

# =========================================================
# BASE DE MÉDICAMENTS — Autocomplete (200+ entrées)
# =========================================================
MEDICAMENTS = sorted([
    # Antalgiques / Anti-inflammatoires
    "Paracetamol", "Ibuprofene", "Aspirine", "Diclofenac", "Naproxene",
    "Ketoprofene", "Celecoxib", "Meloxicam", "Piroxicam", "Indometacine",
    "Tramadol", "Codeine", "Morphine", "Oxycodone", "Fentanyl",
    "Buprenorphine", "Nalbuphine", "Nefopam", "Acide Mefenamique",
    # Antibiotiques
    "Amoxicilline", "Amoxicilline-Clavulanate", "Ampicilline", "Cephalexine",
    "Cefuroxime", "Ceftriaxone", "Cefixime", "Cefazoline", "Imipenem",
    "Meropenem", "Azithromycine", "Clarithromycine", "Erythromycine",
    "Doxycycline", "Tetracycline", "Ciprofloxacine", "Levofloxacine",
    "Ofloxacine", "Norfloxacine", "Metronidazole", "Tinidazole",
    "Clindamycine", "Vancomycine", "Linezolide", "Rifampicine",
    "Isoniazide", "Ethambutol", "Pyrazinamide", "Sulfamethoxazole",
    "Trimethoprime", "Nitrofurantoine", "Fosfomycine",
    # Antihypertenseurs
    "Amlodipine", "Nifedipine", "Verapamil", "Diltiazem", "Felodipine",
    "Lisinopril", "Enalapril", "Captopril", "Ramipril", "Perindopril",
    "Trandolapril", "Losartan", "Valsartan", "Candesartan", "Irbesartan",
    "Olmesartan", "Telmisartan", "Atenolol", "Metoprolol", "Bisoprolol",
    "Carvedilol", "Nebivolol", "Propranolol", "Labetalol",
    "Hydrochlorothiazide", "Furosemide", "Spironolactone", "Indapamide",
    "Torasemide", "Amiloride", "Methyldopa", "Clonidine", "Doxazosine",
    # Antidiabétiques
    "Metformine", "Glibenclamide", "Gliclazide", "Glimepiride", "Glipizide",
    "Sitagliptine", "Vildagliptine", "Saxagliptine", "Linagliptine",
    "Empagliflozine", "Dapagliflozine", "Canagliflozine", "Liraglutide",
    "Exenatide", "Insuline Rapide", "Insuline NPH", "Insuline Glargine",
    "Insuline Detemir", "Insuline Aspart", "Insuline Lispro",
    # Anticoagulants / Antiagrégants
    "Warfarine", "Acenocoumarol", "Heparine", "Enoxaparine", "Dalteparine",
    "Rivaroxaban", "Apixaban", "Dabigatran", "Edoxaban",
    "Aspirine", "Clopidogrel", "Ticagrelor", "Prasugrel", "Dipyridamole",
    # Cardio / Statines
    "Atorvastatine", "Rosuvastatine", "Simvastatine", "Pravastatine",
    "Fluvastatine", "Ezetimibe", "Fenofibrate", "Bezafibrate",
    "Digoxine", "Amiodarone", "Flecainide", "Sotalol", "Propafenone",
    "Nitroglycerin", "Isosorbide Dinitrate", "Isosorbide Mononitrate",
    "Ivabradine", "Sacubitril", "Ranolazine",
    # Gastro-entérologie
    "Omeprazole", "Pantoprazole", "Esomeprazole", "Lansoprazole",
    "Rabeprazole", "Ranitidine", "Famotidine", "Cimetidine",
    "Domperidone", "Metoclopramide", "Ondansetron", "Granisetron",
    "Loperamide", "Mesalazine", "Sulfasalazine", "Lactulose",
    "Bisacodyl", "Senna", "Macrogol", "Charbon Actif",
    # Antiasthmatiques / Respiratoire
    "Salbutamol", "Terbutaline", "Salmeterol", "Formoterol",
    "Budesonide", "Fluticasone", "Beclometasone", "Ciclesonide",
    "Ipratropium", "Tiotropium", "Acide Acetylsalicylique",
    "Montelukast", "Zafirlukast", "Theophylline", "Aminophylline",
    "Acetylcysteine", "Ambroxol", "Bromhexine", "Carbocisteine",
    # Neurologie / Psychiatrie
    "Carbamazepine", "Valproate", "Phenobarbital", "Phenytoine",
    "Lamotrigine", "Levetiracetam", "Topiramate", "Gabapentine",
    "Pregabaline", "Clonazepam", "Diazepam", "Lorazepam", "Oxazepam",
    "Alprazolam", "Zolpidem", "Zopiclone", "Melatonine",
    "Fluoxetine", "Sertraline", "Paroxetine", "Escitalopram",
    "Citalopram", "Venlafaxine", "Duloxetine", "Mirtazapine",
    "Amitriptyline", "Clomipramine", "Imipramine",
    "Haloperidol", "Risperidone", "Olanzapine", "Quetiapine",
    "Aripiprazole", "Clozapine", "Lithium", "Levodopa",
    "Carbidopa", "Pramipexole", "Ropinirole", "Donepezil",
    "Rivastigmine", "Memantine",
    # Hormones / Endocrinologie
    "Levothyroxine", "Carbimazole", "Propylthiouracile",
    "Prednisolone", "Methylprednisolone", "Dexamethasone", "Hydrocortisone",
    "Betamethasone", "Triamcinolone", "Fludrocortisone",
    "Testosterone", "Estradiol", "Progesterone", "Levonorgestrel",
    "Ethinylestradiol", "Medroxyprogesterone", "Finasteride",
    # Antiviraux / Antiparasitaires
    "Aciclovir", "Valaciclovir", "Famciclovir", "Oseltamivir",
    "Chloroquine", "Hydroxychloroquine", "Artemether", "Lumefantrine",
    "Quinine", "Metronidazole", "Albendazole", "Mebendazole",
    "Ivermectine", "Praziquantel",
    # Antifongiques
    "Fluconazole", "Itraconazole", "Voriconazole", "Ketoconazole",
    "Terbinafine", "Nystatine", "Amphotericine B", "Griseofulvine",
    # Divers
    "Allopurinol", "Colchicine", "Probenecide",
    "Ferrous Sulfate", "Acide Folique", "Vitamine B12", "Vitamine D",
    "Calcium", "Potassium Chloride", "Magnesium",
    "Levamisole", "Azathioprine", "Methotrexate", "Hydroxychloroquine",
    "Ciclosporine", "Tacrolimus",
])



def get_resource_path(filename):
    """Retourne le chemin absolu vers une ressource (fonctionne aussi en .exe PyInstaller)."""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


DB_PATH = get_resource_path('medsafe_cabinet.db')
LOGO_PATH = get_resource_path('mokkt.jpg')

# =========================================================
# THÈME GLOBAL MEDSAFE — même Design System
# =========================================================
COULEURS = {
    "fond_principal": "#F0F4F3",
    "fond_sidebar": "#0D2B28",
    "fond_carte": "#FFFFFF",
    "vert_primaire": "#1A6B55",
    "vert_clair": "#2C9970",
    "vert_accent": "#3EBF8A",
    "teal_doux": "#A8D5C8",
    "texte_principal": "#0D2B28",
    "texte_clair": "#FFFFFF",
    "texte_gris": "#6B7F7D",
    "danger": "#C0392B",
    "warning": "#E67E22",
    "bordure": "#D4E8E2",
    "fond_input": "#EEF5F3",
    "sidebar_active": "#1A6B55",
    "sidebar_hover": "#1A4A40",
    "fond_entete": "#0D2B28",
}

FONT_TITRE = ("Segoe UI", 26, "bold")
FONT_SOUS = ("Segoe UI", 14, "bold")
FONT_NORMAL = ("Segoe UI", 13)
FONT_PETIT = ("Segoe UI", 11)
FONT_BTN = ("Segoe UI", 13, "bold")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


# =========================================================
# COMPOSANTS
# =========================================================
def creer_carte(parent, **kwargs):
    outer = ctk.CTkFrame(parent, fg_color=COULEURS["bordure"], corner_radius=14)
    inner = ctk.CTkFrame(outer, fg_color=COULEURS["fond_carte"], corner_radius=12, **kwargs)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    return outer, inner


def creer_badge(parent, texte, couleur_fond, couleur_texte, taille=11):
    return ctk.CTkLabel(parent, text=texte, fg_color=couleur_fond, text_color=couleur_texte,
                        font=("Segoe UI", taille, "bold"), corner_radius=8, padx=10, pady=3)


def creer_separateur(parent, couleur=None):
    c = couleur or COULEURS["bordure"]
    sep = ctk.CTkFrame(parent, height=1, fg_color=c)
    sep.pack(fill="x", padx=20, pady=8)
    return sep


# =========================================================
# WIDGET AUTOCOMPLETE — saisie multi-médicaments
# =========================================================
class AutocompleteEntry(ctk.CTkEntry):
    """
    CTkEntry avec dropdown d'autocomplétion pour saisie
    multi-médicaments séparés par des virgules.
    Supporte : frappe, ↑↓ clavier, Entrée, clic, Échap.
    """
    MAX_SUGGESTIONS = 8

    def __init__(self, master, suggestions: list, **kwargs):
        super().__init__(master, **kwargs)
        self._all_items = [s.strip() for s in suggestions]
        self._popup     = None
        self._listbox   = None
        self._sel_idx   = -1
        self._suppressed = False  # évite la boucle textvariable→trace→popup

        # Surveiller chaque frappe
        self._var = ctk.StringVar()
        self.configure(textvariable=self._var)
        self._var.trace_add("write", self._on_text_changed)

        self.bind("<KeyPress-Down>",   self._move_down)
        self.bind("<KeyPress-Up>",     self._move_up)
        self.bind("<Return>",          self._on_enter)
        self.bind("<Escape>",          lambda e: self._fermer_popup())
        self.bind("<FocusOut>",        self._on_focus_out)
        self.bind("<Tab>",             self._on_tab)

    # ── Logique mot courant ─────────────────────────────────
    def _mot_courant(self):
        """Retourne le fragment après la dernière virgule."""
        txt = self._var.get()
        parts = txt.split(",")
        return parts[-1].strip()

    def _remplacer_mot_courant(self, choix: str):
        """Remplace le dernier fragment par le médicament choisi."""
        txt   = self._var.get()
        parts = txt.split(",")
        parts[-1] = " " + choix
        self._suppressed = True
        self._var.set(",".join(parts) + ", ")
        self._suppressed = False
        self.icursor("end")
        self._fermer_popup()

    # ── Filtrage ────────────────────────────────────────────
    def _suggestions(self):
        mot = self._mot_courant().lower()
        if len(mot) < 1:
            return []
        # Commence par > Contient
        debut   = [s for s in self._all_items if s.lower().startswith(mot)]
        contient = [s for s in self._all_items if mot in s.lower() and not s.lower().startswith(mot)]
        return (debut + contient)[:self.MAX_SUGGESTIONS]

    # ── Événements ─────────────────────────────────────────
    def _on_text_changed(self, *_):
        if self._suppressed:
            return
        sugg = self._suggestions()
        if sugg:
            self._afficher_popup(sugg)
        else:
            self._fermer_popup()

    def _move_down(self, event):
        if self._listbox:
            self._sel_idx = min(self._sel_idx + 1, self._listbox.size() - 1)
            self._highlight(self._sel_idx)
        return "break"

    def _move_up(self, event):
        if self._listbox:
            self._sel_idx = max(self._sel_idx - 1, 0)
            self._highlight(self._sel_idx)
        return "break"

    def _on_enter(self, event):
        if self._listbox and self._sel_idx >= 0:
            self._selectionner(self._sel_idx)
            return "break"

    def _on_tab(self, event):
        if self._listbox and self._listbox.size() > 0:
            idx = self._sel_idx if self._sel_idx >= 0 else 0
            self._selectionner(idx)
            return "break"

    def _on_focus_out(self, event):
        # Délai pour laisser le clic sur le listbox s'enregistrer d'abord
        self.after(150, self._fermer_popup)

    # ── Popup ───────────────────────────────────────────────
    def _afficher_popup(self, suggestions: list):
        self._fermer_popup()
        self._sel_idx = -1

        # Coordonnées absolues sous l'entry
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2
        w = self.winfo_width()

        self._popup = ctk.CTkToplevel(self)
        self._popup.wm_overrideredirect(True)
        self._popup.wm_geometry(f"{w}x{min(len(suggestions), self.MAX_SUGGESTIONS) * 36}+{x}+{y}")
        self._popup.configure(fg_color=COULEURS["fond_sidebar"])
        self._popup.lift()
        self._popup.attributes("-topmost", True)

        import tkinter as tk
        self._listbox = tk.Listbox(
            self._popup,
            font=("Segoe UI", 12),
            bg=COULEURS["fond_sidebar"],
            fg=COULEURS["texte_clair"],
            selectbackground=COULEURS["vert_primaire"],
            selectforeground="white",
            activestyle="none",
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self._listbox.pack(fill="both", expand=True)

        for s in suggestions:
            self._listbox.insert("end", f"  💊  {s}")

        self._listbox.bind("<ButtonRelease-1>", self._on_click)
        self._listbox.bind("<Motion>",          self._on_hover)

    def _highlight(self, idx):
        if self._listbox:
            self._listbox.selection_clear(0, "end")
            self._listbox.selection_set(idx)
            self._listbox.see(idx)

    def _on_hover(self, event):
        idx = self._listbox.nearest(event.y)
        self._sel_idx = idx
        self._highlight(idx)

    def _on_click(self, event):
        idx = self._listbox.nearest(event.y)
        self._selectionner(idx)

    def _selectionner(self, idx):
        if self._listbox:
            raw = self._listbox.get(idx)           # "  💊  Amoxicilline"
            choix = raw.replace("💊", "").strip()
            self._remplacer_mot_courant(choix)
            self.focus_set()

    def _fermer_popup(self):
        if self._popup:
            try:
                self._popup.destroy()
            except Exception:
                pass
            self._popup   = None
            self._listbox = None


# =========================================================
# MEDSAFE AI ENGINE — Moteur DistilBERT partagé
# =========================================================
class MedSafeAI:
    """Singleton léger qui charge le modèle DistilBERT une seule fois."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None
            cls._instance.tokenizer = None
            cls._instance.loaded = False
            cls._instance.loading = False
            cls._instance._callbacks = []
        return cls._instance

    def load_async(self, on_ready=None, on_log=None):
        """Lance le chargement en arrière-plan. on_ready(ok: bool) appelé quand terminé."""
        if self.loaded:
            if on_ready:
                on_ready(True)
            return
        if on_ready:
            self._callbacks.append(on_ready)
        if self.loading:
            return
        self.loading = True
        self._on_log = on_log

        def _load():
            try:
                self._log("🔍 Recherche du modèle IA...")
                # Extraire le zip si le dossier n'existe pas encore
                if not os.path.exists(AI_MODEL_DIR):
                    if os.path.exists(AI_ZIP_PATH):
                        self._log(f"📦 Extraction de {AI_ZIP_PATH}…")
                        with zipfile.ZipFile(AI_ZIP_PATH, 'r') as z:
                            z.extractall(AI_MODEL_DIR)
                        self._log("✅ Extraction terminée")
                    else:
                        self._log(f"❌ Introuvable : {AI_ZIP_PATH}")
                        self._notify(False)
                        return

                self._log("⏳ Chargement du tokenizer…")
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                self.tokenizer = AutoTokenizer.from_pretrained(AI_MODEL_DIR)

                self._log("⏳ Chargement du modèle DistilBERT…")
                self.model = AutoModelForSequenceClassification.from_pretrained(AI_MODEL_DIR)
                self.model.eval()

                self.loaded = True
                self._log("✅ Modèle IA prêt !")
                self._notify(True)
            except Exception as e:
                self._log(f"❌ Erreur chargement : {e}")
                self._notify(False)

        threading.Thread(target=_load, daemon=True).start()

    def _log(self, msg):
        if self._on_log:
            try:
                self._on_log(msg)
            except Exception:
                pass

    def _notify(self, ok):
        self.loading = False
        for cb in self._callbacks:
            try:
                cb(ok)
            except Exception:
                pass
        self._callbacks.clear()

    def predict(self, drug1: str, drug2: str) -> dict:
        """Retourne {'risk': 'MILD'|'CAUTION'|'DANGER', 'confidence': float, 'label': int}"""
        import torch
        import numpy as np
        text = f"{drug1.lower()} interacts with {drug2.lower()}"
        enc  = self.tokenizer(text, return_tensors='pt', max_length=64,
                              truncation=True, padding='max_length')
        with torch.no_grad():
            logits = self.model(**enc).logits
            proba  = torch.softmax(logits, dim=1).numpy()[0]
            pred   = int(np.argmax(proba))
        return {
            'drug1': drug1, 'drug2': drug2,
            'label': pred,
            'risk':  LABEL_MAP[pred],
            'confidence': round(float(proba[pred]) * 100, 1),
        }


# =========================================================
# 1. FENÊTRE DE CONNEXION PHARMACIEN
# =========================================================
class LoginPharmacien(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MEDSAFE — Espace Pharmacie")
        self.geometry("480x720")
        self.resizable(False, False)
        self.configure(fg_color=COULEURS["fond_principal"])
        self.connexion_reussie = False
        self.pharmacien_data = None
        self.afficher_login()

    def nettoyer(self):
        for w in self.winfo_children():
            w.destroy()

    def ajouter_logo(self, taille=(110, 110)):
        try:
            img = ctk.CTkImage(light_image=Image.open(LOGO_PATH), dark_image=Image.open(LOGO_PATH), size=taille)
            ctk.CTkLabel(self, image=img, text="").pack(pady=(45, 6))
        except Exception:
            logo_frame = ctk.CTkFrame(self, fg_color=COULEURS["vert_primaire"], corner_radius=55,
                                      width=taille[0], height=taille[1])
            logo_frame.pack(pady=(45, 6))
            logo_frame.pack_propagate(False)
            ctk.CTkLabel(logo_frame, text="💊", font=("Segoe UI", 38), text_color="white").place(relx=0.5, rely=0.5,
                                                                                                anchor="center")

    def afficher_login(self):
        self.nettoyer()
        self.ajouter_logo()

        ctk.CTkLabel(self, text="MEDSAFE", font=("Segoe UI", 28, "bold"),
                     text_color=COULEURS["fond_entete"]).pack()
        ctk.CTkLabel(self, text="Portail Pharmacie", font=("Segoe UI", 13),
                     text_color=COULEURS["texte_gris"]).pack(pady=(2, 28))

        outer, card = creer_carte(self)
        outer.pack(padx=40, fill="x")

        ctk.CTkLabel(card, text="Connexion", font=("Segoe UI", 15, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(20, 12))

        self.entry_email = ctk.CTkEntry(
            card, placeholder_text="Email de la pharmacie",
            height=44, corner_radius=10, fg_color=COULEURS["fond_input"],
            border_color=COULEURS["bordure"], border_width=1,
            text_color=COULEURS["texte_principal"], font=FONT_NORMAL
        )
        self.entry_email.pack(fill="x", padx=24, pady=6)

        self.entry_mdp = ctk.CTkEntry(
            card, placeholder_text="Mot de passe", show="●",
            height=44, corner_radius=10, fg_color=COULEURS["fond_input"],
            border_color=COULEURS["bordure"], border_width=1,
            text_color=COULEURS["texte_principal"], font=FONT_NORMAL
        )
        self.entry_mdp.pack(fill="x", padx=24, pady=6)

        ctk.CTkButton(
            card, text="Se connecter", height=46,
            fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
            font=FONT_BTN, corner_radius=10, command=self.verifier_login
        ).pack(fill="x", padx=24, pady=(14, 20))

        lien = ctk.CTkFrame(self, fg_color="transparent")
        lien.pack(pady=16)
        ctk.CTkLabel(lien, text="Nouvelle pharmacie ?", font=FONT_PETIT,
                     text_color=COULEURS["texte_gris"]).pack(side="left")
        ctk.CTkButton(lien, text=" S'inscrire", fg_color="transparent",
                      text_color=COULEURS["vert_primaire"], hover_color=COULEURS["fond_principal"],
                      font=("Segoe UI", 11, "bold"), command=self.afficher_inscription).pack(side="left")

    def afficher_inscription(self):
        self.nettoyer()
        self.ajouter_logo((90, 90))
        ctk.CTkLabel(self, text="Inscrire une pharmacie", font=("Segoe UI", 18, "bold"),
                     text_color=COULEURS["fond_entete"]).pack(pady=(4, 18))

        outer, card = creer_carte(self)
        outer.pack(padx=40, fill="x")

        champs = [
            ("reg_nom", "Nom du pharmacien (ex : Dr. Yassine)", False),
            ("reg_pharmacie", "Nom de la pharmacie", False),
            ("reg_email", "Adresse email", False),
            ("reg_mdp", "Mot de passe", True),
        ]
        for attr, ph, is_pass in champs:
            e = ctk.CTkEntry(card, placeholder_text=ph, height=42, corner_radius=10,
                             fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
                             border_width=1, text_color=COULEURS["texte_principal"],
                             font=FONT_NORMAL, show="●" if is_pass else "")
            e.pack(fill="x", padx=24, pady=5)
            setattr(self, attr, e)

        ctk.CTkButton(card, text="Créer le compte", height=44, fg_color=COULEURS["vert_primaire"],
                      hover_color=COULEURS["vert_clair"], font=FONT_BTN, corner_radius=10,
                      command=self.enregistrer_pharmacien).pack(fill="x", padx=24, pady=(12, 20))

        ctk.CTkButton(self, text="← Retour à la connexion", fg_color="transparent",
                      text_color=COULEURS["texte_gris"], hover_color=COULEURS["fond_principal"],
                      font=FONT_PETIT, command=self.afficher_login).pack(pady=8)

    def verifier_login(self):
        email, mdp = self.entry_email.get(), self.entry_mdp.get()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pharmaciens WHERE email = ? AND mot_de_passe = ?", (email, mdp))
            p = cursor.fetchone()
            conn.close()
            if p:
                self.pharmacien_data = p
                self.connexion_reussie = True
                self.quit()
                self.destroy()
            else:
                messagebox.showerror("Erreur", "Identifiants incorrects.")
        except Exception:
            messagebox.showerror("Erreur", "Aucune pharmacie enregistrée.")

    def enregistrer_pharmacien(self):
        nom = self.reg_nom.get()
        pharmacie = self.reg_pharmacie.get()
        email = self.reg_email.get()
        mdp = self.reg_mdp.get()
        if not nom or not email or not mdp:
            messagebox.showwarning("Champs manquants", "Remplissez tous les champs.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS pharmaciens
                (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, pharmacie TEXT, email TEXT UNIQUE, mot_de_passe TEXT)''')
            cursor.execute("INSERT INTO pharmaciens (nom, pharmacie, email, mot_de_passe) VALUES (?, ?, ?, ?)",
                           (nom, pharmacie, email, mdp))
            conn.commit()
            conn.close()
            messagebox.showinfo("Inscrit ✓", "Pharmacie inscrite avec succès !")
            self.afficher_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Email existant", "Cet email est déjà utilisé.")


# =========================================================
# 2. TABLEAU DE BORD PHARMACIEN
# =========================================================
class DashboardPharmacien(ctk.CTk):
    def __init__(self, pharmacien_connecte):
        super().__init__()
        self.pharm_info = pharmacien_connecte
        self.title("MEDSAFE — Espace Pharmacie")
        self.geometry("1240x820")
        self.minsize(1000, 680)
        self.configure(fg_color=COULEURS["fond_principal"])
        self.ai = MedSafeAI()
        self._construire_interface()
        self.afficher_profil()
        # Lancement du chargement IA en arrière-plan dès l'ouverture
        self.ai.load_async(on_ready=self._on_ai_ready, on_log=self._ai_log)

    def _construire_interface(self):
        # ─── SIDEBAR ───────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COULEURS["fond_sidebar"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        try:
            img = ctk.CTkImage(light_image=Image.open(LOGO_PATH), dark_image=Image.open(LOGO_PATH), size=(120, 120))
            ctk.CTkLabel(self.sidebar, image=img, text="").pack(pady=(30, 4))
        except Exception:
            logo_f = ctk.CTkFrame(self.sidebar, fg_color=COULEURS["vert_primaire"],
                                  corner_radius=40, width=80, height=80)
            logo_f.pack(pady=(30, 4))
            logo_f.pack_propagate(False)
            ctk.CTkLabel(logo_f, text="💊", font=("Segoe UI", 32), text_color="white").place(relx=0.5, rely=0.5,
                                                                                            anchor="center")

        ctk.CTkLabel(self.sidebar, text="MEDSAFE", font=("Segoe UI", 16, "bold"),
                     text_color=COULEURS["teal_doux"]).pack()
        ctk.CTkLabel(self.sidebar, text="Espace Pharmacie", font=("Segoe UI", 10),
                     text_color="#7AAFA4").pack(pady=(0, 24))

        creer_separateur(self.sidebar, "#1A3D38")

        self.btns_nav = {}
        nav_items = [
            ("👤", "Mon Profil", self.afficher_profil),
            ("📥", "Contrôle Ordonnance", self.afficher_controle_ordo),
            ("💊", "Stocks Pharmacie", self.afficher_stock),
            ("📢", "Panneaux Pub", self.afficher_panneaux_pub),
        ]
        for icone, label, cmd in nav_items:
            btn = self._creer_btn_nav(icone, label, cmd)
            self.btns_nav[label] = btn

        # Pied sidebar
        creer_separateur(self.sidebar, "#1A3D38")
        nom = self.pharm_info[1] if self.pharm_info else "Pharmacien"
        phar = self.pharm_info[2] if self.pharm_info else ""
        ctk.CTkLabel(self.sidebar, text=nom, font=("Segoe UI", 12, "bold"),
                     text_color=COULEURS["texte_clair"]).pack(pady=(10, 0))
        ctk.CTkLabel(self.sidebar, text=phar, font=("Segoe UI", 10),
                     text_color="#7AAFA4").pack(pady=(0, 8))
        ctk.CTkButton(
            self.sidebar, text="Déconnexion", height=34, fg_color="#1A3D38",
            hover_color=COULEURS["danger"], text_color="#7AAFA4", font=("Segoe UI", 11),
            command=self.destroy, corner_radius=8
        ).pack(padx=20, pady=(0, 20), fill="x")

        # ─── CONTENU ───────────────────────────────────────────────
        self.zone_contenu = ctk.CTkScrollableFrame(self, fg_color=COULEURS["fond_principal"], corner_radius=0)
        self.zone_contenu.pack(side="right", fill="both", expand=True)

    def _creer_btn_nav(self, icone, label, cmd):
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", corner_radius=10)
        frame.pack(fill="x", padx=12, pady=2)
        btn = ctk.CTkButton(frame, text=f"  {icone}  {label}", anchor="w", height=44,
                            corner_radius=10, fg_color="transparent",
                            hover_color=COULEURS["sidebar_hover"], font=("Segoe UI", 13),
                            text_color=COULEURS["texte_clair"],
                            command=lambda: self._nav(label, cmd))
        btn.pack(fill="x")
        return btn

    def _nav(self, label, cmd):
        for lbl, btn in self.btns_nav.items():
            btn.configure(fg_color=COULEURS["sidebar_active"] if lbl == label else "transparent")
        cmd()

    # ─── CALLBACKS IA ──────────────────────────────────────────────
    def _on_ai_ready(self, ok):
        """Appelé depuis le thread IA quand le modèle est prêt (ou en erreur)."""
        def _update():
            if ok:
                # Met à jour le badge statut si la section contrôle est ouverte
                if hasattr(self, '_ai_status_lbl'):
                    self._ai_status_lbl.configure(
                        text="✅  Modèle IA prêt", fg_color="#1A4A3A", text_color=COULEURS["vert_accent"])
                if hasattr(self, '_btn_analyse'):
                    self._btn_analyse.configure(state="normal")
            else:
                if hasattr(self, '_ai_status_lbl'):
                    self._ai_status_lbl.configure(
                        text="❌  Modèle introuvable — placez medsafe_model.zip ici",
                        fg_color="#4A1F1F", text_color=COULEURS["danger"])
        self.after(0, _update)

    def _ai_log(self, msg):
        """Redirige les logs IA vers la zone résultat si elle est visible."""
        def _write():
            if hasattr(self, 'resultat_analyse'):
                try:
                    self.resultat_analyse.insert("end", msg + "\n")
                    self.resultat_analyse.see("end")
                except Exception:
                    pass
        self.after(0, _write)

    def nettoyer_contenu(self):
        for w in self.zone_contenu.winfo_children():
            w.destroy()

    def _entete_section(self, titre, sous_titre=""):
        f = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        f.pack(fill="x", padx=30, pady=(28, 0))
        ctk.CTkLabel(f, text=titre, font=FONT_TITRE, text_color=COULEURS["texte_principal"]).pack(anchor="w")
        if sous_titre:
            ctk.CTkLabel(f, text=sous_titre, font=FONT_PETIT, text_color=COULEURS["texte_gris"]).pack(anchor="w",
                                                                                                      pady=(2, 0))

    # ─── 0. PROFIL ─────────────────────────────────────────────────
    def afficher_profil(self):
        self._nav("Mon Profil", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Mon Profil", "Informations de la pharmacie")

        outer, card = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=20)

        header = ctk.CTkFrame(card, fg_color=COULEURS["vert_primaire"], corner_radius=0, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        nom = self.pharm_info[1] if self.pharm_info else "Pharmacien"
        phar = self.pharm_info[2] if self.pharm_info else "—"
        email = self.pharm_info[3] if self.pharm_info else "—"

        ctk.CTkLabel(header, text=nom, font=("Segoe UI", 20, "bold"), text_color="white").pack(anchor="w", padx=30,
                                                                                               pady=(18, 0))
        ctk.CTkLabel(header, text=phar, font=("Segoe UI", 12), text_color=COULEURS["teal_doux"]).pack(anchor="w",
                                                                                                      padx=30)

        info_f = ctk.CTkFrame(card, fg_color="transparent")
        info_f.pack(fill="x", padx=30, pady=20)

        for lbl, val in [("Pharmacie", phar), ("Email", email), ("Statut", "Actif ✓")]:
            row = ctk.CTkFrame(info_f, fg_color=COULEURS["fond_input"], corner_radius=8)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=lbl, font=("Segoe UI", 11), text_color=COULEURS["texte_gris"],
                         width=120, anchor="w").pack(side="left", padx=16, pady=12)
            ctk.CTkLabel(row, text=val, font=("Segoe UI", 12, "bold"),
                         text_color=COULEURS["texte_principal"]).pack(side="left", padx=8)

        # Stats
        stats = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        stats.pack(fill="x", padx=30)

        def _compter(tbl):
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute(f"SELECT COUNT(*) FROM {tbl}")
                v = c.fetchone()[0]
                conn.close()
                return v
            except Exception:
                return "—"

        for label, val, icone, couleur in [
            ("Médicaments en stock", _compter("stock_pharmacie"), "💊", COULEURS["vert_accent"]),
            ("Ordonnances lues", "—", "📥", "#3D8EC4"),
        ]:
            outer2, c2 = creer_carte(stats)
            outer2.pack(side="left", expand=True, fill="x", padx=8, pady=8)
            ctk.CTkLabel(c2, text=icone, font=("Segoe UI", 26)).pack(pady=(20, 4))
            ctk.CTkLabel(c2, text=str(val), font=("Segoe UI", 28, "bold"), text_color=couleur).pack()
            ctk.CTkLabel(c2, text=label, font=FONT_PETIT, text_color=COULEURS["texte_gris"]).pack(pady=(2, 18))

    # ─── 1. CONTRÔLE ORDONNANCE ────────────────────────────────────
    def afficher_controle_ordo(self):
        self._nav("Contrôle Ordonnance", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Contrôle d'Ordonnance", "Importation et vérification IA des interactions médicamenteuses")

        # Import ordonnance
        outer, card_imp = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=(16, 8))

        hdr = ctk.CTkFrame(card_imp, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(16, 8))
        ctk.CTkLabel(hdr, text="Ordonnance importée", font=("Segoe UI", 13, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(side="left")
        ctk.CTkButton(hdr, text="📂  Importer un fichier .txt", height=36, corner_radius=8,
                      fg_color=COULEURS["fond_entete"], hover_color=COULEURS["vert_primaire"],
                      font=FONT_BTN, command=self.charger_ordonnance).pack(side="right")

        self.texte_ordo_lue = ctk.CTkTextbox(
            card_imp, height=160, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"], border_width=1,
            font=("Courier New", 13), text_color=COULEURS["texte_principal"]
        )
        self.texte_ordo_lue.pack(fill="both", padx=24, pady=(0, 20))
        self.texte_ordo_lue.insert("0.0", "Le contenu de l'ordonnance s'affichera ici après importation…")

        # Vérificateur interactions IA
        outer2, card_ana = creer_carte(self.zone_contenu)
        outer2.pack(fill="both", expand=True, padx=30, pady=(0, 24))

        # Bandeau rouge alerte
        alerte_hdr = ctk.CTkFrame(card_ana, fg_color="#C0392B", corner_radius=12, height=50)
        alerte_hdr.pack(fill="x")
        alerte_hdr.pack_propagate(False)
        ctk.CTkLabel(alerte_hdr, text="⚠   VÉRIFICATEUR D'INTERACTIONS MÉDICAMENTEUSES — IA DistilBERT",
                     font=("Segoe UI", 12, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # Badge statut IA
        ai_status_txt = "✅  Modèle IA prêt" if self.ai.loaded else "⏳  Chargement du modèle IA…"
        ai_status_bg  = "#1A4A3A" if self.ai.loaded else "#3A3020"
        ai_status_col = COULEURS["vert_accent"] if self.ai.loaded else COULEURS["warning"]
        self._ai_status_lbl = ctk.CTkLabel(
            card_ana, text=ai_status_txt, font=("Segoe UI", 11, "bold"),
            fg_color=ai_status_bg, text_color=ai_status_col,
            corner_radius=8, padx=14, pady=4
        )
        self._ai_status_lbl.pack(anchor="e", padx=24, pady=(10, 0))

        box = ctk.CTkFrame(card_ana, fg_color="transparent")
        box.pack(fill="x", padx=24, pady=(10, 8))

        self.entry_meds_check = AutocompleteEntry(
            box,
            suggestions=MEDICAMENTS,
            placeholder_text="Ex : Aspirine, Warfarine, Metformine… (↓ pour suggestions)",
            height=42, corner_radius=10, fg_color=COULEURS["fond_input"],
            border_color=COULEURS["bordure"], border_width=1,
            text_color=COULEURS["texte_principal"], font=FONT_NORMAL
        )
        self.entry_meds_check.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_state = "normal" if self.ai.loaded else "disabled"
        self._btn_analyse = ctk.CTkButton(
            box, text="⚡ Lancer l'analyse IA", height=42, corner_radius=10, width=180,
            fg_color=COULEURS["danger"], hover_color="#A93226",
            font=FONT_BTN, state=btn_state, command=self.lancer_analyse
        )
        self._btn_analyse.pack(side="right")

        self.resultat_analyse = ctk.CTkTextbox(
            card_ana, height=200, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
            border_width=1, font=("Segoe UI", 13), text_color=COULEURS["texte_principal"]
        )
        self.resultat_analyse.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        init_msg = ("Modèle IA prêt. Entrez les médicaments pour vérifier les interactions avant délivrance."
                    if self.ai.loaded else
                    "⏳ Chargement du modèle DistilBERT en arrière-plan…\nCela peut prendre quelques secondes.")
        self.resultat_analyse.insert("0.0", init_msg)

    def charger_ordonnance(self):
        fp = filedialog.askopenfilename(title="Choisir une ordonnance", filetypes=[("Fichiers Texte", "*.txt")])
        if fp:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    contenu = f.read()
                self.texte_ordo_lue.delete("0.0", "end")
                self.texte_ordo_lue.insert("0.0", contenu)
            except Exception:
                messagebox.showerror("Erreur", "Impossible de lire le fichier.")

    def lancer_analyse(self):
        raw = self.entry_meds_check.get().strip()
        if not raw:
            messagebox.showwarning("Champ vide", "Entrez au moins 2 médicaments séparés par des virgules.")
            return
        if not self.ai.loaded:
            messagebox.showwarning("Modèle IA", "Le modèle IA est encore en cours de chargement. Patientez.")
            return

        meds = [m.strip().title() for m in raw.split(",") if m.strip()]
        if len(meds) < 2:
            messagebox.showwarning("Attention", "Entrez au moins 2 médicaments séparés par des virgules.")
            return

        self._btn_analyse.configure(state="disabled", text="⏳ Analyse…")
        self.resultat_analyse.delete("0.0", "end")
        self.resultat_analyse.insert("0.0",
            f"🤖  Analyse IA DistilBERT — {len(list(combinations(meds, 2)))} paire(s) à évaluer…\n"
            + "─" * 62 + "\n")

        def run():
            try:
                pairs   = list(combinations(meds, 2))
                results = []
                for d1, d2 in pairs:
                    r = self.ai.predict(d1, d2)
                    results.append(r)

                # Tri : DANGER en premier
                results.sort(key=lambda x: -x['label'])

                def afficher():
                    counts = {0: 0, 1: 0, 2: 0}
                    for r in results:
                        counts[r['label']] += 1
                        icone  = EMOJI_MAP[r['label']]
                        risque = r['risk']
                        conf   = r['confidence']

                        ligne = f"{icone}  {r['drug1']}  +  {r['drug2']}  →  {risque}  ({conf}%)\n"

                        if r['label'] == 2:
                            ligne += (
                                "   ❌  ALERTE MAJEURE — Ne pas délivrer sans contact médecin !\n"
                                "   📢  Conseil : Contacter le prescripteur avant toute délivrance.\n"
                            )
                        elif r['label'] == 1:
                            ligne += "   ⚠️  PRUDENCE — Surveiller le patient, informer du risque.\n"
                        else:
                            ligne += "   ✅  Interaction faible — Délivrance possible avec surveillance.\n"

                        self.resultat_analyse.insert("end", ligne + "\n")

                    # Résumé final
                    self.resultat_analyse.insert("end", "─" * 62 + "\n")
                    summary = (
                        f"📊  Résumé : {len(results)} paire(s) analysée(s)\n"
                        f"   🔴 DANGER  : {counts[2]}\n"
                        f"   🟡 CAUTION : {counts[1]}\n"
                        f"   🟢 MILD    : {counts[0]}\n"
                    )
                    if counts[2] > 0:
                        summary += f"\n⛔  {counts[2]} interaction(s) dangereuse(s) ! Contactez le médecin.\n"
                    else:
                        summary += "\n✅  Aucune interaction critique détectée. Délivrance possible.\n"

                    self.resultat_analyse.insert("end", summary)
                    self._btn_analyse.configure(state="normal", text="⚡ Lancer l'analyse IA")

                self.after(0, afficher)

            except Exception as e:
                self.after(0, lambda: (
                    self.resultat_analyse.insert("end", f"\n❌  Erreur IA : {e}\n"),
                    self._btn_analyse.configure(state="normal", text="⚡ Lancer l'analyse IA")
                ))

        threading.Thread(target=run, daemon=True).start()

    # ─── 2. STOCKS PHARMACIE ──────────────────────────────────────
    def afficher_stock(self):
        self._nav("Stocks Pharmacie", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Gestion des Stocks", "Inventaire de la pharmacie")

        outer, form = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=(16, 8))

        ctk.CTkLabel(form, text="Ajouter un médicament", font=("Segoe UI", 13, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(16, 8))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 16))

        self.e_nom = AutocompleteEntry(row, suggestions=MEDICAMENTS,
                                  placeholder_text="Médicament (ex : Doliprane 1g)", height=40,
                                  corner_radius=10, fg_color=COULEURS["fond_input"],
                                  border_color=COULEURS["bordure"], border_width=1,
                                  text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_nom.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.e_qte = ctk.CTkEntry(row, placeholder_text="Boîtes", height=40, width=90,
                                  corner_radius=10, fg_color=COULEURS["fond_input"],
                                  border_color=COULEURS["bordure"], border_width=1,
                                  text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_qte.pack(side="left", padx=(0, 8))

        self.e_seuil = ctk.CTkEntry(row, placeholder_text="Seuil", height=40, width=90,
                                    corner_radius=10, fg_color=COULEURS["fond_input"],
                                    border_color=COULEURS["bordure"], border_width=1,
                                    text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_seuil.pack(side="left", padx=(0, 8))

        ctk.CTkButton(row, text="Ajouter", height=40, width=100, corner_radius=10,
                      fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
                      font=FONT_BTN, command=self.ajouter_stock).pack(side="right")

        self.liste_stock = ctk.CTkScrollableFrame(
            self.zone_contenu, fg_color=COULEURS["fond_carte"],
            corner_radius=12, border_color=COULEURS["bordure"], border_width=1
        )
        self.liste_stock.pack(fill="both", expand=True, padx=30, pady=(0, 24))
        self.charger_stock()

    def ajouter_stock(self):
        # On enlève les espaces inutiles avec .strip()
        nom = self.e_nom.get().strip()
        qte = self.e_qte.get().strip()
        seuil = self.e_seuil.get().strip()

        if not nom or not qte:
            messagebox.showwarning("Incomplet", "Remplissez le nom et la quantité.")
            return

        # Vérification stricte que ce sont des nombres
        if not qte.isdigit():
            messagebox.showerror("Erreur", "La quantité doit être un nombre entier.")
            return

        if seuil and not seuil.isdigit():
            messagebox.showerror("Erreur", "Le seuil doit être un nombre entier.")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS stock_pharmacie
                (id INTEGER PRIMARY KEY AUTOINCREMENT, nom_med TEXT, quantite INTEGER, seuil INTEGER)''')

            cursor.execute("INSERT INTO stock_pharmacie (nom_med, quantite, seuil) VALUES (?, ?, ?)",
                           (nom, int(qte), int(seuil) if seuil else 5))
            conn.commit()
            conn.close()

            # Vider les champs après un ajout réussi
            self.e_nom.delete(0, 'end')
            self.e_qte.delete(0, 'end')
            self.e_seuil.delete(0, 'end')

            # Rafraîchir UNIQUEMENT la liste
            self.charger_stock()

        except Exception as e:
            messagebox.showerror("Erreur BDD", f"Une erreur s'est produite : {e}")

    def charger_stock(self):
        for w in self.liste_stock.winfo_children():
            w.destroy()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS stock_pharmacie
                (id INTEGER PRIMARY KEY AUTOINCREMENT, nom_med TEXT, quantite INTEGER, seuil INTEGER)''')
            cursor.execute("SELECT nom_med, quantite, seuil FROM stock_pharmacie ORDER BY nom_med ASC")
            stocks = cursor.fetchall()
            conn.close()

            if not stocks:
                ctk.CTkLabel(self.liste_stock, text="Le stock est vide.", font=FONT_NORMAL,
                             text_color=COULEURS["texte_gris"]).pack(pady=30)
                return

            for nom, qte, seuil in stocks:
                en_alerte = qte <= seuil
                fond = "#FFF5F5" if en_alerte else COULEURS["fond_input"]

                row = ctk.CTkFrame(self.liste_stock, fg_color=fond, corner_radius=10)
                row.pack(fill="x", pady=4, padx=10)

                left = ctk.CTkFrame(row, fg_color="transparent")
                left.pack(side="left", fill="both", expand=True, padx=16, pady=12)
                ctk.CTkLabel(left, text=nom, font=("Segoe UI", 13, "bold"),
                             text_color=COULEURS["texte_principal"]).pack(anchor="w")
                sub = ctk.CTkFrame(left, fg_color="transparent")
                sub.pack(anchor="w", pady=(3, 0))
                ctk.CTkLabel(sub, text=f"En rayon : {qte} boîtes   Seuil : {seuil}",
                             font=FONT_PETIT, text_color=COULEURS["texte_gris"]).pack(side="left")
                if en_alerte:
                    creer_badge(sub, "  ⚠  Rupture imminente  ", "#FFECEC", COULEURS["danger"]).pack(side="left",
                                                                                                     padx=8)

                btn_f = ctk.CTkFrame(row, fg_color="transparent")
                btn_f.pack(side="right", padx=12)

                ctk.CTkButton(btn_f, text="Modifier", height=32, width=80, corner_radius=8,
                              fg_color=COULEURS["fond_input"], hover_color=COULEURS["bordure"],
                              text_color=COULEURS["vert_primaire"], font=("Segoe UI", 11, "bold"),
                              command=lambda n=nom: self.modifier_stock(n)).pack(side="left", padx=4)

                ctk.CTkButton(btn_f, text="Supprimer", height=32, width=90, corner_radius=8,
                              fg_color="#FFECEC", hover_color="#FFCDD2",
                              text_color=COULEURS["danger"], font=("Segoe UI", 11, "bold"),
                              command=lambda n=nom: self.supprimer_stock(n)).pack(side="left", padx=4)

        except Exception as e:
            print(e)

    def supprimer_stock(self, nom):
        if messagebox.askyesno("Confirmer", f"Supprimer « {nom} » ?"):
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.cursor().execute("DELETE FROM stock_pharmacie WHERE nom_med = ?", (nom,))
                conn.commit()
                conn.close()
                self.charger_stock()  # Rafraîchissement fluide
            except Exception as e:
                messagebox.showerror("Erreur BDD", f"Impossible de supprimer : {e}")

    def modifier_stock(self, nom):
        nv = ctk.CTkInputDialog(text=f"Nouvelle quantité pour « {nom} » :", title="Modifier stock").get_input()

        # Si l'utilisateur n'a pas cliqué sur Annuler
        if nv is not None:
            nv = nv.strip()
            if nv.isdigit():
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.cursor().execute("UPDATE stock_pharmacie SET quantite = ? WHERE nom_med = ?", (int(nv), nom))
                    conn.commit()
                    conn.close()
                    self.charger_stock()  # Rafraîchissement fluide
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur de mise à jour: {e}")
            else:
                messagebox.showerror("Erreur", "La quantité doit être un nombre entier.")


    # ─── 3. PANNEAUX PUBLICITAIRES ────────────────────────────────
    def afficher_panneaux_pub(self):
        self._nav("Panneaux Pub", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Panneaux Publicitaires", "Affiches et campagnes de prévention santé")

        PANNEAUX = [
            {
                "titre":      "💉  Vaccination Grippe",
                "sous_titre": "Campagne hivernale",
                "corps":      "Protégez-vous et vos proches.\nVaccin disponible en pharmacie\nsans ordonnance.",
                "cta":        "Disponible maintenant",
                "couleur":    "#1A6B55",
                "badge_txt":  "RECOMMANDÉ",
                "badge_col":  "#3EBF8A",
            },
            {
                "titre":      "🩺  Tension Artérielle",
                "sous_titre": "Dépistage gratuit",
                "corps":      "1 adulte sur 3 est hypertendu\nsans le savoir.\nMesure gratuite en pharmacie.",
                "cta":        "Mesure offerte",
                "couleur":    "#2471A3",
                "badge_txt":  "GRATUIT",
                "badge_col":  "#5DADE2",
            },
            {
                "titre":      "🩸  Diabète",
                "sous_titre": "Semaine nationale",
                "corps":      "Glycémie capillaire rapide.\nRésultats immédiats.\nConseil personnalisé inclus.",
                "cta":        "Dépistage rapide",
                "couleur":    "#884EA0",
                "badge_txt":  "DÉPISTAGE",
                "badge_col":  "#A569BD",
            },
            {
                "titre":      "🤰  Maternité & Santé",
                "sous_titre": "Supplémentation",
                "corps":      "Acide folique, vitamine D,\nfer et oméga-3 disponibles.\nConseils grossesse offerts.",
                "cta":        "Conseil sage-femme",
                "couleur":    "#B7950B",
                "badge_txt":  "CONSEIL",
                "badge_col":  "#F4D03F",
            },
            {
                "titre":      "🚭  Arrêt du Tabac",
                "sous_titre": "Programme pharmacie",
                "corps":      "Patches, gommes, inhalateurs.\nSuivi personnalisé par votre\npharmacien référent.",
                "cta":        "Commencer le sevrage",
                "couleur":    "#C0392B",
                "badge_txt":  "PROGRAMME",
                "badge_col":  "#E74C3C",
            },
            {
                "titre":      "☀️  Protection Solaire",
                "sous_titre": "Été — UV Index élevé",
                "corps":      "SPF 50+ pour toute la famille.\nCrèmes, sprays et sticks\ndisponibles en pharmacie.",
                "cta":        "Voir la gamme",
                "couleur":    "#D35400",
                "badge_txt":  "SAISONNIER",
                "badge_col":  "#E59866",
            },
            {
                "titre":      "💊  Génériques",
                "sous_titre": "Économisez sur vos traitements",
                "corps":      "Même efficacité, prix réduit.\nDemandez à votre pharmacien\nle générique disponible.",
                "cta":        "En savoir plus",
                "couleur":    "#1E8449",
                "badge_txt":  "ÉCONOMIE",
                "badge_col":  "#58D68D",
            },
            {
                "titre":      "🧴  Dermatologie",
                "sous_titre": "Soins de la peau",
                "corps":      "Eczéma, psoriasis, acné.\nGamme dermo-cosmétique\ncomplète en conseil.",
                "cta":        "Consultation offerte",
                "couleur":    "#1A5276",
                "badge_txt":  "NOUVEAUTÉ",
                "badge_col":  "#2E86C1",
            },
        ]

        grille = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        grille.pack(fill="both", expand=True, padx=24, pady=(18, 24))
        grille.columnconfigure(0, weight=1)
        grille.columnconfigure(1, weight=1)

        for i, p in enumerate(PANNEAUX):
            self._creer_carte_pub(grille, p, i // 2, i % 2)

    def _creer_carte_pub(self, parent, data: dict, row: int, col: int):
        couleur = data["couleur"]

        outer = ctk.CTkFrame(parent, fg_color=couleur, corner_radius=16)
        outer.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")

        # ── Entête ────────────────────────────────────────────────
        entete = ctk.CTkFrame(outer, fg_color=couleur, corner_radius=0)
        entete.pack(fill="x", padx=2, pady=(2, 0))

        top_row = ctk.CTkFrame(entete, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            top_row, text=data["titre"],
            font=("Segoe UI", 17, "bold"), text_color="#FFFFFF", anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Badge
        txt_col = "#0D2B28" if data["badge_col"] in ("#F4D03F", "#58D68D", "#E59866") else "white"
        ctk.CTkLabel(
            top_row, text=data["badge_txt"],
            font=("Segoe UI", 10, "bold"),
            fg_color=data["badge_col"], text_color=txt_col,
            corner_radius=6, padx=8, pady=3
        ).pack(side="right")

        ctk.CTkLabel(
            entete, text=data["sous_titre"],
            font=("Segoe UI", 11), text_color="#CCEEEA", anchor="w"
        ).pack(anchor="w", padx=20, pady=(0, 12))

        ctk.CTkFrame(outer, height=1, fg_color="#FFFFFF").pack(fill="x", padx=16)

        # ── Corps blanc ───────────────────────────────────────────
        corps_frame = ctk.CTkFrame(outer, fg_color="#FFFFFF", corner_radius=0)
        corps_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))

        ctk.CTkLabel(
            corps_frame, text=data["corps"],
            font=("Segoe UI", 12), text_color=COULEURS["texte_principal"],
            justify="left", anchor="w", wraplength=300
        ).pack(anchor="w", padx=20, pady=(14, 10))

        # ── Pied CTA ──────────────────────────────────────────────
        pied = ctk.CTkFrame(corps_frame, fg_color=COULEURS["fond_input"], corner_radius=0)
        pied.pack(fill="x")

        cta_row = ctk.CTkFrame(pied, fg_color="transparent")
        cta_row.pack(fill="x", padx=20, pady=12)

        ctk.CTkButton(
            cta_row, text=f"→  {data['cta']}",
            height=34, corner_radius=8,
            fg_color=couleur, hover_color=couleur,
            text_color="white", font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            command=lambda t=data["titre"]: messagebox.showinfo(
                "Panneau", f"{t}\n\nFonction impression / partage à venir.")
        ).pack(side="left")

        ctk.CTkButton(
            cta_row, text="🖨", width=36, height=34, corner_radius=8,
            fg_color=COULEURS["bordure"], hover_color=COULEURS["teal_doux"],
            text_color=COULEURS["texte_principal"], font=("Segoe UI", 14),
            cursor="hand2",
            command=lambda t=data["titre"]: messagebox.showinfo("Impression", f"Impression : {t}")
        ).pack(side="right")
    def deconnexion(self):
        self.quit()

# =========================================================
if __name__ == "__main__":
    login_app = LoginPharmacien()
    login_app.mainloop()

    if login_app.connexion_reussie:
        dash = DashboardPharmacien(login_app.pharmacien_data)
        dash.mainloop()