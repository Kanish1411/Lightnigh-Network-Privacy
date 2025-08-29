import networkx as nx

def edge_cost(u, v, data, trx_amt):
    try:
        cost = (trx_amt * ((int(data.get("fee_rate_milli_msat", 0)) / 1e6) + (int(data.get("time_lock_delta", 0)) * int(data.get("rf", 1e-9))))) +  int(data.get("fee_base_msat", 0)) + int(data.get("bias", 1))
        return cost
    except(Exception) as e:
        print(e)
    

def calculate_total_fee(path, trx_amt, G):
    """
    Computes the total fee for the transaction by working backwards from the destination.
    """
    total_fee = 0
    amt_needed = int(trx_amt)

    for i in range(len(path) - 1, 0, -1):
        v, u = path[i], path[i - 1] 

        edge_data = G[u][v]
        base_fee = int(edge_data.get("fee_base_msat", 0))
        prop_fee = int(amt_needed * (
            (int(edge_data.get("fee_rate_milli_msat", 0)) / 1e6) +
            (int(edge_data.get("time_lock_delta", 0)) * int(edge_data.get("rf", 1e-9)))
        ))

        hop_fee = int(base_fee + prop_fee + edge_data.get("bias", 0))
        total_fee += hop_fee
        amt_needed += hop_fee  

    return total_fee


def calculate_fee_at_node(path, trx_amt, G, node):
    total_fee = 0
    amt_needed = int(trx_amt)

    for i in range(len(path) - 1, 0, -1):
        v, u = path[i], path[i - 1] 
        edge_data = G[u][v]

        base_fee = int(edge_data.get("fee_base_msat", 0))
        prop_fee = int(amt_needed * (
            (int(edge_data.get("fee_rate_milli_msat", 0)) / 1e6) +
            (int(edge_data.get("time_lock_delta", 0)) * int(edge_data.get("rf", 1e-9)))
        ))
        hop_fee = int(base_fee + prop_fee + edge_data.get("bias", 0))

        total_fee += hop_fee
        amt_needed += hop_fee  

        if u == node:
            return amt_needed
    return None
