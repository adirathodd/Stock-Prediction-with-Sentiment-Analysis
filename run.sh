cd backend
cd app
uvicorn main:app --host 0.0.0.0 --port 8000

open -a Terminal .

cd frontend
npx serve -s build