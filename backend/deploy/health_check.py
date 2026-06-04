import xmlrpc.client
import traceback

if __name__ == "__main__":
    try:
        with xmlrpc.client.ServerProxy("http://localhost:9005/RPC2") as server:
            info = server.supervisor.getAllProcessInfo()
            error_states = list(filter(lambda x: x["state"] != 20, info))
            exit(len(error_states))
    except Exception:
        traceback.print_exc()
        exit(1)
