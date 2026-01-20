# DNS Server Manager

Un server DNS completo con pannello di gestione grafico per Windows, sviluppato con PySide6.

## Caratteristiche

### Funzionalità del Server DNS

- **Server DNS UDP completo**: Implementazione nativa del protocollo DNS
- **Supporto per record multipli**: A, AAAA, CNAME, MX, TXT, NS, SOA, PTR
- **Gestione connessioni multiple**: Supporto per query simultanee
- **Configurazione flessibile**: Porta, indirizzo di bind, timeout personalizzabili
- **Logging dettagliato**: Tracciamento completo delle query e risposte

### Interfaccia Grafica

- **Pannello di gestione intuitivo**: Interfaccia moderna con PySide6
- **Gestione record DNS**: Aggiungi, modifica, elimina record DNS
- **Monitoraggio in tempo reale**: Statistiche e metriche del server
- **Configurazione grafica**: Impostazioni del server tramite interfaccia
- **Visualizzazione log**: Logs in tempo reale con filtri e export

### Sicurezza e Affidabilità

- **Validazione input**: Controllo rigoroso dei record DNS
- **Gestione errori**: Robusta gestione delle eccezioni
- **Logging completo**: Tracciamento di tutte le attività
- **Threading sicuro**: Gestione concorrente delle query

## Installazione

### Prerequisiti

- Python 3.8 o superiore
- Windows 10/11 (raccomandato)
- Privilegi di amministratore (per la porta 53)

### Installazione Automatica

```bash
# Clona il repository
git clone https://github.com/Nsfr750/dns-server-manager.git
cd dns-server-manager

# Installa le dipendenze
pip install -r requirements.txt

# Oppure installa in modalità development
pip install -e .
```

### Installazione Manuale

```bash
# Installa PySide6
pip install PySide6>=6.6.0

# Installa il pacchetto
python setup.py install
```

## Utilizzo

### Avvio del Server

```bash
# Avvia l'interfaccia grafica
python main.py

# Oppure usando lo script installato
dns-server-gui
```

### Configurazione Iniziale

1. **Avvio**: Lancia l'applicazione con privilegi di amministratore
2. **Configurazione**: Usa la tab "Configuration" per impostare porta e indirizzo
3. **Avvio Server**: Clicca "Start Server" per avviare il server DNS
4. **Gestione Record**: Usa la tab "DNS Records" per aggiungere record personalizzati

### Gestione Record DNS

- **Record A**: `example.com -> 192.168.1.1`
- **Record AAAA**: `example.com -> 2001:db8::1`
- **Record CNAME**: `www.example.com -> example.com`
- **Record MX**: `example.com -> 10 mail.example.com`

## Struttura del Progetto

```text
dns-server-manager/
├── main.py                 # Entry point principale
├── core/                   # Funzionalità del server
│   ├── __init__.py
│   ├── dns_server.py       # Server DNS implementation
│   ├── dns_records.py      # DNS record types
│   └── config.py           # Configuration management
├── ui/                     # Interfaccia grafica
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── records_widget.py   # DNS records management
│   ├── stats_widget.py     # Statistics display
│   ├── config_widget.py    # Configuration interface
│   └── logs_widget.py      # Log viewer
├── requirements.txt        # Python dependencies
├── setup.py               # Installation script
└── README.md              # This file
```

## Configurazione

### Impostazioni del Server

- **Porta DNS**: Default 53 (richiede privilegi di amministratore)
- **Bind Address**: Default 0.0.0.0 (tutte le interfacce)
- **Timeout Query**: Default 5 secondi
- **Max Connessioni**: Default 1000

### Logging

- **Livello Log**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **File Log**: dns_server.log
- **Rotazione Log**: Automatica con dimensione massima
- **Preview Log**: Visualizzazione in tempo reale nell'interfaccia

## Utilizzo Avanzato

### Record DNS Supportati

#### Record A (IPv4)

```text
Nome: server.local
Tipo: A
Valore: 192.168.1.100
TTL: 300
```

#### Record AAAA (IPv6)

```text
Nome: server.local
Tipo: AAAA
Valore: 2001:db8::100
TTL: 300
```

#### Record CNAME

```text
Nome: www.local
Tipo: CNAME
Valore: server.local
TTL: 300
```

#### Record MX

```text
Nome: local
Tipo: MX
Valore: 10 mail.local
TTL: 300
```

### Integrazione con Windows

1. **Servizio Windows**: Configura come servizio per avvio automatico
2. **Firewall**: Aggiungi eccezioni per la porta DNS
3. **Configurazione Rete**: Imposta il server DNS primario nelle impostazioni di rete

## Risoluzione Problemi

### Porta 53 Già in Uso

```bash
# Controlla cosa usa la porta 53
netstat -ano | findstr :53

# Ferma il servizio DNS di Windows se necessario
net stop dnscache
```

### Privilegi Insufficienti

- Esegui come Amministratore
- Controlla le policy di sicurezza
- Verifica il firewall di Windows

### Problemi di Rete

- Controlla la configurazione IP
- Verifica le regole del firewall
- Testa con `nslookup` o `dig`

## Sviluppo

### Ambiente di Sviluppo

```bash
# Installa dipendenze di sviluppo
pip install -r requirements.txt
pip install -e .

# Esegui test
python -m pytest tests/

# Formatta codice
black .
```

### Estensioni

- Aggiungi nuovi tipi di record DNS
- Implementa DNSSEC
- Aggiungi interfaccia web
- Supporto per clustering

## Licenza

Questo progetto è distribuito sotto licenza GPLv3. Vedi il file LICENSE per dettagli.

## Supporto

- **Issues**: [GitHub Issues](https://github.com/Nsfr750/issues)
- **Email**: nsfr750@yandex.com
- **Website**: https://www.tuxxle.org
- **Security**: info@tuxxle.org

## Donazioni

Se trovi utile questo progetto, considera una donazione:

- **PayPal**: https://paypal.me/3dmega
- **Monero**: 47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF

---

© Copyright 2024-2026 Nsfr750 - All rights reserved.
