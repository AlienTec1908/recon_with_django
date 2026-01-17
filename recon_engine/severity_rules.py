def get_severity(category, value):
    value_lower = str(value).lower()
    category_lower = category.lower()

    if category_lower == "vulns":
        hard_vulns = ['anonymous ftp login allowed', 'git-exposed', 'wp-config', 'env-file', 'id_rsa', 'security misconfiguration', 'remote code execution', 'sql injection']
        if any(v in value_lower for v in hard_vulns):
            return "Hard"
        medium_vulns = ['outdated', 'no-x-frame', 'xss', 'cross-site scripting']
        if any(v in value_lower for v in medium_vulns):
            return "Medium"
        easy_vulns = ['directory indexing']
        if any(v in value_lower for v in easy_vulns):
            return "Easy"
        return "Info"
    
    if category_lower == "api_specs_and_frameworks":
        if 'graphql' in value_lower: return "Hard"
        if 'swagger' in value_lower: return "Medium"
        return "Easy"

    if category_lower == "ci_cd_and_repos":
        return "Hard"

    if category_lower == "authentication":
        return "Medium"

    if category_lower == "cloud_and_metadata":
        return "Hard"

    if category_lower == "frameworks":
        return "Medium"

    if category_lower == "endpoints":
        hard_endpoints = ['.git', 'wp-config.php', '.env', 'id_rsa', '/.aws', '/.ssh', 'phpmyadmin', '_ignition/execute-solution']
        if any(ep in value_lower for ep in hard_endpoints):
            return "Hard"
        medium_endpoints = ['admin', 'login', 'dashboard', 'backup', 'dump', 'config', 'setup', 'install', 'phpinfo.php']
        if any(ep in value_lower for ep in medium_endpoints):
            return "Medium"
        easy_endpoints = ['uploads', 'includes', 'assets']
        if any(ep in value_lower for ep in easy_endpoints):
            return "Easy"
        return "Info"

    if category_lower == "extensions":
        hard_extensions = ['.sql', '.bak', '.zip', '.tar.gz', '.tgz', 'rar', '.key', '.pem', '.p12', '.pfx', '.env']
        if any(ext in value_lower for ext in hard_extensions):
            return "Hard"
        medium_extensions = ['.log', '.cfg', '.conf', '.ini', '.yml', '.yaml', '.json', 'xml']
        if any(ext in value_lower for ext in medium_extensions):
            return "Medium"
        easy_extensions = ['.php', '.py', 'js', '.sh', '.pl', '.cgi']
        if any(ext in value_lower for ext in easy_extensions):
            return "Easy"
        return "Info"

    if category_lower == "ports":
        hard_ports = ['3306/tcp', '5432/tcp', '1433/tcp', '1521/tcp', '27017/tcp', '27018/tcp', '3389/tcp', '5985/tcp', '5986/tcp', '5900/tcp']
        if value_lower in hard_ports:
            return "Hard"
        medium_ports = ['21/tcp', '22/tcp', '23/tcp', '139/tcp', '445/tcp']
        if value_lower in medium_ports:
            return "Medium"
        easy_ports = ['25/tcp', '110/tcp', '143/tcp', '161/udp', '162/udp']
        if value_lower in easy_ports:
            return "Easy"
        return "Info"

    if category_lower == "services":
        hard_services = ['mysql', 'postgresql', 'ms-sql-s', 'oracle', 'mongodb', 'ms-wbt-server', 'winrm', 'vnc']
        if any(s in value_lower for s in hard_services):
            return "Hard"
        medium_services = ['ftp', 'ssh', 'telnet', 'microsoft-ds', 'smb']
        if any(s in value_lower for s in medium_services):
            return "Medium"
        easy_services = ['smtp', 'pop3', 'imap', 'snmp']
        if any(s in value_lower for s in easy_services):
            return "Easy"
        return "Info"

    return "Info"

