# Bot de Discord per a Medalles de Pokémon

## Descripció

Aquest projecte és un bot de Discord desenvolupat en Python que permet als usuaris registrar i gestionar medalles basades en tipus de Pokémon. A més, ofereix funcionalitats addicionals com la gestió de rols, l'exportació de dades a Google Sheets i la moderació de missatges.

## Característiques

- Registre i gestió de medalles associades a rols.
- Exportació de medalles a Google Sheets.
- Comandes per a moderació, com mutear i desmutear usuaris.
- Sistema de ranking per als usuaris amb més medalles.
- Maneig d'errors i missatges informatius.

## Requeriments

- Python 3.8 o superior.
- Una base de dades SQLite per a l'emmagatzematge de medalles i usuaris.
- Una aplicació de Discord registrada amb un token de bot.
- Llibreries requerides (instal·lables amb pip):
  ```sh
  pip install -r requirements.txt
  ```
## Comandes Principals

- `Dam med <medalla> <replay>` → Registra una medalla.
- `Dam verMeds` → Mostra totes les medalles d'un usuari.
- `Dam eliminarMeds` → Elimina totes les medalles registrades d'un usuari.
- `Dam ranking` → Mostra el ranking dels 10 usuaris amb més medalles.
- `Dam exportarMeds` → Exporta les medalles a Google Sheets.
- `Dam mutear <@usuari>` → Muteja un usuari durant un temps determinat.
- `Dam unmute <@usuari>` → Desmuteja un usuari.
- `Dam crearRol <nom_rol>` → Crea un rol nou al servidor.
- `Dam help` → Mostra la llista de comandes disponibles.

## Autor

👤 **[04Pauter]**

