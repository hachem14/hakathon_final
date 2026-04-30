import customtkinter as ctk
from PIL import Image
import sqlite3
from tkinter import messagebox, filedialog
import sys
import os


def get_resource_path(filename):
    """Retourne le chemin absolu vers une ressource."""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


DB_PATH = get_resource_path('medsafe_cabinet.db')
LOGO_PATH = get_resource_path('mokkt.jpg')

# =========================================================
# THÈME GLOBAL MEDSAFE — Design System
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
# COMPOSANTS RÉUTILISABLES & PUBLICITÉ
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


def ajouter_banniere_pub(parent):
    """Ajoute un espace publicitaire en bas de l'écran."""
    pub_frame = ctk.CTkFrame(parent, fg_color="#E8F8F5", height=60, corner_radius=0)
    pub_frame.pack(side="bottom", fill="x")
    pub_frame.pack_propagate(False)
    ctk.CTkLabel(pub_frame, text="📢 ESPACE PUBLICITAIRE — Votre annonce ici",
                 font=("Segoe UI", 12, "bold"), text_color=COULEURS["vert_primaire"]).place(relx=0.5, rely=0.5,
                                                                                            anchor="center")
    return pub_frame


# =========================================================
# 1. ÉCRAN DE SÉLECTION DE LA PROFESSION
# =========================================================
class ChoixProfessionWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MEDSAFE — Bienvenue")
        self.geometry("480x720")
        self.resizable(False, False)
        self.configure(fg_color=COULEURS["fond_principal"])
        self.role_choisi = None
        self._build_ui()

    def _build_ui(self):
        ajouter_banniere_pub(self)  # PUB au démarrage

        try:
            img = ctk.CTkImage(light_image=Image.open(LOGO_PATH), dark_image=Image.open(LOGO_PATH), size=(110, 110))
            ctk.CTkLabel(self, image=img, text="").pack(pady=(60, 10))
        except:
            ctk.CTkLabel(self, text="⚕/💊", font=("Segoe UI", 48)).pack(pady=(60, 10))

        ctk.CTkLabel(self, text="MEDSAFE", font=("Segoe UI", 28, "bold"), text_color=COULEURS["fond_entete"]).pack()
        ctk.CTkLabel(self, text="Sélectionnez votre profil", font=("Segoe UI", 14),
                     text_color=COULEURS["texte_gris"]).pack(pady=(5, 40))

        # Bouton Médecin
        btn_med = ctk.CTkButton(self, text="👨‍⚕️ Espace Médecin", height=60, font=("Segoe UI", 16, "bold"),
                                fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
                                command=lambda: self.selectionner_role("medecin"))
        btn_med.pack(fill="x", padx=40, pady=10)

        # Bouton Pharmacien
        btn_phar = ctk.CTkButton(self, text="💊 Espace Pharmacie", height=60, font=("Segoe UI", 16, "bold"),
                                 fg_color=COULEURS["fond_entete"], hover_color="#1A4A40",
                                 command=lambda: self.selectionner_role("pharmacien"))
        btn_phar.pack(fill="x", padx=40, pady=10)

    def selectionner_role(self, role):
        self.role_choisi = role
        self.destroy()


# =========================================================
# 2. FENÊTRE DE CONNEXION / INSCRIPTION UNIFIÉE
# =========================================================
class LoginUnifiedWindow(ctk.CTk):
    def __init__(self, role):
        super().__init__()
        self.role = role
        titre = "Espace Médecin" if role == "medecin" else "Espace Pharmacie"
        self.title(f"MEDSAFE — Authentification ({titre})")
        self.geometry("480x720")
        self.resizable(False, False)
        self.configure(fg_color=COULEURS["fond_principal"])
        self.connexion_reussie = False
        self.user_data = None

        self.pub_frame = ajouter_banniere_pub(self)  # PUB
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        self.afficher_login()

    def nettoyer(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def afficher_login(self):
        self.nettoyer()
        titre_str = "Espace Médecin" if self.role == "medecin" else "Portail Pharmacie"

        ctk.CTkLabel(self.content_frame, text="MEDSAFE", font=("Segoe UI", 28, "bold"),
                     text_color=COULEURS["fond_entete"]).pack(pady=(40, 0))
        ctk.CTkLabel(self.content_frame, text=titre_str, font=("Segoe UI", 13), text_color=COULEURS["texte_gris"]).pack(
            pady=(2, 28))

        outer, card = creer_carte(self.content_frame)
        outer.pack(padx=40, fill="x")

        ctk.CTkLabel(card, text="Connexion", font=("Segoe UI", 15, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(20, 12))

        ph_email = "Adresse email" if self.role == "medecin" else "Email de la pharmacie"
        self.entry_email = ctk.CTkEntry(card, placeholder_text=ph_email, height=44, corner_radius=10,
                                        fg_color=COULEURS["fond_input"])
        self.entry_email.pack(fill="x", padx=24, pady=6)

        self.entry_mdp = ctk.CTkEntry(card, placeholder_text="Mot de passe", show="●", height=44, corner_radius=10,
                                      fg_color=COULEURS["fond_input"])
        self.entry_mdp.pack(fill="x", padx=24, pady=6)

        ctk.CTkButton(card, text="Se connecter", height=46, fg_color=COULEURS["vert_primaire"],
                      hover_color=COULEURS["vert_clair"],
                      font=FONT_BTN, command=self.verifier_login).pack(fill="x", padx=24, pady=(14, 20))

        lien = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        lien.pack(pady=16)
        ctk.CTkLabel(lien, text="Pas encore de compte ?", font=FONT_PETIT, text_color=COULEURS["texte_gris"]).pack(
            side="left")
        ctk.CTkButton(lien, text=" S'inscrire", fg_color="transparent", text_color=COULEURS["vert_primaire"],
                      font=("Segoe UI", 11, "bold"), command=self.afficher_inscription).pack(side="left")

    def afficher_inscription(self):
        self.nettoyer()
        titre_reg = "Nouveau compte médecin" if self.role == "medecin" else "Inscrire une pharmacie"
        ctk.CTkLabel(self.content_frame, text=titre_reg, font=("Segoe UI", 18, "bold"),
                     text_color=COULEURS["fond_entete"]).pack(pady=(40, 18))

        outer, card = creer_carte(self.content_frame)
        outer.pack(padx=40, fill="x")

        if self.role == "medecin":
            champs = [("reg_nom", "Nom complet (ex : Dr. Benali)", False), ("reg_spec", "Spécialité", False)]
        else:
            champs = [("reg_nom", "Nom du pharmacien", False), ("reg_spec", "Nom de la pharmacie", False)]

        champs += [("reg_email", "Adresse email", False), ("reg_mdp", "Mot de passe", True)]

        for attr, ph, is_pass in champs:
            e = ctk.CTkEntry(card, placeholder_text=ph, height=42, corner_radius=10, fg_color=COULEURS["fond_input"],
                             show="●" if is_pass else "")
            e.pack(fill="x", padx=24, pady=5)
            setattr(self, attr, e)

        ctk.CTkButton(card, text="Créer le compte", height=44, fg_color=COULEURS["vert_primaire"], font=FONT_BTN,
                      command=self.enregistrer_utilisateur).pack(fill="x", padx=24, pady=(12, 20))

        ctk.CTkButton(self.content_frame, text="← Retour", fg_color="transparent", text_color=COULEURS["texte_gris"],
                      font=FONT_PETIT, command=self.afficher_login).pack(pady=8)

    def verifier_login(self):
        email, mdp = self.entry_email.get(), self.entry_mdp.get()
        table = "medecins" if self.role == "medecin" else "pharmaciens"
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(f"SELECT * FROM {table} WHERE email = ? AND mot_de_passe = ?", (email, mdp))
            user = c.fetchone()
            conn.close()
            if user:
                self.user_data = user
                self.connexion_reussie = True
                self.destroy()
            else:
                messagebox.showerror("Erreur", "Identifiants incorrects.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Base de données : {e}")

    def enregistrer_utilisateur(self):
        nom, spec, email, mdp = self.reg_nom.get(), self.reg_spec.get(), self.reg_email.get(), self.reg_mdp.get()
        if not nom or not email or not mdp:
            messagebox.showwarning("Erreur", "Remplissez tous les champs.")
            return
        table = "medecins" if self.role == "medecin" else "pharmaciens"
        col2 = "specialite" if self.role == "medecin" else "pharmacie"
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(f"INSERT INTO {table} (nom, {col2}, email, mot_de_passe) VALUES (?, ?, ?, ?)",
                      (nom, spec, email, mdp))
            conn.commit()
            conn.close()
            messagebox.showinfo("Succès", "Compte créé ! Connectez-vous.")
            self.afficher_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Cet email existe déjà.")


# =========================================================
# 3. TABLEAU DE BORD MÉDECIN
# =========================================================
class DashboardMedecin(ctk.CTk):
    def __init__(self, medecin_connecte):
        super().__init__()
        self.medecin_info = medecin_connecte
        self.title("MEDSAFE — Espace Médecin")
        self.geometry("1240x820")
        self.configure(fg_color=COULEURS["fond_principal"])

        ajouter_banniere_pub(self)  # PUB

        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COULEURS["fond_sidebar"])
        self.sidebar.pack(side="left", fill="y")
        self.zone_contenu = ctk.CTkScrollableFrame(self, fg_color=COULEURS["fond_principal"], corner_radius=0)
        self.zone_contenu.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(self.sidebar, text="MEDSAFE\nCabinet Médical", font=("Segoe UI", 16, "bold"),
                     text_color=COULEURS["teal_doux"]).pack(pady=40)
        creer_separateur(self.sidebar, "#1A3D38")

        for icone, label, cmd in [("👤", "Profil", self.afficher_profil), ("🗂", "Patients", self.afficher_malades),
                                  ("📝", "Ordonnance", self.afficher_ordonnance)]:
            ctk.CTkButton(self.sidebar, text=f" {icone} {label}", fg_color="transparent", anchor="w", font=FONT_NORMAL,
                          command=cmd).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(self.sidebar, text="Déconnexion", fg_color=COULEURS["danger"], command=self.destroy).pack(
            side="bottom", pady=20, padx=20, fill="x")
        self.afficher_profil()

    def nettoyer_contenu(self):
        for w in self.zone_contenu.winfo_children(): w.destroy()

    def afficher_profil(self):
        self.nettoyer_contenu()
        ctk.CTkLabel(self.zone_contenu, text=f"Dr. {self.medecin_info[1]}", font=FONT_TITRE).pack(pady=30)
        ctk.CTkLabel(self.zone_contenu,
                     text="Bienvenue dans votre espace médecin.\nUtilisez le menu de gauche pour gérer vos patients.",
                     font=FONT_NORMAL).pack()

    def afficher_malades(self):
        self.nettoyer_contenu()
        ctk.CTkLabel(self.zone_contenu, text="Gestion des Patients", font=FONT_TITRE).pack(pady=30)
        btn = ctk.CTkButton(self.zone_contenu, text="+ Ajouter un patient",
                            command=lambda: messagebox.showinfo("Info", "Module d'ajout en développement"))
        btn.pack()

    def afficher_ordonnance(self):
        self.nettoyer_contenu()
        ctk.CTkLabel(self.zone_contenu, text="Rédaction d'ordonnance", font=FONT_TITRE).pack(pady=30)
        txt = ctk.CTkTextbox(self.zone_contenu, height=300, width=600)
        txt.pack(pady=10)
        ctk.CTkButton(self.zone_contenu, text="Exporter",
                      command=lambda: messagebox.showinfo("Info", "Export en cours...")).pack()


# =========================================================
# 4. TABLEAU DE BORD PHARMACIEN
# =========================================================
class DashboardPharmacien(ctk.CTk):
    def __init__(self, pharmacien_connecte):
        super().__init__()
        self.pharm_info = pharmacien_connecte
        self.title("MEDSAFE — Espace Pharmacie")
        self.geometry("1240x820")
        self.configure(fg_color=COULEURS["fond_principal"])

        ajouter_banniere_pub(self)  # PUB

        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COULEURS["fond_sidebar"])
        self.sidebar.pack(side="left", fill="y")
        self.zone_contenu = ctk.CTkScrollableFrame(self, fg_color=COULEURS["fond_principal"], corner_radius=0)
        self.zone_contenu.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(self.sidebar, text="MEDSAFE\nPharmacie", font=("Segoe UI", 16, "bold"),
                     text_color=COULEURS["teal_doux"]).pack(pady=40)
        creer_separateur(self.sidebar, "#1A3D38")

        for icone, label, cmd in [("👤", "Profil", self.afficher_profil),
                                  ("📥", "Contrôle Ordo", self.afficher_controle_ordo),
                                  ("💊", "Stocks", self.afficher_stock)]:
            ctk.CTkButton(self.sidebar, text=f" {icone} {label}", fg_color="transparent", anchor="w", font=FONT_NORMAL,
                          command=cmd).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(self.sidebar, text="Déconnexion", fg_color=COULEURS["danger"], command=self.destroy).pack(
            side="bottom", pady=20, padx=20, fill="x")
        self.afficher_profil()

    def nettoyer_contenu(self):
        for w in self.zone_contenu.winfo_children(): w.destroy()

    def afficher_profil(self):
        self.nettoyer_contenu()
        ctk.CTkLabel(self.zone_contenu, text=f"Pharmacie {self.pharm_info[2]}", font=FONT_TITRE).pack(pady=30)
        ctk.CTkLabel(self.zone_contenu,
                     text="Bienvenue dans votre espace pharmacie.\nVérifiez les ordonnances et gérez vos stocks.",
                     font=FONT_NORMAL).pack()

    def afficher_controle_ordo(self):
        self.nettoyer_contenu()
        ctk.CTkLabel(self.zone_contenu, text="Vérificateur d'Interactions", font=FONT_TITRE).pack(pady=30)
        ctk.CTkEntry(self.zone_contenu, placeholder_text="Entrez les médicaments...", width=400).pack(pady=10)
        ctk.CTkButton(self.zone_contenu, text="Analyser les risques", fg_color=COULEURS["danger"],
                      hover_color="#A93226").pack()

    def afficher_stock(self):
        self.nettoyer_contenu()
        ctk.CTkLabel(self.zone_contenu, text="Gestion des Stocks", font=FONT_TITRE).pack(pady=30)
        ctk.CTkButton(self.zone_contenu, text="+ Ajouter un médicament").pack()


# =========================================================
# LANCEUR PRINCIPAL
# =========================================================
def demarrer_application():
    # 1. Sélection du profil
    app_choix = ChoixProfessionWindow()
    app_choix.mainloop()

    # Si l'utilisateur a fermé la fenêtre sans choisir
    if not app_choix.role_choisi:
        return

    # 2. Authentification selon le rôle choisi
    app_login = LoginUnifiedWindow(app_choix.role_choisi)
    app_login.mainloop()

    # 3. Lancement du bon tableau de bord
    if app_login.connexion_reussie:
        if app_login.role == "medecin":
            dash = DashboardMedecin(app_login.user_data)
        else:
            dash = DashboardPharmacien(app_login.user_data)
        dash.mainloop()


if __name__ == "__main__":
    demarrer_application()