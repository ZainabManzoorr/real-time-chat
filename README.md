step 1: activate venv 
python -m venv venv
source venv/bin/activate (this is for linux there is different command for windows)


step 2: install dependencies
pip install -r requirments.txt

step3: run main.py(server):
python -m uvicorn main:app --reload


step4: run the frontend
streamlit run frontend.py


test from frontend :

1) signup new user 1 
2) signup new user 2 
3) login user 1 
4) login user 2
5) create chat room
5) connect both users
6) chat now 
7) you can see chat below reciving from both users 

