class offloadingPolicy:
    name = None
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return self.name

LOCAL_ONLY = offloadingPolicy("Local Only")
RANDOM_PEER_ONLY = offloadingPolicy("Offload Random Peer")
SPECIFIC_PEER_ONLY = offloadingPolicy("Offload Specific Peer")
ANYTHING = offloadingPolicy("Offloading Anywhere")

OPTIONS = [LOCAL_ONLY, RANDOM_PEER_ONLY, SPECIFIC_PEER_ONLY, ANYTHING]