import urllib.request, json
url = 'https://api.vercel.com/v6/deployments?projectId=prj_iVQdx0xYqw5vVg3GnNdnffD54ZW6&limit=3'
req = urllib.request.Request(url, headers={'Authorization': 'Bearer vcp_4pkIx7avnoZLDzNrBR5Sht6FCoeLEg8fTX6d4iCP3Wq8hiwiqf4MLSrZ'})
try:
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    for d in data.get('deployments', []):
        print(f"ID: {d['uid']} - State: {d['state']} - URL: {d['url']} - Message: {d.get('meta', {}).get('gitCommitMessage', 'None')} - Source: {d['source']}")
except Exception as e:
    print('Error:', e)
