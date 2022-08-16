from datetime import datetime


import numpy as np
import torch

from numpy.linalg import svd
from scipy.linalg import qr
from sklearn.utils.extmath import randomized_svd


import rayleaf
from rayleaf.entities import Server, Client


def dp_nla(
    rank: int,
    stdev: float,
    C: float,
    num_rounds: int = 100,
    eval_every: int = 10,
    num_clients: int = 200,
    clients_per_round: int = 40,
    client_lr: float = 0.05,
    batch_size: int = 64,
    seed: int = 0,
    num_epochs: int = 10,
    gpus_per_client_cluster: float = 1,
    num_client_clusters: int = 8,
    save_model: bool = False,
    notes: str = None
):
    curr_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    def make_comp_server_client():
        class CompClient(Client):
            def train(self):
                grads = self.train_model(compute_grads=True)

                res = []
                for layer in grads:
                    layer /= max(1, torch.linalg.norm(layer) / C)
                    if rank > 0 and layer.shape == (2048, 3136):
                        layer = layer.detach().numpy()
                        U, S, Vt = randomized_svd(layer, n_components=rank, n_iter="auto", random_state=None)

                        S = np.diag(S)
                        S += C * np.random.normal(loc=0, scale=stdev)

                        U_g, S_g, Vt_g = np.linalg.svd(S)

                        res.append((U @ U_g, S_g, Vt_g @ Vt))
                    else:
                        layer += stdev * C * torch.randn(layer.shape)
                        res.append(layer)

                return res
        

        class CompServer(Server):
            def update_layer(self, current_params, updates: list, client_num_samples: list, num_clients: int):
                average_grads = 0

                if type(updates[0]) == tuple:
                    for i in range(num_clients):
                        update = updates[i]

                        U, S, Vt = update
                        decompressed = torch.Tensor(np.dot(U * S, Vt))

                        average_grads += decompressed * client_num_samples[i]
                else:
                    for i in range(num_clients):
                        average_grads += updates[i] * client_num_samples[i]
                
                average_grads /= self.num_train_samples

                return current_params + average_grads
        

        return CompServer, CompClient

    
    CompServer, CompClient = make_comp_server_client()


    rayleaf.run_experiment(
        dataset = "femnist",
        dataset_dir = "../data/femnist/",
        output_dir= f"output/dp_nla/r{rank}_femnist-{curr_time}/",
        model = "cnn",
        num_rounds = num_rounds,
        eval_every = eval_every,
        ServerType=CompServer,
        client_types=[(CompClient, num_clients)],
        clients_per_round = clients_per_round,
        client_lr = client_lr,
        batch_size = batch_size,
        seed = seed,
        use_val_set = False,
        num_epochs = num_epochs,
        gpus_per_client_cluster = gpus_per_client_cluster,
        num_client_clusters = num_client_clusters,
        save_model = save_model,
        notes = notes
    )
