import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://amega-ai-repo-views-default-rtdb.firebaseio.com/"
})

ref = db.reference("repo_views")
current = ref.get() or 0
ref.set(current + 1)

print(f"Updated repo views to: {current + 1}")
