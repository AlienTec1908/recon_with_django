SCAN_CHECKS = {
    "Feroxbuster - Common Directories": "check_web_scanner_conditions",
    "Feroxbuster - API Endpoints": "check_web_scanner_conditions",
    "Feroxbuster - Config Files": "check_web_scanner_conditions",
    "Feroxbuster - Framework Signatures": "check_web_scanner_conditions",
    "Nikto Scan": "check_web_scanner_conditions",
    "Curl - HTTP Headers": "check_web_scanner_conditions",
    "Curl - Cookie Jar": "check_web_scanner_conditions",
    "Curl - Allowed Methods": "check_web_scanner_conditions",
}

SCANS_TO_RUN = [
    {
        "id": "ipv6",
        "name": "IPv6 Discovery Scan",
        "command": ["ping6", "-c", "3", "ff02::1"]
    },
    {
        "id": "curl_headers",
        "name": "Curl - HTTP Headers",
        "command": ["curl", "-I", "-v", "-L", "{URL}", "-s"]
    },
    {
        "id": "curl_cookies",
        "name": "Curl - Cookie Jar",
        "command": [
            "curl",
            "-s",
            "-L",
            "-c",
            "logs/{TARGET}/cookies.txt",
            "-o",
            "/dev/null",
            "{URL}"
        ]
    },
    {
        "id": "curl_methods",
        "name": "Curl - Allowed Methods",
        "command": ["curl", "-X", "OPTIONS", "-I", "-L", "{URL}", "-s"]
    },
    {
        "id": "nmap_full",
        "name": "Nmap Full Scan",
        "command": [
            "nmap",
            "-sS",
            "-sC",
            "-sV",
            "-p-",
            "-Pn",
            "--min-rate",
            "5000",
            "{TARGET}",
            "-oX",
            "logs/{TARGET}/full.xml"
        ]
    },
    {
        "id": "nmap_udp",
        "name": "Nmap UDP Scan",
        "command": [
            "nmap",
            "-sU",
            "--top-ports",
            "1000",
            "-Pn",
            "--min-rate",
            "5000",
            "{TARGET}",
            "-oX",
            "logs/{TARGET}/udp.xml"
        ]
    },
    {
        "id": "nikto",
        "name": "Nikto Scan",
        "command": [
            "nikto",
            "-h",
            "{URL}",
            "-nointeractive",
            "-Format",
            "json",
            "-output",
            "logs/{TARGET}/nikto.json"
        ]
    },
    {
        "id": "ferox_common",
        "name": "Feroxbuster - Common Directories",
        "command": [
            "feroxbuster",
            "-u", "{URL}",
            "-w", "/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-big.txt",
            "-k", "--json", "--silent",
            "--output", "logs/{TARGET}/ferox_common.json"
        ]
    },
    {
        "id": "ferox_apis",
        "name": "Feroxbuster - API Endpoints",
        "command": [
            "feroxbuster",
            "-u", "{URL}",
            "-w", "/usr/share/seclists/Discovery/Web-Content/api/all.txt",
            "-k", "--json", "--silent",
            "--output", "logs/{TARGET}/ferox_apis.json"
        ]
    },
    {
        "id": "ferox_configs",
        "name": "Feroxbuster - Config Files",
        "command": [
            "feroxbuster",
            "-u", "{URL}",
            "-w", "/usr/share/seclists/Discovery/Web-Content/common-and-large-web-directories/config-files.txt",
            "-k", "--json", "--silent",
            "--output", "logs/{TARGET}/ferox_configs.json"
        ]
    },
    {
        "id": "ferox_frameworks",
        "name": "Feroxbuster - Framework Signatures",
        "command": [
            "feroxbuster",
            "-u", "{URL}",
            "-w", "/usr/share/seclists/Discovery/Web-Content/framework-signatures.txt",
            "-k", "--json", "--silent",
            "--output", "logs/{TARGET}/ferox_frameworks.json"
        ]
    }
]
