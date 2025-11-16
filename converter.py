import socket
import sys
import mido
import json
import os
import time
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

# --- Globale Einstellungen ---
CONFIG_FILE = 'config.json'
OSC_PORT = 5005
VERBOSE = False
OSC_IP = None
MIDI_PORT_NAME = None
OUTPUT_PORT = None
LANGUAGE = 'en' # Standard: Deutsch

# --- Texte für Sprachauswahl ---
TEXTS = {
    'de': {
        'title': "OSC zu MIDI Konverter Einstellungen",
        'opt1': "Netzwerk Interface (Hören):",
        'opt2': "OSC Port (Hören):",
        'opt3': "MIDI Port (Senden):",
        'opt4': "Verbose/Logging:",
        'opt5': "Sprache/Language:",
        'start': "START Konverter",
        'exit': "Beenden",
        'not_selected': "Noch nicht ausgewählt",
        'on': "An",
        'off': "Aus",
        'choose_opt': "Wählen Sie eine Option (1-7): ",
        'invalid_input': "Ungültige Eingabe. Bitte wählen Sie eine Zahl zwischen 1 und 7.",
        'ip_menu_title': "--- Netzwerk Interface Auswahl ---",
        'ip_input': "Geben Sie die Nummer des Interface ein: ",
        'ip_ok': "OSC-Hören auf IP: **{ip}** (Port: {port})",
        'port_menu_title': "--- OSC Port Ändern (Aktuell: {port}) ---",
        'port_input': "Geben Sie den neuen OSC Port ein (z.B. 8000): ",
        'port_invalid': "Ungültige Portnummer. Bitte eine Zahl zwischen 1024 und 65535 eingeben.",
        'port_ok': "Neuer OSC-Port ist **{port}**.",
        'logging_ok': "Logging ist jetzt **{status}**.",
        'midi_port_fail': "Es wurden keine MIDI Output Ports gefunden. Starten Sie LoopMIDI!",
        'midi_menu_title': "--- MIDI Output Port Auswahl ---",
        'midi_input': "Geben Sie die Nummer des MIDI Output Ports ein: ",
        'midi_port_ok': "MIDI Port **'{name}'** erfolgreich geöffnet.",
        'midi_port_err1': "Fehler beim Öffnen von Port '{name}': {e}",
        'midi_port_err2': "Der Port wird wahrscheinlich von einer anderen Anwendung blockiert.",
        'start_msg': "**Konverter wird gestartet...**",
        'start_err_ip': "Bitte wählen Sie zuerst ein Netzwerk Interface aus (Option 1).",
        'start_err_midi': "MIDI-Port konnte nicht geöffnet oder ausgewählt werden. Überprüfen Sie LoopMIDI.",
        'server_running': "OSC-Server läuft auf UDP: **{ip}:{port}**",
        'midi_sending': "MIDI-Output sendet an: **{name}**",
        'log_status': "Logging:",
        'expected_format': "Zu erwartendes OSC-Format: `/Kanal/Note/Velocity`",
        'stop_info': "Zum Beenden **STRG+C** drücken.",
        'stop_msg': "\nServer wird beendet...",
        'server_err': "\nFehler beim Starten des Servers: {e}",
        'server_hint': "Stellen Sie sicher, dass die IP-Adresse korrekt ist und der Port nicht belegt ist.",
        'resources_freed': "Alle Ressourcen wurden freigegeben.",
        'exit_msg': "Beende das Skript.",
        'settings_loaded': "Letzte Einstellungen geladen.",
        'settings_saved': "Einstellungen gespeichert.",
        'settings_fail_save': "Fehler beim Speichern der Konfiguration: {e}",
        'settings_fail': "Fehler beim Laden der Konfiguration: {e}. Verwende Standardwerte.",
        'midi_loaded_ok': "MIDI Port '{name}' aus Konfiguration geöffnet.",
        'midi_loaded_fail': "MIDI Port '{name}' konnte nicht geöffnet werden. Bitte neu wählen.",
        'osc_recv': "OSC-Nachricht empfangen: {address} {args}",
        'osc_err_format': "Fehler: Falsches OSC-Adressformat: {address}",
        'osc_err_values': "Fehler: Ungültige MIDI-Werte: Kanal={ch}, Note={note}, Velocity={vel}",
        'midi_sent': "-> MIDI Gesendet: {msg}",
        'conv_fail': "Fehler: Konvertierung fehlgeschlagen in {address} mit Werten {args}",
        'unexpected_err': "Ein unerwarteter Fehler ist aufgetreten: {e}",
        'selection_err': "Ungültige Nummer. Bitte erneut versuchen.",
        'selection_err_num': "Ungültige Eingabe. Bitte eine Zahl eingeben."
    },
    'en': {
        'title': "OSC to MIDI Converter Settings",
        'opt1': "Network Interface (Listen):",
        'opt2': "OSC Port (Listen):",
        'opt3': "MIDI Port (Send):",
        'opt4': "Verbose/Logging:",
        'opt5': "Language/Sprache:",
        'start': "START Converter",
        'exit': "Exit",
        'not_selected': "Not selected yet",
        'on': "On",
        'off': "Off",
        'choose_opt': "Select an option (1-7): ",
        'invalid_input': "Invalid input. Please select a number between 1 and 7.",
        'ip_menu_title': "--- Network Interface Selection ---",
        'ip_input': "Enter the number of the interface: ",
        'ip_ok': "OSC listening on IP: **{ip}** (Port: {port})",
        'port_menu_title': "--- Change OSC Port (Current: {port}) ---",
        'port_input': "Enter the new OSC Port (e.g., 8000): ",
        'port_invalid': "Invalid port number. Please enter a number between 1024 and 65535.",
        'port_ok': "New OSC Port is **{port}**.",
        'logging_ok': "Logging is now **{status}**.",
        'midi_port_fail': "No MIDI output ports found. Start LoopMIDI!",
        'midi_menu_title': "--- MIDI Output Port Selection ---",
        'midi_input': "Enter the number of the MIDI Output Port: ",
        'midi_port_ok': "MIDI Port **'{name}'** successfully opened.",
        'midi_port_err1': "Error opening port '{name}': {e}",
        'midi_port_err2': "The port is likely blocked by another application.",
        'start_msg': "**Converter starting...**",
        'start_err_ip': "Please select a network interface first (Option 1).",
        'start_err_midi': "MIDI port could not be opened or selected. Check LoopMIDI.",
        'server_running': "OSC Server running on UDP: **{ip}:{port}**",
        'midi_sending': "MIDI Output sending to: **{name}**",
        'log_status': "Logging:",
        'expected_format': "Expected OSC format: `/Channel/Note/Velocity`",
        'stop_info': "Press **CTRL+C** to stop.",
        'stop_msg': "\nServer shutting down...",
        'server_err': "\nError starting server: {e}",
        'server_hint': "Ensure the IP address is correct and the port is not in use.",
        'resources_freed': "All resources have been released.",
        'exit_msg': "Exiting script.",
        'settings_loaded': "Last settings loaded.",
        'settings_saved': "Settings saved.",
        'settings_fail_save': "Error saving configuration: {e}",
        'settings_fail': "Error loading configuration: {e}. Using default values.",
        'midi_loaded_ok': "MIDI Port '{name}' opened from configuration.",
        'midi_loaded_fail': "MIDI Port '{name}' could not be opened. Please re-select.",
        'osc_recv': "OSC message received: {address} {args}",
        'osc_err_format': "Error: Invalid OSC address format: {address}",
        'osc_err_values': "Error: Invalid MIDI values: Channel={ch}, Note={note}, Velocity={vel}",
        'midi_sent': "-> MIDI Sent: {msg}",
        'conv_fail': "Error: Conversion failed in {address} with values {args}",
        'unexpected_err': "An unexpected error occurred: {e}",
        'selection_err': "Invalid number. Please try again.",
        'selection_err_num': "Invalid input. Please enter a number."
    }
}

# --- Hilfsfunktionen ---

def _(key):
    """Gibt den Text in der aktuellen Sprache zurück."""
    return TEXTS[LANGUAGE][key]

def clear_console():
    """Löscht die Konsole und setzt den Titel des Fensters"""
    if os.name == 'nt':
        os.system('title OSC to MIDI Bridge - V1.0')
        
    os.system('cls' if os.name == 'nt' else 'clear')
    time.sleep(0.05) 

# --- Konfiguration Speichern/Laden ---

def load_settings():
    global OSC_PORT, VERBOSE, OSC_IP, MIDI_PORT_NAME, LANGUAGE
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                settings = json.load(f)
                OSC_PORT = settings.get('osc_port', 5005)
                VERBOSE = settings.get('verbose', False)
                OSC_IP = settings.get('osc_ip')
                MIDI_PORT_NAME = settings.get('midi_port_name')
                LANGUAGE = settings.get('language', 'de')
                print(_('settings_loaded'))
        except Exception as e:
            print(_('settings_fail').format(e=e))

def save_settings():
    global LANGUAGE
    settings = {
        'osc_port': OSC_PORT,
        'verbose': VERBOSE,
        'osc_ip': OSC_IP,
        'midi_port_name': MIDI_PORT_NAME,
        'language': LANGUAGE
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        if VERBOSE:
            print(_('settings_saved'))
    except Exception as e:
        print(_('settings_fail_save').format(e=e))

# --- OSC Handler Funktion ---

def osc_to_midi_handler(address, *args):
    global OUTPUT_PORT, VERBOSE

    if VERBOSE:
        print(_('osc_recv').format(address=address, args=args))

    try:
        parts = address.strip('/').split('/')
        if len(parts) != 3:
            if VERBOSE:
                print(_('osc_err_format').format(address=address))
            return

        midi_channel_1_16 = int(parts[0])
        midi_note = int(parts[1])
        velocity = int(parts[2])

        if not (1 <= midi_channel_1_16 <= 16 and 0 <= midi_note <= 127 and 0 <= velocity <= 127):
            if VERBOSE:
                print(_('osc_err_values').format(ch=midi_channel_1_16, note=midi_note, vel=velocity))
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
                print(_('midi_sent').format(msg=msg))

    except ValueError:
        if VERBOSE:
            print(_('conv_fail').format(address=address, args=args))
    except Exception as e:
        print(_('unexpected_err').format(e=e))

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
    global OSC_IP, VERBOSE, OUTPUT_PORT, OSC_PORT, MIDI_PORT_NAME, LANGUAGE

    while True:
        clear_console()
        midi_status = MIDI_PORT_NAME if MIDI_PORT_NAME else _('not_selected')
        log_status = _('on') if VERBOSE else _('off')
        lang_status = 'Deutsch (DE)' if LANGUAGE == 'de' else 'English (EN)'
        
        print("\n" + "="*50)
        print(_('title'))
        print("="*50)
        print(f"1. {_('opt1')}  {'**' + (OSC_IP if OSC_IP else _('not_selected')) + '**'}")
        print(f"2. {_('opt2')}            **{OSC_PORT}**")
        print(f"3. {_('opt3')}          **{midi_status}**")
        print(f"4. {_('opt4')}             **{log_status}**")
        print(f"5. {_('opt5')}             **{lang_status}**")
        print(f"\n6. {_('start')}")
        print(f"7. {_('exit')}")
        print("="*50)

        choice = input(_('choose_opt'))

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
            print(_('logging_ok').format(status=_('on') if VERBOSE else _('off')))
            time.sleep(1)
            save_settings()
        elif choice == '5':
            LANGUAGE = select_language()
            save_settings()
        elif choice == '6':
            if OSC_IP and OUTPUT_PORT:
                clear_console()
                print(_('start_msg'))
                save_settings()
                start_server()
                break
            elif not OSC_IP:
                print(_('start_err_ip'))
                time.sleep(2)
            elif not OUTPUT_PORT:
                 print(_('start_err_midi'))
                 time.sleep(2)
        elif choice == '7':
            print(_('exit_msg'))
            sys.exit(0)
        else:
            print(_('invalid_input'))
            time.sleep(1)

def select_language():
    global LANGUAGE
    while True:
        clear_console()
        print("\n--- Language Selection ---")
        print("  [1] Deutsch (DE)")
        print("  [2] English (EN)")
        print("--------------------------")
        
        lang_choice = input("Select Language/Sprache wählen (1/2): ")
        
        if lang_choice == '1':
            return 'de'
        elif lang_choice == '2':
            return 'en'
        else:
            print("Invalid choice. Ungültige Auswahl.")
            time.sleep(1)


def select_network_interface():
    interfaces = get_network_interfaces()
    while True:
        clear_console()
        print(f"\n{_('ip_menu_title')}")
        for i, ip in enumerate(interfaces):
            print(f"  [{i+1}] {ip}")
        print("----------------------------------")

        try:
            selection = int(input(_('ip_input')))
            if 1 <= selection <= len(interfaces):
                selected_ip = interfaces[selection - 1].split(' ')[0]
                print(_('ip_ok').format(ip=selected_ip, port=OSC_PORT))
                time.sleep(1)
                return selected_ip
            else:
                print(_('selection_err'))
                time.sleep(1)
        except ValueError:
            print(_('selection_err_num'))
            time.sleep(1)
            
def change_osc_port():
    global OSC_PORT
    
    while True:
        clear_console()
        print(_('port_menu_title').format(port=OSC_PORT))
        new_port_str = input(_('port_input'))
        
        try:
            new_port = int(new_port_str)
            if 1024 <= new_port <= 65535:
                OSC_PORT = new_port
                print(_('port_ok').format(port=OSC_PORT))
                time.sleep(1)
                return
            else:
                print(_('port_invalid'))
                time.sleep(1)
        except ValueError:
            print(_('selection_err_num'))
            time.sleep(1)


def select_midi_port():
    global OUTPUT_PORT, MIDI_PORT_NAME

    output_names = mido.get_output_names()

    if OUTPUT_PORT:
        OUTPUT_PORT.close()
        OUTPUT_PORT = None
        MIDI_PORT_NAME = None

    if not output_names:
        print(f"\n{_('midi_port_fail')}")
        time.sleep(2)
        return
        
    while True:
        clear_console()
        print(f"\n{_('midi_menu_title')}")
        for i, name in enumerate(output_names):
            print(f"  [{i+1}] {name}")
        print("--------------------------------")

        try:
            selection = int(input(_('midi_input')))
            if 1 <= selection <= len(output_names):
                selected_name = output_names[selection - 1]
                try:
                    OUTPUT_PORT = mido.open_output(selected_name)
                    MIDI_PORT_NAME = selected_name
                    print(_('midi_port_ok').format(name=MIDI_PORT_NAME))
                    time.sleep(1)
                    return
                except Exception as e:
                    print(_('midi_port_err1').format(name=selected_name, e=e))
                    print(_('midi_port_err2'))
                    time.sleep(2)
                    return
            else:
                print(_('selection_err'))
                time.sleep(1)
        except ValueError:
            print(_('selection_err_num'))
            time.sleep(1)

# --- Server Start ---

def start_server():
    global OSC_IP, OSC_PORT, VERBOSE
    
    dispatcher = Dispatcher()
    dispatcher.map("/*/*/*", osc_to_midi_handler)
    
    try:
        server = BlockingOSCUDPServer((OSC_IP, OSC_PORT), dispatcher)
        print("-" * 50)
        print(_('server_running').format(ip=OSC_IP, port=OSC_PORT))
        print(_('midi_sending').format(name=MIDI_PORT_NAME))
        print(f"{_('log_status')} **{_('on') if VERBOSE else _('off')}**")
        print(_('expected_format'))
        print(_('stop_info'))
        print("-" * 50)
        
        server.serve_forever() 

    except KeyboardInterrupt:
        print(_('stop_msg'))
    except Exception as e:
        print(_('server_err').format(e=e))
        print(_('server_hint'))
    finally:
        if 'server' in locals() and server:
            server.shutdown()
        if OUTPUT_PORT:
            OUTPUT_PORT.close()
        print(_('resources_freed'))
        time.sleep(1)


# --- Skript Start ---
if __name__ == "__main__":
    load_settings()
    
    # Versuche den MIDI-Port aus den geladenen Einstellungen zu öffnen
    if MIDI_PORT_NAME:
        try:
            OUTPUT_PORT = mido.open_output(MIDI_PORT_NAME)
            print(_('midi_loaded_ok').format(name=MIDI_PORT_NAME))
            time.sleep(1)
        except:
            OUTPUT_PORT = None
            print(_('midi_loaded_fail').format(name=MIDI_PORT_NAME))
            time.sleep(2)
            MIDI_PORT_NAME = None

    # Falls kein Port aus der Konfig geladen/geöffnet werden konnte, starte die manuelle Auswahl
    if not MIDI_PORT_NAME:
        select_midi_port()

    print_settings_menu()