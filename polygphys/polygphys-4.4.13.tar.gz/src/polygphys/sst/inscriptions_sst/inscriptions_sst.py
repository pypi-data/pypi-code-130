# -*- coding: utf-8 -*-
"""Transmettre les nouvelles inscriptions au SIMDUT."""

# Bibliothèque standard
from datetime import datetime
from pathlib import Path
import time

# Bibliothèque PIPy
import pandas as pd
import schedule

# Bibliothèques maison
from polygphys.outils.reseau import OneDrive
from polygphys.outils.reseau.msforms import MSFormConfig, MSForm
from polygphys.outils.reseau.courriel import Courriel



class SSTSIMDUTInscriptionConfig(MSFormConfig):

    def default(self):
        return (Path(__file__).parent / 'inscription.cfg').open().read()

class SSTSIMDUTInscriptionForm(MSForm):

    def nettoyer(self, cadre):
        cadre = self.convertir_champs(cadre)
        return cadre.loc[:, ['date', 'Prénom', 'Nom', 'Courriel',
                             'Matricule', 'Département', 'Langue',
                             'Statut', 'Professeur ou supérieur immédiat']]

    def action(self, cadre):
        print(f'Mise à jour {datetime.now()}...')
        try:
            destinataire = self.config.get('courriel', 'destinataire')
            pièces_jointes = []
            message = 'Bonjour! Il n\'y a pas eu de nouvelles inscriptions cette semaine. Bonne journée!'
            html = f'<p>{message}</p>'

            if not cadre.empty:
                fichier_temp = Path('nouvelles_entrées.xlsx')
                with pd.ExcelWriter(str(fichier_temp)) as excel_temp:
                    français = cadre.loc[cadre.Langue == 'Français', :]
                    english = cadre.loc[cadre.Langue == 'English', :]
                    français.to_excel(excel_temp, 'Français')
                    english.to_excel(excel_temp, 'English')
                pièces_jointes.append(fichier_temp)

                #destinataire = destinataire\
                #   + ','\
                #       + self.config.get('courriel', 'superviseur')
                message = 'Bonjour! Voici les nouvelles inscriptions à faire pour le SIMDUT. Bonne journée!'
                html = f'<p>{message}</p>{cadre.to_html()}'
        except Exception as e:
            message = f'L\'erreur {e} s\'est produite.'
            html = f'<p>{message}</p>'

        courriel = Courriel(destinataire,
                            self.config.get('courriel', 'expéditeur'),
                            self.config.get('courriel', 'objet'),
                            message,
                            html,
                            pièces_jointes=pièces_jointes)
        courriel.envoyer(self.config.get('courriel', 'serveur'))

def main():
        chemin_config = Path('~').expanduser() / 'simdut.cfg'
        config = SSTSIMDUTInscriptionConfig(chemin_config)

        dossier = OneDrive('',
                           config.get('onedrive', 'organisation'),
                           config.get('onedrive', 'sous-dossier'),
                           partagé=True)
        fichier = dossier / config.get('formulaire', 'nom')
        config.set('formulaire', 'chemin', str(fichier))

        formulaire = SSTSIMDUTInscriptionForm(config)

        schedule.every().friday.at('13:00').do(formulaire.mise_à_jour)

        formulaire.mise_à_jour()
        try:
            print('On commence...')
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print('Fin.')

if __name__ == '__main__':
    main()
