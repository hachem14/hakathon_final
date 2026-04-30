"""
safe_button.py — Importer EN PREMIER dans main.py.

Corrige définitivement :
    invalid command name "XXXXXXX_click_animation"
    invalid command name "XXXXXXX_click_animation_vide"

La vraie cause : CTkButton._on_leave() appelle
    self.after(delay, self._click_animation)
Ce `after()` enregistre un callback nommé d'après l'adresse mémoire
du widget. Si la fenêtre est détruite/cachée avant que le délai
expire, Tkinter essaie d'exécuter un widget qui n'existe plus → erreur.

Solution : on surcharge `after()` sur CTkButton pour intercepter
et ignorer tout appel lié à _click_animation.
"""

import customtkinter as ctk


_original_after = ctk.CTkButton.after  # type: ignore


def _safe_after(self, ms, func=None, *args):
    """
    Surcharge de CTkButton.after() :
    - Si le callback est lié à l'animation de clic → on l'ignore
    - Sinon → comportement normal
    """
    if func is not None:
        name = getattr(func, "__name__", "")
        if "click_animation" in name:
            return "blocked"   # retourne un ID factice, ne planifie rien
    return _original_after(self, ms, func, *args)


# Patch appliqué sur la CLASSE → valable pour tous les CTkButton
# de toute l'application (dashboards inclus) sans les modifier
ctk.CTkButton.after = _safe_after