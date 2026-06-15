import asyncio
import time
from fastapi import APIRouter
from app.schemas.schemas import CalculationRequest, CalculationResponse, IndividualResult

router = APIRouter(prefix="/calculate", tags=["calculations"])

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

@router.post("/", response_model=CalculationResponse, summary="Асинхронные вычисления")
async def calculate(request: CalculationRequest):
    start_total = time.perf_counter()
    tasks = [calculate_square(num, delay) for num, delay in zip(request.numbers, request.delays)]
    results = await asyncio.gather(*tasks)
    end_total = time.perf_counter()
    total_time = round(end_total - start_total, 2)
    sequential_time = sum(request.delays)
    return CalculationResponse(
        results=results,
        total_time=total_time,
        parallel_faster_than_sequential=(total_time < sequential_time)
    )
