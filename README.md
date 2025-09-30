Vercel-ready result lookup app (fixed)

Files included:
- public/index.html  -> frontend (card layout)
- api/result.py      -> defensive serverless handler exposing handler(request)
- data/*.json        -> cleaned JSON files (if included)
- vercel.json        -> minimal routes
- requirements.txt   -> (empty)

Deploy:
1. Inspect data/ to ensure it contains your JSON files (CS.json, AI&DS-E.json, ...).
2. Commit and push to GitHub, import repository to Vercel.
3. If Vercel errors about runtimes, remove any 'functions' runtime entries from vercel.json and let Vercel auto-detect.
