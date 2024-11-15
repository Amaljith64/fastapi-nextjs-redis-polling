from fastapi import FastAPI, HTTPException, Request, Depends
from redis import Redis
from functools import wraps
from typing import Callable


redis = Redis(host='redis', port=6379, db=0)
RATE_LIMIT_DURATION = 60
MAX_REQUESTS = 10


def rate_limit():
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request:Request,*args,**kwargs):
            client_ip = request.client.host
            key = f"rate_limit:{client_ip}"

            current = redis.get(key)
            if current is None:
                redis.setex(key,RATE_LIMIT_DURATION,1)
            else:
                current = int(current)
                if current >= MAX_REQUESTS:
                    raise HTTPException(
                        status_code=429,
                        detail="Too many requests. Please try again later"
                    )
                redis.incr(key)
            
            return await func(request,*args,**kwargs)
        return wrapper
    return decorator
