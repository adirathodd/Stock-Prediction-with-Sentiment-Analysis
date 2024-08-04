cd backend
cd app
uvicorn main:app --host 0.0.0.0 --port 8000

cd ..

cd frontend
npx serve -s build