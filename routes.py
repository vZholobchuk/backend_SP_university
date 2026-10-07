from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId
from typing import List
from database import tasks_collection, schedule_collection, users_collection
from models import TaskCreate, TaskUpdate, TaskResponse, ScheduleCreate, ScheduleResponse, UserCreate, UserResponse, UserInDB
from auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from services.university_api import fetch_pnu_schedule
import jwt
from jwt.exceptions import InvalidTokenError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def serialize_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_db = UserInDB(**user.model_dump(), hashed_password=hashed_password)
    
    result = await users_collection.insert_one(user_db.model_dump())
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_user)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer", "userId": str(user["_id"])}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
        
    user = await users_collection.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return serialize_doc(user)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    task_dict = task.model_dump(exclude_unset=True)
    task_dict["user_id"] = current_user["_id"]
    result = await tasks_collection.insert_one(task_dict)
    created_task = await tasks_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_task)

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(current_user: dict = Depends(get_current_user)):
    tasks = await tasks_collection.find({"user_id": current_user["_id"]}).to_list(100)
    return [serialize_doc(task) for task in tasks]

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    task = await tasks_collection.find_one({"_id": ObjectId(task_id), "user_id": current_user["_id"]})
    if task:
        return serialize_doc(task)
    raise HTTPException(status_code=404, detail="Task not found")

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskUpdate, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update")

    result = await tasks_collection.update_one(
        {"_id": ObjectId(task_id), "user_id": current_user["_id"]}, {"$set": update_data}
    )
    if result.modified_count == 1 or result.matched_count == 1:
        updated_task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
        return serialize_doc(updated_task)
    raise HTTPException(status_code=404, detail="Task not found")

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    result = await tasks_collection.delete_one({"_id": ObjectId(task_id), "user_id": current_user["_id"]})
    if result.deleted_count == 1:
        return
    raise HTTPException(status_code=404, detail="Task not found")


from pydantic import BaseModel
class SyncRequest(BaseModel):
    group_name: str

@router.post("/schedule/sync", response_model=List[ScheduleResponse])
async def sync_schedule(sync_req: SyncRequest, current_user: dict = Depends(get_current_user)):
    """Отримує реальний (або моковий) розклад з ПНУ та зберігає його в базу"""
    schedule_data = await fetch_pnu_schedule(sync_req.group_name)
    

    await schedule_collection.delete_many({"user_id": current_user["_id"]})
    
    inserted_entries = []
    if schedule_data:
        for entry in schedule_data:
            entry["user_id"] = current_user["_id"]
            inserted = await schedule_collection.insert_one(entry)
            entry["_id"] = inserted.inserted_id
            inserted_entries.append(entry)
            
    return [serialize_doc(entry) for entry in inserted_entries]

@router.post("/schedule", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule_entry(entry: ScheduleCreate, current_user: dict = Depends(get_current_user)):
    entry_dict = entry.model_dump(exclude_unset=True)
    entry_dict["user_id"] = current_user["_id"]
    result = await schedule_collection.insert_one(entry_dict)
    created_entry = await schedule_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_entry)

@router.get("/schedule", response_model=List[ScheduleResponse])
async def get_schedule(current_user: dict = Depends(get_current_user)):
    entries = await schedule_collection.find({"user_id": current_user["_id"]}).sort("start_time", 1).to_list(1000)
    return [serialize_doc(entry) for entry in entries]
