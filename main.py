from sanic import Sanic
from backend.app.routes import setup_routes
from sanic import Sanic   
from sanic_cors import CORS            
              
app = Sanic("SurveyProcessor")          
CORS(app)  # This will allow all cross-origin requests by default              
    
    
# Load Routes  
setup_routes(app) 
 
if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=8000, debug=True) 
