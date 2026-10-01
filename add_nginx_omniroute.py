import os

conf_path = '/etc/nginx/conf.d/anypass.conf'
with open(conf_path, 'r') as f:
    content = f.read()

omni_block = """
    # OmniRoute Cloud AI Gateway API (OpenAI Compatible)
    location /omniroute/ {
        proxy_pass http://127.0.0.1:20128/;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location = /omniroute {
        return 301 /omniroute/;
    }
"""

if 'location /omniroute/' not in content:
    target = 'location = /hermes {\n        return 301 /hermes/;\n    }'
    if target in content:
        content = content.replace(target, target + '\n' + omni_block)
        with open(conf_path, 'w') as f:
            f.write(content)
        print("SUCCESS: Added /omniroute/ location block.")
    else:
        print("ERROR: Target block not found in nginx config.")
else:
    print("INFO: /omniroute/ block already present.")
