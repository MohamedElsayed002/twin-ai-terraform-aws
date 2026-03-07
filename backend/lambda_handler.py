from mangum import Mangum 
from server import app 

# Create the lambda handler
handler = Mangum(app)