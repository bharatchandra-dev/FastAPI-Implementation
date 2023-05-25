import uvicorn

# import newrelic.agent

# newrelic.agent.initialize('newrelic.ini')

# run two instances of the app on different ports to simulate a load balancer setup with two servers behind it

if __name__ == "__main__":
    uvicorn.run("server.app:app", host="0.0.0.0", port=8080, reload=True) 
    # uvicorn.run("insurance_server.app:app", host="0.0.0.0", port=8801, reload=True)
