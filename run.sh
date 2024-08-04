cd -

cd frontend

npm run build

cd -

cd backend

cd app

uvicorn main:app --host 0.0.0.0 --port 8000