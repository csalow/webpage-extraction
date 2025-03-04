import requests
from bs4 import BeautifulSoup
import justext
import argparse
import sys
import pyperclip

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f'Fehler: {message}\n')
        self.print_help()
        sys.exit(2)

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Versuch, den Haupttext mit jusText zu extrahieren
        paragraphs = justext.justext(response.content, justext.get_stoplist("German"))
        main_text = "\n".join(p.text for p in paragraphs if not p.is_boilerplate)
        
        # Falls jusText nichts findet, Rückfall auf BeautifulSoup
        if not main_text.strip():
            soup = BeautifulSoup(response.content, 'html.parser')
            main_text = soup.get_text()
        
        return main_text
    except requests.exceptions.RequestException as e:
        return f"Ein Fehler ist aufgetreten: {e}"

def main():
    parser = MyParser(
        description='Extrahiere den Haupttext einer Webseite.',
        epilog='Beispiel: python scriptname.py https://www.beispiel.de -o ausgabe.txt --xclip',
        add_help=True
    )
    parser.add_argument('url', nargs='?', help='URL der Webseite')
    parser.add_argument('-o', '--output', help='Dateiname zum Speichern des extrahierten Textes')
    parser.add_argument('--xclip', action='store_true', help='Kopiere den extrahierten Text in die Zwischenablage')
    parser.add_argument('--version', action='version', version='%(prog)s 1.2')

    args = parser.parse_args()

    if not args.url:
        parser.print_help()
        sys.exit(1)

    text = extract_text_from_url(args.url)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as file:
                file.write(text)
            print(f"Der extrahierte Text wurde in '{args.output}' gespeichert.")
        except IOError as e:
            print(f"Fehler beim Schreiben in die Datei: {e}")
    
    if args.xclip:
        pyperclip.copy(text)
        print("Der extrahierte Text wurde in die Zwischenablage kopiert.")
    
    if not args.output and not args.xclip:
        print(text)

if __name__ == '__main__':
    main()
