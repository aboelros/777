import urllib.request, json
url = 'https://api.vercel.com/v9/projects'
req = urllib.request.Request(url, headers={'Authorization': 'Bearer vcp_4pkIx7avnoZLDzNrBR5Sht6FCoeLEg8fTX6d4iCP3Wq8hiwiqf4MLSrZ'})
try:
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    for p in data.get('projects', []):
        print(f"Project: {p['name']} - ID: {p['id']}")
        for target in p.get('targets', {}).values():
            print(f"  Target URL: {target.get('url')}")
except Exception as e:
    print('Error:', e)
