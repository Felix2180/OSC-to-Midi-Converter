import socket
import sys
import mido
import json
import os
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

# --- Globale Einstellungen ---
CONFIG_FILE = 'config.json'
OSC_PORT = 5005
VERBOSE = False
OSC_IP = None
MIDI_PORT_NAME = None
OUTPUT_PORT = None

# --- Konfiguration Speichern/Laden ---

def load_settings():
    """Lädt Einstellungen aus der Konfigurationsdatei."""
    global OSC_PORT, VERBOSE, OSC_IP, MIDI_PORT_NAME
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                settings = json.load(f)
                OSC_PORT = settings.get('osc_port', 5005)
                VERBOSE = settings.get('verbose', False)
                OSC_IP = settings.get('osc_ip')
                MIDI_PORT_NAME = settings.get('midi_port_name')
                print("Letzte Einstellungen geladen.")
        except Exception as e:
            print(f"Fehler beim Laden der Konfiguration: {e}. Verwende Standardwerte.")

def save_settings():
    """Speichert die aktuellen Einstellungen in der Konfigurationsdatei."""
    settings = {
        'osc_port': OSC_PORT,
        'verbose': VERBOSE,
        'osc_ip': OSC_IP,
        'midi_port_name': MIDI_PORT_NAME
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        if VERBOSE:
            print("Einstellungen gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Konfiguration: {e}")

# --- OSC Handler Funktion ---

def osc_to_midi_handler(address, *args):
    global OUTPUT_PORT, VERBOSE

    if VERBOSE:
        print(f"OSC-Nachricht empfangen: {address} {args}")

    try:
        parts = address.strip('/').split('/')
        if len(parts) != 3:
            if VERBOSE:
                print(f"Fehler: Falsches OSC-Adressformat: {address}")
            return

        midi_channel_1_16 = int(parts[0])
        midi_note = int(parts[1])
        velocity = int(parts[2])

        if not (1 <= midi_channel_1_16 <= 16 and 0 <= midi_note <= 127 and 0 <= velocity <= 127):
            if VERBOSE:
                print(f"Fehler: Ungültige MIDI-Werte: Kanal={midi_channel_1_16}, Note={midi_note}, Velocity={velocity}")
            return

        midi_channel_0_15 = midi_channel_1_16 - 1
        msg_type = 'note_on' if velocity > 0 else 'note_off'

        msg = mido.Message(
            msg_type,
            channel=midi_channel_0_15,
            note=midi_note,
            velocity=velocity
        )

        if OUTPUT_PORT:
            OUTPUT_PORT.send(msg)
            if VERBOSE:
                print(f"-> MIDI Gesendet: {msg}")

    except ValueError:
        if VERBOSE:
            print(f"Fehler: Konvertierung fehlgeschlagen in {address} mit Werten {args}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# --- Netzwerk- und Einstellungsfunktionen ---

def get_network_interfaces():
    interfaces = ["127.0.0.1 (localhost)"]
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            ip = info[4][0]
            if ip not in interfaces and not ip.startswith('127.'):
                interfaces.append(ip)

    except socket.gaierror:
        pass
    
    if "0.0.0.0 (Alle Interfaces)" not in interfaces:
         interfaces.append("0.0.0.0 (Alle Interfaces)")
         
    return interfaces

def print_settings_menu():
    global OSC_IP, VERBOSE, OUTPUT_PORT, OSC_PORT, MIDI_PORT_NAME

    while True:
        midi_status = MIDI_PORT_NAME if MIDI_PORT_NAME else 'Noch nicht ausgewählt'
        
        print("\n" + "="*50)
        print("OSC zu MIDI Konverter Einstellungen")
        print("="*50)
        print(f"1. Netzwerk Interface (Hören):  {'**' + (OSC_IP if OSC_IP else 'Noch nicht ausgewählt') + '**'}")
        print(f"2. OSC Port (Hören):            **{OSC_PORT}**")
        print(f"3. MIDI Port (Senden):          **{midi_status}**")
        print(f"4. Verbose/Logging:             **{'An' if VERBOSE else 'Aus'}**")
        print("\n5. START Konverter")
        print("6. Beenden")
        print("="*50)

        choice = input("Wählen Sie eine Option (1-6): ")

        if choice == '1':
            OSC_IP = select_network_interface()
            save_settings()
        elif choice == '2':
            change_osc_port()
            save_settings()
        elif choice == '3':
            select_midi_port()
            save_settings()
        elif choice == '4':
            VERBOSE = not VERBOSE
            print(f"Logging ist jetzt **{'An' if VERBOSE else 'Aus'}**.")
            save_settings()
        elif choice == '5':
            if OSC_IP and OUTPUT_PORT:
                print("\n**Konverter wird gestartet...**")
                save_settings()
                start_server()
                break
            elif not OSC_IP:
                print("Bitte wählen Sie zuerst ein Netzwerk Interface aus (Option 1).")
            elif not OUTPUT_PORT:
                 print("MIDI-Port konnte nicht geöffnet oder ausgewählt werden. Überprüfen Sie LoopMIDI.")
        elif choice == '6':
            print("Beende das Skript.")
            sys.exit(0)
        else:
            print("Ungültige Eingabe. Bitte wählen Sie eine Zahl zwischen 1 und 6.")

def select_network_interface():
    interfaces = get_network_interfaces()
    while True:
        print("\n--- Netzwerk Interface Auswahl ---")
        for i, ip in enumerate(interfaces):
            print(f"  [{i+1}] {ip}")
        print("----------------------------------")

        try:
            selection = int(input("Geben Sie die Nummer des Interface ein: "))
            if 1 <= selection <= len(interfaces):
                selected_ip = interfaces[selection - 1].split(' ')[0]
                print(f"OSC-Hören auf IP: **{selected_ip}** (Port: {OSC_PORT})")
                return selected_ip
            else:
                print("Ungültige Nummer. Bitte erneut versuchen.")
        except ValueError:
            print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
            
def change_osc_port():
    global OSC_PORT
    
    while True:
        print(f"\n--- OSC Port Ändern (Aktuell: {OSC_PORT}) ---")
        new_port_str = input("Geben Sie den neuen OSC Port ein (z.B. 8000): ")
        
        try:
            new_port = int(new_port_str)
            if 1024 <= new_port <= 65535:
                OSC_PORT = new_port
                print(f"Neuer OSC-Port ist **{OSC_PORT}**.")
                return
            else:
                print("Ungültige Portnummer. Bitte eine Zahl zwischen 1024 und 65535 eingeben.")
        except ValueError:
            print("Ungültige Eingabe. Bitte nur Zahlen eingeben.")


def select_midi_port():
    global OUTPUT_PORT, MIDI_PORT_NAME

    output_names = mido.get_output_names()

    if OUTPUT_PORT:
        OUTPUT_PORT.close()
        OUTPUT_PORT = None
        MIDI_PORT_NAME = None

    if not output_names:
        print("\nEs wurden keine MIDI Output Ports gefunden. Starten Sie LoopMIDI!")
        return
        
    while True:
        print("\n--- MIDI Output Port Auswahl ---")
        for i, name in enumerate(output_names):
            print(f"  [{i+1}] {name}")
        print("--------------------------------")

        try:
            selection = int(input("Geben Sie die Nummer des MIDI Output Ports ein: "))
            if 1 <= selection <= len(output_names):
                selected_name = output_names[selection - 1]
                try:
                    OUTPUT_PORT = mido.open_output(selected_name)
                    MIDI_PORT_NAME = selected_name
                    print(f"\nMIDI Port **'{MIDI_PORT_NAME}'** erfolgreich geöffnet.")
                    return
                except Exception as e:
                    print(f"\nFehler beim Öffnen von Port '{selected_name}': {e}")
                    print("Der Port wird wahrscheinlich von einer anderen Anwendung blockiert.")
                    return
            else:
                print("Ungültige Nummer. Bitte erneut versuchen.")
        except ValueError:
            print("Ungültige Eingabe. Bitte eine Zahl eingeben.")

# --- Server Start ---

def start_server():
    global OSC_IP, OSC_PORT, VERBOSE
    
    dispatcher = Dispatcher()
    dispatcher.map("/*/*/*", osc_to_midi_handler)
    
    try:
        server = BlockingOSCUDPServer((OSC_IP, OSC_PORT), dispatcher)
        print("-" * 50)
        print(f"OSC-Server läuft auf UDP: **{OSC_IP}:{OSC_PORT}**")
        print(f"MIDI-Output sendet an: **{MIDI_PORT_NAME}**")
        print(f"Logging: **{'AN' if VERBOSE else 'AUS'}**")
        print("Zu erwartendes OSC-Format: `/Kanal/Note/Velocity`")
        print("Zum Beenden **STRG+C** drücken.")
        print("-" * 50)
        
        server.serve_forever() 

    except KeyboardInterrupt:
        print("\nServer wird beendet...")
    except Exception as e:
        print(f"\nFehler beim Starten des Servers: {e}")
        print("Stellen Sie sicher, dass die IP-Adresse korrekt ist und der Port nicht belegt ist.")
    finally:
        if 'server' in locals() and server:
            server.shutdown()
        if OUTPUT_PORT:
            OUTPUT_PORT.close()
        print("Alle Ressourcen wurden freigegeben.")
        save_settings()

# --- Skript Start ---
if __name__ == "__main__":
    load_settings()
    
    # Versuche den MIDI-Port aus den geladenen Einstellungen zu öffnen
    if MIDI_PORT_NAME:
        try:
            OUTPUT_PORT = mido.open_output(MIDI_PORT_NAME)
            print(f"MIDI Port '{MIDI_PORT_NAME}' aus Konfiguration geöffnet.")
        except:
            OUTPUT_PORT = None
            print(f"MIDI Port '{MIDI_PORT_NAME}' konnte nicht geöffnet werden. Bitte neu wählen.")
            MIDI_PORT_NAME = None

    # Falls kein Port aus der Konfig geladen/geöffnet werden konnte, starte die manuelle Auswahl
    if not MIDI_PORT_NAME:
        select_midi_port()

    print_settings_menu()