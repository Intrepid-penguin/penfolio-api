from ninja import Router


router = Router()

@router.get("/")
def Home(request):
  """Home endpoint to check if the API is running."""
  return {"message": "Welcome to the Journals API!"}
    