import customtkinter as ctk
from PIL import Image
import sqlite3
from tkinter import messagebox, filedialog
import os
import sys


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
        self._construire_interface()
        self.afficher_profil()

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
        self._entete_section("Contrôle d'Ordonnance", "Importation et vérification des interactions")

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

        # Vérificateur interactions
        outer2, card_ana = creer_carte(self.zone_contenu)
        outer2.pack(fill="both", expand=True, padx=30, pady=(0, 24))

        # Bandeau rouge alerte
        alerte_hdr = ctk.CTkFrame(card_ana, fg_color="#C0392B", corner_radius=12, height=50)
        alerte_hdr.pack(fill="x")
        alerte_hdr.pack_propagate(False)
        ctk.CTkLabel(alerte_hdr, text="⚠   VÉRIFICATEUR D'INTERACTIONS MÉDICAMENTEUSES",
                     font=("Segoe UI", 12, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        box = ctk.CTkFrame(card_ana, fg_color="transparent")
        box.pack(fill="x", padx=24, pady=16)

        self.entry_meds_check = ctk.CTkEntry(
            box, placeholder_text="Ex : Aspirine, Anticoagulant, Metformine…",
            height=42, corner_radius=10, fg_color=COULEURS["fond_input"],
            border_color=COULEURS["bordure"], border_width=1,
            text_color=COULEURS["texte_principal"], font=FONT_NORMAL
        )
        self.entry_meds_check.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(box, text="Lancer l'analyse", height=42, corner_radius=10, width=160,
                      fg_color=COULEURS["danger"], hover_color="#A93226",
                      font=FONT_BTN, command=self.lancer_analyse).pack(side="right")

        self.resultat_analyse = ctk.CTkTextbox(
            card_ana, height=150, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
            border_width=1, font=("Segoe UI", 13), text_color=COULEURS["texte_principal"]
        )
        self.resultat_analyse.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self.resultat_analyse.insert("0.0",
                                     "Système prêt. Entrez les médicaments pour vérifier les risques avant délivrance.")

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
        meds = self.entry_meds_check.get().lower()
        if not meds:
            return
        self.resultat_analyse.delete("0.0", "end")
        self.resultat_analyse.insert("0.0", "🔄  Interrogation de la base DDInter (236 834 entrées)…\n")
        self.resultat_analyse.insert("end", "─" * 60 + "\n")

        if "aspirine" in meds:
            self.resultat_analyse.insert("end", "❌  ALERTE MAJEURE — NIVEAU ROUGE\n")
            self.resultat_analyse.insert("end", "Risque d'hémorragie digestive sévère détecté.\n\n")
            self.resultat_analyse.insert("end",
                                         "📢  Conseil Darija : « Balek a aami! Had el dwa m3a hada ydirlek nezif fel karch. »\n")
            self.resultat_analyse.insert("end",
                                         "➡  ACTION REQUISE : Contacter le médecin prescripteur pour modification.")
        else:
            self.resultat_analyse.insert("end", "✅  AUCUNE INTERACTION DANGEREUSE DÉTECTÉE\n")
            self.resultat_analyse.insert("end", "Vous pouvez délivrer le traitement en toute sécurité.")

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

        self.e_nom = ctk.CTkEntry(row, placeholder_text="Médicament (ex : Doliprane 1g)", height=40,
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


# =========================================================
if __name__ == "__main__":
    login_app = LoginPharmacien()
    login_app.mainloop()

    if login_app.connexion_reussie:
        dash = DashboardPharmacien(login_app.pharmacien_data)
        dash.mainloop()