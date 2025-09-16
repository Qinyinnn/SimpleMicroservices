from __future__ import annotations

import os
import socket
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Path

from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.health import Health
from models.age import Age
from models.job import Job

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# In-memory stores
# -----------------------------------------------------------------------------
persons: Dict[UUID, PersonRead] = {}
addresses: Dict[UUID, AddressRead] = {}
ages: Dict[str, Age] = {}          # key: person_name
jobs: Dict[str, Job] = {}          # key: str(UUID)

app = FastAPI(
    title="Person/Address/Age/Job API",
    description="Demo FastAPI app using Pydantic v2 models",
    version="0.2.0",
)

# -----------------------------------------------------------------------------
# Health
# -----------------------------------------------------------------------------
def make_health(echo: Optional[str], path_echo: Optional[str] = None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo,
    )

@app.get("/health", response_model=Health, tags=["health"])
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health, tags=["health"])
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

# -----------------------------------------------------------------------------
# Addresses
# -----------------------------------------------------------------------------
@app.post("/addresses", response_model=AddressRead, status_code=201, tags=["addresses"])
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead], tags=["addresses"])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())
    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]
    return results

@app.get("/addresses/{address_id}", response_model=AddressRead, tags=["addresses"])
def get_address(address_id: UUID):
    item = addresses.get(address_id)
    if not item:
        raise HTTPException(status_code=404, detail="Address not found")
    return item

@app.patch("/addresses/{address_id}", response_model=AddressRead, tags=["addresses"])
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

# -----------------------------------------------------------------------------
# Persons
# -----------------------------------------------------------------------------
@app.post("/persons", response_model=PersonRead, status_code=201, tags=["persons"])
def create_person(person: PersonCreate):
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead], tags=["persons"])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="City in any embedded address"),
    country: Optional[str] = Query(None, description="Country in any embedded address"),
):
    results = list(persons.values())
    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]
    return results

@app.get("/persons/{person_id}", response_model=PersonRead, tags=["persons"])
def get_person(person_id: UUID):
    item = persons.get(person_id)
    if not item:
        raise HTTPException(status_code=404, detail="Person not found")
    return item

@app.patch("/persons/{person_id}", response_model=PersonRead, tags=["persons"])
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]

# -----------------------------------------------------------------------------
# Ages (full-ish CRUD)
# -----------------------------------------------------------------------------
@app.post("/ages", response_model=Age, status_code=201, tags=["ages"])
def create_age(payload: Age):
    ages[payload.person_name] = payload
    return payload

@app.get("/ages", response_model=List[Age], tags=["ages"])
def list_ages():
    return list(ages.values())

@app.get("/ages/{person_name}", response_model=Age, tags=["ages"])
def get_age(person_name: str):
    item = ages.get(person_name)
    if not item:
        raise HTTPException(status_code=404, detail="Age record not found")
    return item

@app.put("/ages/{person_name}", response_model=Age, tags=["ages"])
def replace_age(person_name: str, age: Age):
    # enforce path id as the key
    if person_name != age.person_name:
        raise HTTPException(status_code=400, detail="Person name in URL must match payload")
    ages[person_name] = age
    return age

@app.delete("/ages/{person_name}", status_code=204, tags=["ages"])
def delete_age(person_name: str):
    if ages.pop(person_name, None) is None:
        raise HTTPException(status_code=404, detail="Age record not found")

# -----------------------------------------------------------------------------
# Jobs (full-ish CRUD)
# -----------------------------------------------------------------------------
@app.post("/jobs", response_model=Job, status_code=201, tags=["jobs"])
def create_job(payload: Job):
    jobs[str(payload.id)] = payload
    return payload

@app.get("/jobs", response_model=List[Job], tags=["jobs"])
def list_jobs():
    return list(jobs.values())

@app.get("/jobs/{job_id}", response_model=Job, tags=["jobs"])
def get_job(job_id: str):
    item = jobs.get(job_id)
    if not item:
        raise HTTPException(status_code=404, detail="Job not found")
    return item

@app.put("/jobs/{job_id}", response_model=Job, tags=["jobs"])
def replace_job(job_id: str, job: Job):
    if str(job.id) != job_id:
        raise HTTPException(status_code=400, detail="Job ID in URL must match payload")
    jobs[job_id] = job
    return job

@app.delete("/jobs/{job_id}", status_code=204, tags=["jobs"])
def delete_job(job_id: str):
    if jobs.pop(job_id, None) is None:
        raise HTTPException(status_code=404, detail="Job not found")

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/", tags=["root"])
def root():
    return {"message": "Welcome to the Person/Address/Age/Job API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
