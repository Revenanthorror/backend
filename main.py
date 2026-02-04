import asyncio
import time
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class CalculationRequest(BaseModel):
    numbers: List[int]
    delays: List[float]

class IndividualResult(BaseModel):
    number: int
    square: int
    delay: float
    time: float

class CalculationResponse(BaseModel):
    results: List[IndividualResult]
    total_time: float
    parallel_faster_than_sequential: bool


async def calculate_square(number: int, delay: float) -> IndividualResult:
    start_time = time.perf_counter()
    await asyncio.sleep(delay)
    square = number ** 2
    end_time = time.perf_counter()
    
    return IndividualResult(
        number=number,
        square=square,
        delay=delay,
        time=round(end_time - start_time, 2)
    )


@app.post("/calculate/", response_model=CalculationResponse)
async def calculate(request: CalculationRequest):
    start_total = time.perf_counter()
    
    tasks = []
    for num, delay in zip(request.numbers, request.delays):
        tasks.append(calculate_square(num, delay))
    
    results = await asyncio.gather(*tasks)
    
    end_total = time.perf_counter()
    total_time = round(end_total - start_total, 2)
    
    sequential_time = sum(request.delays)
    
    parallel_faster = total_time < sequential_time

    return CalculationResponse(
        results=results,
        total_time=total_time,
        parallel_faster_than_sequential=parallel_faster
    )