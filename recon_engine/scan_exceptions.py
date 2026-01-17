def check_web_scanner_conditions(port_info_map: dict):
    found_web_ports = []
    for port, data in port_info_map.items():
        service = data.get("service", "").lower()
        status = data.get("status", "")
        
        if status in ("open", "filtered"):
            is_http = "http" in service and "rpc" not in service
            is_ssl = "ssl" in service or "tls" in service
            
            if is_ssl or port in (443, 8443, 4433):
                found_web_ports.append(("https", port))
            elif is_http or port in (80, 8080, 8000, 8888):
                found_web_ports.append(("http", port))

    # Deduplicate in case a port was matched by service and number
    return list(set(found_web_ports))

# Ensure the keys here EXACTLY match the 'name' in SCANS_TO_RUN
SCAN_CHECKS = {
    "Feroxbuster - Common Directories": check_web_scanner_conditions,
    "Feroxbuster - API Endpoints": check_web_scanner_conditions,
    "Feroxbuster - Config Files": check_web_scanner_conditions,
    "Feroxbuster - Framework Signatures": check_web_scanner_conditions,
    "Nikto Scan": check_web_scanner_conditions,
    "Curl - HTTP Headers": check_web_scanner_conditions,
    "Curl - Cookie Jar": check_web_scanner_conditions,
    "Curl - Allowed Methods": check_web_scanner_conditions,
}
