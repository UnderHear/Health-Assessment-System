import sys
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the project root to sys.path to allow importing src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.models import Gender, PhysicalTestInput
from src.core.core_service import IntegratedFitnessRAGService
from src.config.config import settings

app = FastAPI(title="体质测试健康分析系统 API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the service
try:
    service = IntegratedFitnessRAGService(config=settings)
except Exception as e:
    print(f"Error initializing service: {e}")
    service = None

class PhysicalTestRequest(BaseModel):
    age: int
    gender: str
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    body_fat_rate: Optional[float] = None
    vital_capacity: Optional[int] = None
    max_oxygen_uptake: Optional[float] = None
    sit_and_reach: Optional[float] = None
    single_leg_stand: Optional[float] = None
    reaction_time: Optional[float] = None
    grip_strength: Optional[float] = None
    sit_ups_per_minute: Optional[int] = None
    push_ups: Optional[int] = None
    vertical_jump: Optional[float] = None
    high_knees_2min: Optional[int] = None
    sit_to_stand_30s: Optional[int] = None
    name: Optional[str] = "未知用户"
    diseases: Optional[List[str]] = []
    exercise_preferences: Optional[List[str]] = []
    exercise_risk_level: Optional[str] = None
    uses_equipment: Optional[bool] = None

@app.post("/analyze")
async def analyze_physical_test(data: PhysicalTestRequest):
    if service is None:
        raise HTTPException(status_code=500, detail="Service not initialized")

    try:
        # Convert string gender to Enum
        gender_enum = Gender.MALE if data.gender == "男" else Gender.FEMALE
        
        # Create PhysicalTestInput object
        user_data = PhysicalTestInput(
            age=data.age,
            gender=gender_enum,
            height=data.height,
            weight=data.weight,
            bmi=data.bmi,
            body_fat_rate=data.body_fat_rate,
            vital_capacity=data.vital_capacity,
            max_oxygen_uptake=data.max_oxygen_uptake,
            sit_and_reach=data.sit_and_reach,
            single_leg_stand=data.single_leg_stand,
            reaction_time=data.reaction_time,
            grip_strength=data.grip_strength,
            sit_ups_per_minute=data.sit_ups_per_minute,
            push_ups=data.push_ups,
            vertical_jump=data.vertical_jump,
            high_knees_2min=data.high_knees_2min,
            sit_to_stand_30s=data.sit_to_stand_30s,
            name=data.name,
            diseases=data.diseases,
            exercise_preferences=data.exercise_preferences,
            exercise_risk_level=data.exercise_risk_level,
            uses_equipment=data.uses_equipment
        )

        # Call the service
        result = service.analyze_physical_test(user_data)

        # Consume the generator to get the full report text
        full_report = ""
        if result.basic_analysis:
            for chunk in result.basic_analysis:
                full_report += chunk

        return {
            "code": 200,
            "message": "success",
            "data": {
                "overall_score": result.overall_score,
                "overall_rating": result.overall_rating,
                "report": full_report,
                "individual_scores": result.individual_scores,
                "individual_ratings": result.individual_ratings
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
